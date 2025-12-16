#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdbool.h>
#include <time.h>

#define MAX_VALUES 50

// Наибольший общий делитель
int __gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

int main() {
    int pipe_parent_to_child[2];
    int pipe_child_to_parent[2];
    pid_t pid;
    int count = 0;

    srand(time(NULL));

    if (pipe(pipe_parent_to_child) == -1 || pipe(pipe_child_to_parent) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    pid = fork();
    if (pid == -1) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid > 0) { // Родительский процесс
        close(pipe_parent_to_child[0]);
        close(pipe_child_to_parent[1]);

        while (count < MAX_VALUES) {
            int n = rand() % 1000 + 2;
            
            if (write(pipe_parent_to_child[1], &n, sizeof(n)) != sizeof(n)) {
                perror("write");
                break;
            }

            int reduced_residues_count;
            if (read(pipe_child_to_parent[0], &reduced_residues_count, sizeof(reduced_residues_count)) != sizeof(reduced_residues_count)) {
                perror("read");
                break;
            }

            if (reduced_residues_count == n - 1) {
                printf("n = %d: Полная и приведённая системы вычетов совпадают.\n", n);
                count++;
            }
        }

        printf("Получено %d значений, для которых системы вычетов совпадают. Завершение работы.\n", count);
        
        close(pipe_parent_to_child[1]);
        close(pipe_child_to_parent[0]);
        wait(NULL); // Ждём завершения дочернего процесса
        
    } else { // Дочерний процесс
        close(pipe_parent_to_child[1]);
        close(pipe_child_to_parent[0]);

        while (true) {
            int n;

            ssize_t bytes_read = read(pipe_parent_to_child[0], &n, sizeof(n));
            if (bytes_read != sizeof(n)) {
                break; // EOF или ошибка то завершаем
            }

            int reduced_residues_count = 0;
            for (int i = 1; i < n; i++) {
                if (__gcd(i, n) == 1) {
                    reduced_residues_count++;
                }
            }

            if (write(pipe_child_to_parent[1], &reduced_residues_count, sizeof(reduced_residues_count)) != sizeof(reduced_residues_count)) {
                perror("write");
                break;
            }
        }

        close(pipe_parent_to_child[0]);
        close(pipe_child_to_parent[1]);
    }

    return 0;
}