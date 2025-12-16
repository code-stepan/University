#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define FIFO_NAME "/tmp/my_fifo"
#define MAX_STRINGS 5

int main() {
    int fd;
    char buffer[101];
    int length_counts[101] = {0}; // массив для подсчета строк одинаковой длины

    // создаем именованный канал
    if (mkfifo(FIFO_NAME, 0666) == -1) {
        perror("Error mkfifo");
        exit(EXIT_FAILURE);
    }

    // открываем канал для чтение
    fd = open(FIFO_NAME, O_RDONLY);
    if (fd == -1) {
        perror("Error open");
        exit(EXIT_FAILURE);
    }

    printf("Сервер запущен. Ожидание строк от клиента...\n");

    while (1) {
        ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
        if (bytes_read == -1) {
            perror("Error read bytes");
            break;
        }
        buffer[bytes_read] = '\0';

        int length = strlen(buffer);
        length_counts[length]++;

        printf("Получена строка длины %d: %s\n", length, buffer);

        if (length_counts[length] >= MAX_STRINGS) {
            printf("Получено %d строк длины %d. Завершение работы.\n", length_counts[length], length);
            break;
        }
    }

    close(fd);
    unlink(FIFO_NAME); // Удаляем канал
    return 0;
}