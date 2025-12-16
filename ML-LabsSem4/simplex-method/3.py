import numpy as np

def simplex(c, A, b, types, maximize=True):
    m, n = A.shape
    slack_vars = sum(1 for t in types if t == '<=')
    surplus_vars = sum(1 for t in types if t == '>=')
    artificial_vars = sum(1 for t in types if t in ['>=', '='])

    total_vars = n + slack_vars + surplus_vars + artificial_vars
    tableau = np.zeros((m + 1, total_vars + 1))

    tableau[:-1, :n] = A
    tableau[:-1, -1] = b

    col_labels = list(range(total_vars))
    basis = []

    slack_idx = n
    art_start = n + slack_vars + surplus_vars

    for i in range(m):
        if types[i] == '<=':
            tableau[i, slack_idx] = 1
            basis.append(slack_idx)
            slack_idx += 1
        elif types[i] == '>=':
            tableau[i, slack_idx] = 0
            tableau[i, slack_idx + 1] = -1
            tableau[i, art_start] = 1
            basis.append(art_start)
            slack_idx += 1
            art_start += 1
        elif types[i] == '=':
            tableau[i, art_start] = 1
            basis.append(art_start)
            art_start += 1

    tableau[-1, :n] = -c if maximize else c

    print("Начальная симплекс-таблица:")
    print(tableau)

    iteration = 0
    while True:
        print(f"\n--- Итерация {iteration} ---")
        print(tableau)

        entering_col = np.argmin(tableau[-1, :-1])
        if tableau[-1, entering_col] >= 0:
            break

        ratios = np.divide(tableau[:-1, -1], tableau[:-1, entering_col],
                           out=np.full(m, np.inf), where=tableau[:-1, entering_col] > 0)

        leaving_row = np.argmin(ratios)
        if ratios[leaving_row] == np.inf:
            raise ValueError("Задача неограниченна.")

        pivot = tableau[leaving_row, entering_col]
        tableau[leaving_row, :] /= pivot
        for r in range(m + 1):
            if r != leaving_row:
                tableau[r, :] -= tableau[r, entering_col] * tableau[leaving_row, :]

        basis[leaving_row] = entering_col
        iteration += 1

    solution = np.zeros(total_vars)
    for r in range(m):
        solution[basis[r]] = tableau[r, -1]

    optimal_value = tableau[-1, -1]
    return solution[:n], optimal_value


if __name__ == "__main__":
    c = np.array([5, 4])
    A = np.array([[1, 2],
                  [6, 4],
                  [-1, 1]])
    b = np.array([6, 24, 1])
    types = ['<=', '<=', '<=']

    solution, value = simplex(c, A, b, types, maximize=True)

    print("\nОптимальное решение:")
    print(f"x1 = {solution[0]:.1f}, x2 = {solution[1]:.1f}")
    print(f"Целевая функция Z = {value:.1f}")