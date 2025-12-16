#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>

#define FIFO_NAME "/tmp/my_fifo"

int main() {
    int fd;
    char buffer[101];
    srand(time(NULL));

    fd = open(FIFO_NAME, O_WRONLY);
    if (fd == -1) {
        perror("Error open client.c");
        exit(EXIT_FAILURE);
    }

    printf("Клиент запущен. Отправка строк...\n");

    while (1) {
        int length = rand() % 100 + 1;
        for (int j = 0; j < length; j++) {
            buffer[j] = 'a' + (rand() % 26);
        }
        buffer[length] = '\0';

        ssize_t bytes_written = write(fd, buffer, length + 1);
        if (bytes_written == -1) {
            perror("Error write client.c");
            break;
        }
        printf("Отправлена строка длины %d: %s\n", length, buffer);
        // sleep(1);
    }

    close(fd);
    return 0;
}