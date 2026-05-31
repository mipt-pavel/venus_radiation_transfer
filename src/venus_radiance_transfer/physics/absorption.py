"""Расчёт объёмных коэффициентов поглощения газов и аэрозолей"""

import numpy as np
from tqdm import tqdm
from hapi import db_begin, absorptionCoefficient_Voigt
from concurrent.futures import ProcessPoolExecutor, as_completed
from ..config import HITRAN_CACHE_DIR, N_WORKERS, TEMP_DIR, CUT_HEIGHT, WnWing_WH
from ..data.cache import init_k_abs_cache, save_k_abs_layer

# Глобальный флаг для отслеживания инициализации кэша для компонент
_CACHE_INITIALIZED = {}

def ensure_cache_initialized(component_name, n_layers, n_wn):
    if component_name not in _CACHE_INITIALIZED:
        init_k_abs_cache(component_name, n_layers-CUT_HEIGHT, n_wn)
        _CACHE_INITIALIZED[component_name] = True

def compute_k_abs_layer_gas(gas, layer_idx, p_atm, T_K, n_layer, wn_grid):
    """
    Расчет коэффициента поглощения данного газа в данном слое (концентрация газа
    учитывается в параметре Components)
    """
    db_begin(str(HITRAN_CACHE_DIR))

    if gas['VMR'][layer_idx] > 0:
        _, k_abs = absorptionCoefficient_Voigt(
            SourceTables=gas['name'],
            Environment={'p': p_atm, 'T': T_K},
            WavenumberGrid=wn_grid,
            Diluent=gas['Diluent'][layer_idx],
            HITRAN_units=True,
            WavenumberWingHW=WnWing_WH
        )
        k_abs *= (n_layer * gas['VMR'][layer_idx])
    else:
        k_abs = np.zeros_like(wn_grid)
    # Сохраняем во временный файл с именем, содержащим индекс слоя
    temp_file = TEMP_DIR / f"{gas['name']}_layer_{layer_idx}.npy"
    np.save(temp_file, k_abs)

    print(f'Газ {gas["name"]} в {layer_idx} слое посчитан')

    return None

def compute_k_abs_layer_aerosol(layer_idx, modes, wn_grid):
    """
    Расчет коэффициента поглощения аэрозоля (суммарно от всех мод) в данном слое 
    """
    k_abs = np.zeros_like(wn_grid)
    for j in range(len(modes)):
        k_abs += 1e-8 * modes[j]['q_ext'] * modes[j]['density'][layer_idx]

    # Сохраняем во временный файл с именем, содержащим индекс слоя
    temp_file = TEMP_DIR / f"aerosol_layer_{layer_idx}.npy"
    np.save(temp_file, k_abs)

    print(f'Аэрозоль в {layer_idx} слое посчитан')

    return None

def compute_k_abs_gas_parallel(gas, n_layers, P_atm, T_K, n_all, wn_grid):
    """
    Параллельное вычисление k_abs для всех слоёв газовой компоненты.
    Результаты временно сохраняются в .npy файлы (один на слой), затем объединяются в HDF5.
    """
    ensure_cache_initialized(gas['name'], n_layers, len(wn_grid))
    
    with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = []
        for i in range(CUT_HEIGHT, n_layers):
            temp_file = TEMP_DIR / f"{gas['name']}_layer_{i}.npy"
            if temp_file.exists():
                print(f'Загружаю газ {gas['name']} в слое {i} из временного файла')
                continue

            futures.append(executor.submit(
                compute_k_abs_layer_gas,
                gas, i, P_atm[i], T_K[i], n_all[i], wn_grid
            ))
        # Ждём завершения всех задач
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            future.result()   # если было исключение – поднимется здесь

    # После завершения всех процессов – объединяем временные файлы в HDF5
    for i in range(n_layers-CUT_HEIGHT):
        temp_file = TEMP_DIR / f"{gas['name']}_layer_{CUT_HEIGHT+i}.npy"
        k_abs = np.load(temp_file)
        save_k_abs_layer(gas['name'], i, k_abs)
        temp_file.unlink()   # удаляем временный файл

    print(f'Газ {gas["name"]} полностью рассчитан и сохранен')

    return None

def compute_k_abs_aerosol_parallel(modes, n_layers, wn_grid):
    """
    Параллельное вычисление k_abs для всех слоёв аэрозольной компоненты.
    Результаты временно сохраняются в .npy файлы (один на слой), затем объединяются в HDF5.
    """
    ensure_cache_initialized('aerosol', n_layers, len(wn_grid))
    
    with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = []
        for i in range(CUT_HEIGHT, n_layers):
            temp_file = TEMP_DIR / f"aerosol_layer_{i}.npy"
            if temp_file.exists():
                print(f'Загружаю аэрозоль в слое {i} из временного файла')
                continue

            futures.append(executor.submit(
                compute_k_abs_layer_aerosol,
                i, modes, wn_grid
            ))
        # Ждём завершения всех задач
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
            future.result()   # если было исключение – поднимется здесь

    # После завершения всех процессов – объединяем временные файлы в HDF5
    for i in range(n_layers-CUT_HEIGHT):
        temp_file = TEMP_DIR / f"aerosol_layer_{CUT_HEIGHT+i}.npy"
        k_abs = np.load(temp_file)
        save_k_abs_layer('aerosol', i, k_abs)
        temp_file.unlink()   # удаляем временный файл

    print(f'Аэрозоль полностью рассчитан и сохранен')

    return None