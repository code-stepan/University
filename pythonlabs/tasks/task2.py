import formulas
import numpy as np # type: ignore
import matplotlib.pyplot as plt # pyright: ignore

def start(h_values = [1.0, 0.5, 0.1], T = 8.0, y0 = 80.0, t0 = 0.0):
    task2(h_values, T, y0, t0)

def task2(h_values, T, y0, t0):
    for h in h_values:
        t, y = formulas.euler_method(formulas.f, y0, t0, T, h)
        y_exact = formulas.exact_solution(t)
        errors = np.abs(y - y_exact)

        plt.figure(figsize=(10, 6))
        plt.plot(t, errors, 'g-', marker='o', markersize=3, label=f'Ошибка (h={h})')
        plt.xlabel('t')
        plt.ylabel('Абсолютная ошибка')
        plt.title(f'Зависимость ошибки от времени (h={h})')
        plt.legend()
        plt.grid(True)
        plt.savefig('graph/g2.png')

        print(f"\nh = {h}:")
        print(f"  Максимальная ошибка = {np.max(errors):.6e}")
        print(f"  Средняя ошибка       = {np.mean(errors):.6e}")