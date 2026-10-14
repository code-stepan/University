import numpy as np # pyright: ignore
import matplotlib.pyplot as plt # pyright: ignore

import formulas

def start(h_values = [1.0, 0.5, 0.1], T = 8.0, y0 = 80.0, t0 = 0.0, exact_T = None):
    task1(h_values, T, y0, t0, exact_T)

def task1(h_values, T, y0, t0, exact_T):
    if (exact_T == None):
        exact_T = formulas.exact_solution(T)
    
    for h in h_values:
        t, y = formulas.euler_method(formulas.f, y0, t0, T, h)
        N = len(t) - 1
        y_end = y[-1]
        error = abs(y_end - exact_T)
        
        print(f"\nШаг h = {h}")
        print(f"  Количество шагов N = {N}")
        print(f"  y({T}) численное = {y_end:.6f}")
        print(f"  y({T}) точное    = {exact_T:.6f}")
        print(f"  Абсолютная ошибка = {error:.6e}")
        
        print("\n  Первые 5 значений (t, y):")
        for i in range(min(5, len(t))):
            print(f"    t = {t[i]:.3f}, y = {y[i]:.6f}")

        print("  Последние 5 значений (t, y):")
        for i in range(max(0, len(t)-5), len(t)):
            print(f"    t = {t[i]:.3f}, y = {y[i]:.6f}")

        plt.figure(figsize=(10, 6))
        t_fine = np.linspace(t0, T, 200)
        y_exact = formulas.exact_solution(t_fine)
        plt.plot(t_fine, y_exact, 'b-', label='Точное решение')
        plt.plot(t, y, 'ro-', markersize=4, label=f'Численное решение (h={h})')
        plt.xlabel('t')
        plt.ylabel('y')
        plt.title(f'Сравнение точного и численного решений (h={h})')
        plt.legend()
        plt.grid(True)
        plt.savefig('graph/g1.png')