#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

int main() {
    int pipefd[2]; // массив для дескрипторов канала
    pid_t pid;
    char buffer[256];
    const char *message = "Привет из родительского процесса";

    // создаем канал
    if (pipe(pipefd) == -1) {
        perror("Ошибка создания канала");
        exit(EXIT_FAILURE);
    }

    // создаем дочерний процесс
    pid = fork();
    if (pid == -1) {
        perror("Ошибка дочернего процесса");
        exit(EXIT_FAILURE);
    }

    if (pid > 0) { // родительский процесс
        close(pipefd[0]); // закрываем ненужный конец канала для чтение

        // пишем сообщение в канал
        if (write(pipefd[1], message, strlen(message) + 1) == -1) {
            perror("Ошибка записи в канал");
            close(pipefd[1]);
            exit(EXIT_FAILURE);
        }

        printf("Родительский процесс отправил сообщение: %s\n", message);
        close(pipefd[1]); // закрываем канал после записи
        wait(NULL); // ожидаем завершения дочернего процесса
    }
    else { // дочерний процесс
        close(pipefd[1]); // закрываем ненужный конец канала для записи

        // читаем сообщение из канала
        ssize_t bytes_read = read(pipefd[0], buffer, sizeof(buffer));
        if (bytes_read == -1) {
            perror("Ошибка чтения из канала");
            close(pipefd[0]);
            exit(EXIT_FAILURE);
        }

        printf("Дочерний процесс получил сообщение: %s\n", buffer);
        close(pipefd[0]);  // Закрываем канал после чтения
    }

    return EXIT_SUCCESS;
}