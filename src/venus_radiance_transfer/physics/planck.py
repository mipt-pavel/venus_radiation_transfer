"""Функция Планка и яркостная температура."""

import numpy as np

# Константы в СГС
H = 6.62607015e-27      # эрг·с
C = 2.99792458e10       # см/с
K = 1.380649e-16      # эрг/К
C2 = H * C / K     # = 1.4388 см·К

def planck_intensity(wavenumber, T):
    """
    Интенсивность излучения чёрного тела (спектральная яркость).
    wavenumber : array, см⁻¹
    T : float, K
    возвращает array, единицы: эрг·с⁻¹·см⁻²·ср⁻¹·(см⁻¹)⁻¹
    """
    exp_x = np.exp((H * C * wavenumber) / (K * T))
    B = 2 * H * C**2 * wavenumber**3 / (exp_x - 1)
    B = np.nan_to_num(B, nan=0.0)
    return B

def brightness_temperature(wavenumber, intensity):
    """Обратная функция Планка – яркостная температура."""
    a = 2 * H * C**2 * wavenumber**3
    T = C2 * wavenumber / np.log(1 + a / intensity)
    T = np.nan_to_num(T, nan=0.0, posinf=0.0)
    return T