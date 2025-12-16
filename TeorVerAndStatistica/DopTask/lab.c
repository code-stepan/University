#include <stdio.h>
#include <math.h>
#include <omp.h>

#define M_PI 3.14159265358979323846

double f(double t) {
    return exp(-t * t);
}

double rectangle_method(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = 0.0;

    #pragma omp parallel for reduction(+:sum)
    for (int i = 0; i < n; i++) {
        sum += f(a + i * h + h / 2);
    }

    return (2 / sqrt(M_PI)) * h * sum;
}

double trapezoid_method(double a, double b, int n) {
    double h = (b - a) / n;
    double sum = (f(a) + f(b)) / 2;

    #pragma omp parallel for reduction(+:sum)
    for (int i = 1; i < n; i++) {
        sum += f(a + i * h);
    }

    return (2 / sqrt(M_PI)) * h * sum;
}

double bisection_method(double y, double epsilon) {
    double a = 0.0;
    double b = 10.0;
    double c;
    while ((b - a) > epsilon) {
        c = (a + b) / 2;
        if (trapezoid_method(0, c, 1000) < y) {
            a = c;
        } else {
            b = c;
        }
    }
    return (a + b) / 2;
}

double newton_method(double y, double epsilon) {
    double x0 = 1.0;
    double x1;
    do {
        double fx = trapezoid_method(0, x0, 1000) - y;
        double dfx = (2 / sqrt(M_PI)) * exp(-x0 * x0);
        x1 = x0 - fx / dfx;
        if (fabs(x1 - x0) < epsilon) {
            break;
        }
        x0 = x1;
    } while (1);
    return x1;
}

int main() {
    double x, epsilon;
    int n;

    // Ввод данных пользователем
    printf("Введите значение x: ");
    scanf("%lf", &x);

    printf("Введите точность epsilon (например, 1e-6): ");
    scanf("%lf", &epsilon);

    printf("Введите количество разбиений n для интегрирования: ");
    scanf("%d", &n);

    // Прямая задача: вычисление Φ(x)
    double y_rectangle = rectangle_method(0, x, n);
    double y_trapezoid = trapezoid_method(0, x, n);

    printf("\nМетод прямоугольников: Φ(%.6f) ≈ %.10f\n", x, y_rectangle);
    printf("Метод трапеций: Φ(%.6f) ≈ %.10f\n", x, y_trapezoid);

    // Обратная задача: нахождение x по y
    double x_bisection = bisection_method(y_trapezoid, epsilon);
    double x_newton = newton_method(y_trapezoid, epsilon);

    printf("\nОбратная задача (бисекция): x ≈ %.10f\n", x_bisection);
    printf("Обратная задача (Ньютон): x ≈ %.10f\n", x_newton);

    return 0;
}
