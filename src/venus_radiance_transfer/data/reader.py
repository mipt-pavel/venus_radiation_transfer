"""Загрузка табличных данных (VIRA, аэрозоли)"""

import numpy as np
import scipy.io
from ..config import VIRA_FILE, AEROSOL_MODES_FILE, AEROSOL_MODES_PARAMS_FILE, WN_START, WN_STOP

def load_vira_profile():
    """
    Загружает профиль высот, давления, температуры, концентрации из текстового файла.
    Возвращает кортеж (h_km, P_atm, T_K, n_all).
    """
    data = np.loadtxt(VIRA_FILE, comments='#')
    P_atm = data[:, 0]
    h_km = data[:, 1]
    n_all = data[:, 2]
    T_K = data[:, 3]
    return h_km, P_atm, T_K, n_all

def load_aerosol_modes():
    """
    Загружает параметры 4 мод частиц H2SO4.
    Возвращает список словарей.
    """
    modes = []
    modes_params = np.loadtxt(AEROSOL_MODES_PARAMS_FILE, comments='#')
    for i in range(1, 5):
        mode_name = f'aerosol_mode{i}'
        mat = scipy.io.loadmat(f'{AEROSOL_MODES_FILE}{i}.mat')
        nu = mat['WN'].flatten()[int(WN_START/2):int(WN_STOP/2)+1]
        q_ext = mat['Q_EXT'].flatten()[int(WN_START/2):int(WN_STOP/2)+1]
        params = modes_params[i-1, :]

        modes.append({
            'name': mode_name,
            'nu_grid': nu,
            'q_ext': q_ext,
            'z_b': params[0],
            'z_c': params[1],
            'H_up': params[2],
            'H_lo': params[3],
            'N_0': params[4],
            'density': None
        })
    
    print(f'Моды аэрозоля загружены, число мод = {len(modes)}')
    return modes