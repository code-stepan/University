# import numpy as np
#
# # Коэффициенты целевой функции (стоимость продуктов)
# c = np.array([1.5, 2, 1])  # x, y, z
#
# # Матрица ограничений (коэффициенты неравенств)
# A = np.array([
#     [12, 8, 3],   # Белки
#     [9, 10, 2],   # Жиры
#     [0, 15, 10]   # Углеводы
# ])
#
# # Правые части ограничений
# b = np.array([60, 50, 200])
#
# def dual_simplex(c, A, b):
#     m, n = A.shape
#
#     # Добавляем слабые переменные (знак - так как >=)
#     tableau = np.hstack([np.eye(m), -np.eye(m), b.reshape(-1, 1)])
#
#     # Целевая функция: Z = c @ x => добавляем коэффициенты основных переменных
#     obj_row = np.hstack([c, np.zeros(m + 1)])
#     tableau = np.vstack([tableau, obj_row])
#
#     print("Начальная таблица:")
#     print(tableau)
#
#     iteration = 1
#     while True:
#         print(f"\n--- Итерация {iteration} ---")
#         print(tableau)
#         iteration += 1
#
#         # Поиск строки с отрицательным RHS (ведущая строка)
#         rhs = tableau[:, -1]
#         negative_rows = np.where(rhs < 0)[0]
#
#         if len(negative_rows) == 0:
#             break  # Оптимальное решение найдено
#
#         row = negative_rows[0]  # Берём первую отрицательную строку
#
#         # Поиск ведущего столбца (минимум отношений коэффициентов целевой функции к элементам строки)
#         ratios = []
#         for col in range(n + m):
#             pivot = tableau[row, col]
#             z_coeff = tableau[-1, col]
#             if pivot < 0 and z_coeff != 0:
#                 ratios.append(z_coeff / pivot)
#             else:
#                 ratios.append(np.inf)
#
#         col = np.argmin(ratios)
#         if ratios[col] == np.inf:
#             raise ValueError("Задача неограничена!")
#
#         # Обновление таблицы
#         pivot = tableau[row, col]
#         tableau[row, :] /= pivot
#         for i in range(tableau.shape[0]):
#             if i != row:
#                 factor = tableau[i, col]
#                 tableau[i, :] -= factor * tableau[row, :]
#
#     # Извлечение решения
#     solution = np.zeros(n)
#     for i in range(m):
#         basic_col = np.where(np.round(tableau[i, :-1], 5) == 1)[0]
#         for col in basic_col:
#             if col < n:
#                 solution[col] = tableau[i, -1]
#
#     min_cost = -tableau[-1, -1]
#     return solution, min_cost
#
#
# # Запуск двойственного симплекс-метода
# solution, cost = dual_simplex(c, A, b)
# x, y, z = solution
#
# print(f"\nРешение:")
# print(f"Количество яиц (x): {x:.0f}")
# print(f"Количество молока (y): {y:.0f}")
# print(f"Количество хлеба (z): {z:.0f}")
# print(f"Минимальные затраты: {cost:.2f}")




from scipy.optimize import linprog

c = [1.5, 2.0, 1.0]

A_ub = [
    [-12, -8, -3],
    [-9, -10, -2],
    [0, -15, -10]
]

b_ub = [-60, -50, -200]

bounds = [(0, None), (0, None), (0, None)]

result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

if result.success:
    print("Оптимальное решение: ")
    print(f"x (яйца): {result.x[0]:.0f}")
    print(f"y (молоко): {result.x[1]:.0f}")
    print(f"z (хлеб): {result.x[2]:.0f}")
    print(f"Минимальные затраты: {result.fun:.2f}")
else:
    print("Решение не найдено.")
    print("Сообщение:", result.message)

















