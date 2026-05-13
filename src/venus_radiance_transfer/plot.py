"""Визуализация результатов (загружает .txt и строит графики)"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
from .config import DATA_PROCESSED_DIR, DATA_PLOTS_DIR, OUTPUT_FILENAME, PLOT_NAME, CONVOLVE_RESOLUTION
from .physics.planck import brightness_temperature

def plot_spectrum():
    # Загружаем
    data = np.loadtxt(DATA_PROCESSED_DIR / f'{OUTPUT_FILENAME}.txt')
    nu = data[:, 0]
    I = data[:, 1]

    # Свертка спектра
    step = nu[1] - nu[0]
    sigma = CONVOLVE_RESOLUTION # стандартное отклонение
    half_width = int(np.ceil(5 * sigma / step)) # ширина ядра
    x = np.arange(-half_width, half_width + 1) * step
    kernel = np.exp(-x**2 / (2 * sigma**2))
    kernel /= kernel.sum()   # нормировка

    I_convolved = fftconvolve(I, kernel, mode='same')
    Tb_conv = brightness_temperature(nu, I_convolved)

    # График
    plt.figure(figsize=(12,5))
    plt.plot(nu, Tb_conv)
    plt.xlabel(r'Волновое число, $см^{-1}$')
    plt.ylabel(r'Яркостная температура, $T$, K')
    plt.title(rf'Уходящее тепловое излучение Венеры (convolved with $\sigma =$ {CONVOLVE_RESOLUTION} $см^{-1}$)')
    plt.grid()
    plt.savefig(DATA_PLOTS_DIR / f'{PLOT_NAME}.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    plot_spectrum()