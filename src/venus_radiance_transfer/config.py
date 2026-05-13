"""Конфигурация модели"""

from pathlib import Path

# Корень проекта
ROOT_DIR = Path(__file__).parent.parent.parent

# Пути к данным
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATA_PLOTS_DIR = ROOT_DIR / "data" / "plots"
HITRAN_CACHE_DIR = DATA_PROCESSED_DIR / "hitran"   # для fetch-данных HAPI
TEMP_DIR = ROOT_DIR / "data" / "temp"

# Параметры спектральной сетки
WN_START = 1000.0          # см⁻¹
WN_STOP = 1100.0
WN_STEP = 0.0001

# Разрешение для свёртки
CONVOLVE_RESOLUTION = 0.5   # cm-1

# Профиль атмосферы (файл)
VIRA_FILE = DATA_RAW_DIR / "VIRAPROFILE.txt"

# Аэрозольные моды (4 моды H2SO4)
AEROSOL_MODES_FILE = DATA_RAW_DIR / "H2SO4_BIER00_75_2000_Haus16_"
AEROSOL_MODES_PARAMS_FILE = DATA_RAW_DIR / "H2SO4_modes_params.txt"

# Параллельные вычисления
N_WORKERS = 3   # количество процессов

# Список газов для line-by-line расчета
GASES = [{'name': 'CO2', 'M': 2, 'I': 1, 'VMR': None, 'Diluent': None}, 
         {'name': 'O3', 'M': 3, 'I': 1, 'VMR': None, 'Diluent': None}]

# Параметры профиля озона
O3_PROFILE_CONFIG = {
    'model': 'gaussian',
    'peak_altitude_km': 65.0,
    'peak_vmr': 10e-9,    # 10 ppbv
    'sigma_km': 5.0,
}

# Параметры вывода
OUTPUT_FILENAME = 'spectrum_intensity_all_comp_1000_1100'
PLOT_NAME = 'spectrum_Tb_all_comp_1000_1100'