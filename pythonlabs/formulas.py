import numpy as np # type: ignore

def exact_solution(t):
    return 80 * np.exp(0.25 * t)

def f(t, y):
    return 0.25 * y

def euler_method(f, y0, t0, T, h):
    N = int((T - t0) / h)          # количество шагов
    t = np.linspace(t0, T, N+1)    # массив узлов (N+1 точка)
    y = np.zeros(N+1)
    y[0] = y0
    for n in range(N):
        y[n+1] = y[n] + h * f(t[n], y[n])
    return t, y