"""Работа с файлами со всеми значениями коэффициентов поглощения компонент по слоям"""

import h5py
import numpy as np
from ..config import DATA_PROCESSED_DIR, WN_START, WN_STOP

K_ABS_DIR = DATA_PROCESSED_DIR / "k_abs" / f"{WN_START}_{WN_STOP}"
K_ABS_DIR.mkdir(parents=True, exist_ok=True)

def _get_filename(component_name):
    """Возвращает путь к HDF5 файлу для компоненты."""
    return K_ABS_DIR / f"k_abs_{component_name}.h5"

def init_k_abs_cache(component_name, n_layers, n_wn):
    """
    Создаёт HDF5 файл для компоненты с заданной размерностью.
    Вызывается один раз перед расчётом, когда известны n_layers и n_nu.
    """
    filename = _get_filename(component_name)
    if filename.exists():
        return   # уже инициализирован
    with h5py.File(filename, 'w') as f:
        # Создаём dataset с чанками по одному слою (оптимально для построчного доступа)
        f.create_dataset('k_abs', shape=(n_layers, n_wn), dtype=np.float64, chunks=(1, n_wn))

def save_k_abs_layer(component_name, layer_idx, k_abs_layer):
    """Сохраняет массив k_abs для одного слоя в соответствующий файл."""
    filename = _get_filename(component_name)
    if not filename.exists():
        raise FileNotFoundError(f"Cache for {component_name} not initialized. Call init_k_abs_cache first.")
    with h5py.File(filename, 'r+') as f:
        f['k_abs'][layer_idx, :] = k_abs_layer

def load_k_abs_layer(component_name, layer_idx):
    """Загружает массив k_abs для одного слоя из файла кэша."""
    filename = _get_filename(component_name)
    with h5py.File(filename, 'r') as f:
        return f['k_abs'][layer_idx, :]   # читает только одну строку (без загрузки всего массива)