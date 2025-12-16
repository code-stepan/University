import numpy as np
import matplotlib.pyplot as plt

x = np.array([25, 40, 55, 70, 85, 100])
y = np.array([2.4, 3.2, 3.8, 4.3, 4.7, 5.1])
n = len(x)

# Линейная
A_lin = np.vstack([x, np.ones(n)]).T
a_lin, b_lin = np.linalg.lstsq(A_lin, y, rcond=None)[0]
y_lin = a_lin * x + b_lin

# Степенная
log_x = np.log(x)
log_y = np.log(y)

A_pow = np.vstack([log_x, np.ones(n)]).T
a_pow, log_beta_pow = np.linalg.lstsq(A_pow, log_y, rcond=None)[0]

beta_pow = np.exp(log_beta_pow)
y_pow = beta_pow * x ** a_pow

# Показательная
log_y_exp = np.log(y)
A_exp = np.vstack([x, np.ones(n)]).T
a_exp, log_beta_exp = np.linalg.lstsq(A_exp, log_y_exp, rcond=None)[0]

beta_exp = np.exp(log_beta_exp)
y_exp = beta_exp * np.exp(a_exp * x)

# Квадратичная
A_quad = np.vstack([x**2, x, np.ones(n)]).T
a_quad, b_quad, c_quad = np.linalg.lstsq(A_quad, y, rcond=None)[0]
y_quad = a_quad * x**2 + b_quad * x + c_quad

# Ошибки
S_lin = np.sum((y - y_lin)**2)
S_pow = np.sum((y - y_pow)**2)
S_exp = np.sum((y - y_exp)**2)
S_quad = np.sum((y - y_quad)**2)

print("S (линейная):", S_lin)
print("S (степенная):", S_pow)
print("S (показательная):", S_exp)
print("S (квадратичная):", S_quad)

# Визуализация
x_dense = np.linspace(min(x), max(x), 500)
y_lin_dense = a_lin * x_dense + b_lin
y_pow_dense = beta_pow * x_dense**a_pow
y_exp_dense = beta_exp * np.exp(a_exp * x_dense)
y_quad_dense = a_quad * x_dense**2 + b_quad * x_dense + c_quad

# Отдельные графики
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

axs[0, 0].plot(x_dense, y_lin_dense, label='Линейная', color='blue')
axs[0, 0].scatter(x, y, color='black')
axs[0, 0].set_title('Линейная аппроксимация')
axs[0, 0].legend()

axs[0, 1].plot(x_dense, y_pow_dense, label='Степенная', color='green')
axs[0, 1].scatter(x, y, color='black')
axs[0, 1].set_title('Степенная аппроксимация')
axs[0, 1].legend()

axs[1, 0].plot(x_dense, y_exp_dense, label='Показательная', color='orange')
axs[1, 0].scatter(x, y, color='black')
axs[1, 0].set_title('Показательная аппроксимация')
axs[1, 0].legend()

axs[1, 1].plot(x_dense, y_quad_dense, label='Квадратичная', color='red')
axs[1, 1].scatter(x, y, color='black')
axs[1, 1].set_title('Квадратичная аппроксимация')
axs[1, 1].legend()

plt.tight_layout()
plt.show()

# Совместный график
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='black', label='Экспериментальные точки')
plt.plot(x_dense, y_lin_dense, label='Линейная', color='blue')
plt.plot(x_dense, y_pow_dense, label='Степенная', color='green')
plt.plot(x_dense, y_exp_dense, label='Показательная', color='orange')
plt.plot(x_dense, y_quad_dense, label='Квадратичная', color='red')
plt.title('Сравнение аппроксимаций')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()