"""Конфигурация модели"""

from pathlib import Path

# Корень проекта
ROOT_DIR = Path(__file__).parent.parent.parent

# Параметры спектральной сетки
WN_START = 0.0          # см^-1
WN_STOP = 2000.0
WN_STEP = 0.0005

# Пути к данным
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATA_PLOTS_DIR = ROOT_DIR / "data" / "plots"
HITRAN_CACHE_DIR = DATA_PROCESSED_DIR / "hitran" / f"{WN_START}_{WN_STOP}"   # для fetch-данных HAPI
HITRAN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = ROOT_DIR / "data" / "temp"

# Параметр "обрезания" атмосферы (начиная с какого слоя имеет смысл считать перенос излучения)
# (e.g. tau_above > 20)
CUT_HEIGHT = 47
CUT_WN_LEFT = 100 # cm-1

# Параметры расчета коэффициентов поглощения газов
WnWing_WH = 750

# Разрешение для свёртки
CONVOLVE_RESOLUTION = 0.5   # cm-1

# Профиль атмосферы (файл)
VIRA_FILE = DATA_RAW_DIR / "VIRAPROFILE.txt"

# Аэрозольные моды (4 моды H2SO4)
AEROSOL_MODES_FILE = DATA_RAW_DIR / "H2SO4_BIER00_75_2000_Haus16_"
AEROSOL_MODES_PARAMS_FILE = DATA_RAW_DIR / "H2SO4_modes_params.txt"

# Параллельные вычисления
N_WORKERS = 2   # количество процессов

# Список газов для line-by-line расчета
GASES = [{'name': 'CO2', 'M': 2, 'I': [7, 8, 9, 10, 11, 12, 13, 14, 121, 15, 120, 122], 'VMR': None, 'Diluent': None}, 
         {'name': 'O3', 'M': 3, 'I': [16, 17, 18, 19, 20], 'VMR': None, 'Diluent': None}]

# Параметры профиля озона
O3_PROFILE_CONFIG = {
    'model': 'gaussian',
    'peak_altitude_km': 65.0,
    'peak_vmr': 10e-9,    # 10 ppbv
    'sigma_km': 5.0,
}

# Параметры вывода
OUTPUT_FILENAME = 'spectrum_intensity_aer_co2_100_2000_wing750'
PLOT_NAME = 'spectrum_Tb_aer_co2_200_1800_wing750'