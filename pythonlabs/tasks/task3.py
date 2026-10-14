import formulas
import matplotlib.pyplot as plt # pyright: ignore

def start(h_values = [1.0, 0.5, 0.25, 0.1, 0.05], T = 8.0, y0 = 80.0, t0 = 0.0, exact_T = None):
    task3(h_values, T, y0, t0, exact_T)

def task3(h_values, T, y0, t0, exact_T):
    if (exact_T == None):
        exact_T = formulas.exact_solution(T)
    
    N_list = []
    errors_list = []
    
    for h in h_values:
        t, y = formulas.euler_method(formulas.f, y0, t0, T, h)
        N = len(t) - 1
        error = abs(y[-1] - exact_T)
        N_list.append(N)
        errors_list.append(error)
        print(f"h = {h:.2f}: N = {N}, ошибка = {error:.6e}")

    plt.figure(figsize=(10, 6))
    plt.plot(h_values, errors_list, 'bo-', markersize=8)
    plt.xlabel('Шаг h')
    plt.ylabel('Абсолютная ошибка в конечной точке')
    plt.title('Зависимость ошибки от шага интегрирования')
    plt.grid(True)
    plt.savefig('graph/g3_error_vs_h.png')

    plt.figure(figsize=(10, 6))
    plt.loglog(h_values, errors_list, 'bo-', markersize=8)
    plt.xlabel('Шаг h (логарифмическая шкала)')
    plt.ylabel('Ошибка (логарифмическая шкала)')
    plt.title('Зависимость ошибки от шага (log-log)')
    plt.grid(True, which='both')
    plt.savefig('graph/g3_error_loglog.png')
    
    return h_values, N_list, errors_list