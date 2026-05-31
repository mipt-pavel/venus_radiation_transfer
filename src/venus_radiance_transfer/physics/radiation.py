"""Интегрирование переноса излучения (без рассеяния)"""

import numpy as np
from hapi import db_begin, fetch_by_ids
from ..config import HITRAN_CACHE_DIR, WN_START, WN_STOP, WN_STEP, CUT_HEIGHT, CUT_WN_LEFT
from .planck import planck_intensity
from .absorption import compute_k_abs_gas_parallel, compute_k_abs_aerosol_parallel
from ..data.profiles import interpolate_aerosol_ext
from ..data.cache import load_k_abs_layer, _get_filename

def integrate_radiation(h_km, P_atm, T_K, n_all, gases, aerosol_modes):
    """
    Расчет излучения на верхней границе: последовательные вычисления от верхнего слоя к
    поверхности (генерируемое слоем излучение + ослабление верхними слоями)
    """
    n_layers = len(h_km)    # число слоев
    dz_cm = np.diff(h_km, append=101) * 1e5    # толщины слоёв, массив (n_layers,)

    # Создание массива температур слоев (как среднее между границами слоев)
    T_aver_temp = (T_K[:-1] + T_K[1:]) / 2
    T_aver = np.append(T_aver_temp, T_K[-1])

    # Создание сетки волновых чисел
    wn_grid = np.arange(WN_START, WN_STOP, WN_STEP)
    print(f'Расчет сетки выполнен, размер сетки: {len(wn_grid)}')

    # Проверка: выполен ли fetch данных с HITRAN и рассчитаны ли коэффициенты поглощения
    # (Предполагается, что если файл .h5 и .data существуют, то коэффициенты 
    # полностью рассчитаны, а данные загружены для данных WN_START и WN_STOP)
    if gases is not None:
        for gas in gases:
            data_filename = HITRAN_CACHE_DIR / f"{gas['name']}.data"
            if not data_filename.exists():
                db_begin(str(HITRAN_CACHE_DIR))
                fetch_by_ids(gas['name'], gas['I'], WN_START, WN_STOP)
            filename = _get_filename(gas['name'])
            if not filename.exists():
                print(f'Произвожу расчет коэффициентов поглощения газа {gas["name"]}')
                compute_k_abs_gas_parallel(gas, n_layers, P_atm, T_K, n_all, wn_grid)
            else:
                print(f'Загружаю данные газа {gas["name"]}')

    # Проверка: рассчитаны ли коэффициенты поглощения аэрозоля
    # (Предполагается, что если файл .h5 сущетсвует, то коэффициенты полностью
    #  рассчтаны)
    if aerosol_modes is not None:
        aerosol_filename = _get_filename('aerosol')
        if not aerosol_filename.exists():
            print(f'Произвожу расчет коэффициентов поглощения аэрозоля')
            interpolate_aerosol_ext(aerosol_modes, wn_grid)
            compute_k_abs_aerosol_parallel(aerosol_modes, n_layers, wn_grid)
        else:
            print('Загружаю данные аэрозоля')

    # Инициализация накопителей
    idx_start = int(CUT_WN_LEFT / WN_STEP)

    tau_above = np.zeros_like(wn_grid[idx_start:])
    I_up = np.zeros_like(wn_grid[idx_start:])
    
    # Цикл по слоям сверху вниз (чтобы накапливать tau_above)
    for i in range(n_layers-CUT_HEIGHT-1, 0, -1):
        k_total = np.zeros_like(wn_grid[idx_start:])

        # 1. Газовые компоненты
        if gases is not None:
            for gas in gases:
                k_gas = load_k_abs_layer(gas['name'], i)[idx_start:]
                k_gas += load_k_abs_layer(gas['name'], i-1)[idx_start:]
                k_gas *= 0.5
                k_total += k_gas

        # 2. Аэрозольная компоненты
        if aerosol_modes is not None:
            k_aer = load_k_abs_layer('aerosol', i)[idx_start:]
            k_aer += load_k_abs_layer('aerosol', i-1)[idx_start:]
            k_aer *= 0.5
            k_total += k_aer

        tau_i = k_total * dz_cm[i]
        
        # Яркостная температура слоя
        B = planck_intensity(wn_grid[idx_start:], T_aver[i+CUT_HEIGHT])
        
        # Вклад собственного излучения слоя (ослабляется вышележащими слоями)
        I_up += B * (1.0 - np.exp(-tau_i)) * np.exp(-tau_above)
        
        # Обновляем оптическую толщину вышележащих слоёв (добавляем текущий слой)
        tau_above += tau_i
        print(f'В слое {i+CUT_HEIGHT} накопленная оптическая толщина: tau_min = {np.min(tau_above)}; tau_max = {np.max(tau_above)}')
    
    # Добавляем излучение нижней границы (поверхность), ослабленное всей атмосферой
    I0 = planck_intensity(wn_grid[idx_start:], T_K[0])
    I_up += I0 * np.exp(-tau_above)

    print('Спектр интенсивности излучения рассчитан')
    
    return wn_grid[idx_start:], I_up