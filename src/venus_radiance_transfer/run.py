"""Главный скрипт: загружает конфиг, читает данные, вычисляет и сохраняет результаты"""

import numpy as np
from .config import DATA_PROCESSED_DIR, GASES, O3_PROFILE_CONFIG, OUTPUT_FILENAME
from .data.reader import load_vira_profile, load_aerosol_modes
from .data.profiles import generate_o3_profile, generate_o3_diluents, generate_aerosol_profiles
from .physics.radiation import integrate_radiation

def main():
    # Загружаем и генерируем профили
    # HITRAN и газы
    h_km, P_atm, T_K, n_all = load_vira_profile()
    vmr_o3 = generate_o3_profile(h_km, O3_PROFILE_CONFIG)
    next((gas for gas in GASES if gas['name'] == 'O3'), None)['VMR'] = vmr_o3
    next((gas for gas in GASES if gas['name'] == 'CO2'), None)['VMR'] = np.full(np.shape(h_km), 0.965)

    next((gas for gas in GASES if gas['name'] == 'O3'), None)['Diluent'] = generate_o3_diluents(h_km, vmr_o3)
    next((gas for gas in GASES if gas['name'] == 'CO2'), None)['Diluent'] = [{'self': 0.965, 'N2': 0.035}] * len(h_km)
    # Аэрозоль
    aerosol_modes = load_aerosol_modes()
    generate_aerosol_profiles(h_km, aerosol_modes)

    # Расчет переноса излучения
    nu_grid, I_up = integrate_radiation(h_km, P_atm, T_K, n_all, GASES, aerosol_modes)

    # Сохраняем результат в текстовый файл
    output_file = DATA_PROCESSED_DIR / f"{OUTPUT_FILENAME}.txt"
    np.savetxt(output_file, np.column_stack((nu_grid, I_up)), header='wavenumber_cm-1 intensity_cgs')
    print(f"Спектр сохранён в {output_file}")

if __name__ == "__main__":
    main()