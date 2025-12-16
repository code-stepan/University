#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define BUFFER_SIZE 8192

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Должно быть 3 аргумента\n");
        return 1;
    }

    char real_source_path[PATH_MAX];
    char real_dest_path[PATH_MAX];

    if (realpath(argv[1], real_source_path) == NULL) {
        perror("Ошибка получения абсолютного пути source");
        return 1;
    }
    if (realpath(argv[2], real_dest_path) == NULL) {
        perror("Ошибка получения абсолютного пути dest");
        return 1;
    }

    if (strcmp(real_source_path, real_dest_path) == 0) {
        printf("Ошибка: нельзя копировать файл в самого себя\n");
        return 1;
    }

    FILE *source = fopen(argv[1], "rb");
    if (!source) {
        perror("Ошибка открытия файла source");
        return 1;
    }

    FILE *dest = fopen(argv[2], "wb");
    if (!dest) {
        perror("Ошибка открытия файла dest");
        fclose(source);
        return 1;
    }

    char buffer[BUFFER_SIZE];
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, source)) > 0) {
        size_t bytes_written = fwrite(buffer, 1, bytes_read, dest);
        if (bytes_written != bytes_read) {
            perror("Ошибка записи в файл");
            break;
        }
    }

    fclose(source);
    fclose(dest);

    return 0;
}