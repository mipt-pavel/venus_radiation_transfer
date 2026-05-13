"""Генерация вертикальных профилей (озон, аэрозоли) по модельным параметрам"""

import numpy as np
from scipy.interpolate import interp1d

def generate_o3_profile(h_km, O3_profile_param):
    """
    Возвращает профиль концентрации озона (по высоте)
    """
    model, peak_alt, peak_vmr, sigma_km = O3_profile_param.values()
    vmr_o3 = np.zeros_like(h_km)

    if model == 'gaussian':
        vmr_o3 = peak_vmr * np.exp(-((h_km - peak_alt)**2) / (2 * sigma_km**2))
        vmr_o3[h_km < (peak_alt - sigma_km)] = 0.0
        vmr_o3[h_km > (peak_alt + sigma_km)] = 0.0
    
    return vmr_o3

def generate_o3_diluents(h_km, vmr):
    """
    Для каждого слоя создает параметр Diluent для озона
    """
    diluents = []

    for i in range(len(h_km)):
        if vmr[i] > 0:
            diluents.append({'self': vmr[i], 'CO2': 0.965-vmr[i], 'N2': 0.035})
        else:
            diluents.append({'CO2': 0.965, 'N2': 0.035})

    return diluents

def generate_aerosol_profiles(h_km, modes):
    """
    Возвращает профиль концентрации аэрозоля (по высоте)
    """
    for mode in modes:
        _, _, _, z_b, z_c, H_up, H_lo, N_0, _ = mode.values()

        density_aerosol = np.zeros_like(h_km)
        for z in range(len(h_km)):
            if z > (z_b + z_c):
                density_aerosol[z] = N_0 * np.exp(-((z - (z_b + z_c))/(H_up)))
            elif (z <= (z_b + z_c)) & (z >= z_b):
                density_aerosol[z] = N_0
            elif z < z_b:
                density_aerosol[z] = N_0 * np.exp(-((z_b - z)/H_lo))
        
        mode['density'] = density_aerosol

    print(f'Профили концентраций аэрозоля созданы, число мод = {len(modes)}, профиль - {len(modes[0]['density'])} км')
    return None

def interpolate_aerosol_ext(modes, nu_grid):
    """
    Интерполирует значения полного сечения мод аэрозоля на заданную сетку волновых чисел
    """
    for mode in modes:
        interp_func = interp1d(mode['nu_grid'], mode['q_ext'], kind='linear', 
                               fill_value='extrapolate', bounds_error=False)
        mode['q_ext'] = interp_func(nu_grid)
        mode['nu_grid'] = nu_grid
    
    return None