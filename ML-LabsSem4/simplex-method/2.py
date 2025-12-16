import numpy as np

simplex_table = np.array([
    [2, 1, 1, 0, 40],
    [1, 2, 0, 1, 30],
    [-10, -15, 0, 0, 0]
], dtype=float)

n_vars = 2
n_constraints = 2

while True:
    if all(simplex_table[-1, :-1] >= 0):
        break  # Оптимальное решение найдено

    pivot_col = np.argmin(simplex_table[-1, :-1])

    ratios = []
    for i in range(n_constraints):
        if simplex_table[i, pivot_col] > 0:
            ratios.append(simplex_table[i, -1] / simplex_table[i, pivot_col])
        else:
            ratios.append(float('inf'))
    pivot_row = np.argmin(ratios)

    pivot = simplex_table[pivot_row, pivot_col]

    simplex_table[pivot_row] /= pivot

    for i in range(len(simplex_table)):
        if i != pivot_row:
            factor = simplex_table[i, pivot_col]
            simplex_table[i] -= factor * simplex_table[pivot_row]

solution = np.zeros(n_vars)
for j in range(n_vars):
    col = simplex_table[:, j]
    if 1 in col and np.sum(col == 1) == 1 and np.sum(col == 0) == len(col) - 1:
        row = np.where(col == 1)[0][0]
        solution[j] = simplex_table[row, -1]

x, y = solution
z = 10 * x + 15 * y

print(f"Количество продукта A (x): {x:.2f}")
print(f"Количество продукта B (y): {y:.2f}")
print(f"Максимальная прибыль (z): {z:.2f} долларов")



