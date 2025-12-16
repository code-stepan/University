#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#define FIFO_PATH_PATTERN "/tmp/jos_%d_%zu"
#define MAX_PATH 4096

typedef enum MsgType {
    MSG_INIT = 1,
    MSG_TOKEN = 2,
    MSG_REBIND = 3,
    MSG_ACK = 4
} MsgType;

typedef struct Msg {
    MsgType type;
    pid_t from;
    pid_t target;
    pid_t next_pid;
    char next_fifo[MAX_PATH];
    int count; // счетчик токенов
    int k;
} Msg;

// пишет ровно n байт, повторяет при EINTR
static int write_full(const int fd, const void *buf, const size_t n) {
    const char *p = buf;
    size_t left = n;

    while (left > 0) {
        const ssize_t w = write(fd, p, left);
        if (w < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += (size_t)w;
        left -= (size_t)w;
    }
    return 0;
}

// Читает ровно n байт, возвращает 1 при успехе, 0 при EOF, -1 при ошибке
static int read_full(const int fd, void *buf, const size_t n) {
    char *p = buf;
    size_t left = n;

    while (left > 0) {
        const ssize_t r = read(fd, p, left);
        if (r == 0) return 0; // EOF
        if (r < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += (size_t)r;
        left -= (size_t)r;
    }
    return 1;
}

// Отправка сообщения в FIFO
static int send_msg_to_fifo(const char *fifo_path, const Msg *m) {
    const int fd = open(fifo_path, O_WRONLY);
    if (fd < 0) {
        perror("FIFO open error");
        return -1;
    }

    const int rc = write_full(fd, m, sizeof(*m));
    close(fd);
    return rc;
}

// Генерация имени FIFO
static void make_fifo_name(char *out, const size_t cap, const pid_t ppid, const size_t idx) {
    snprintf(out, cap, FIFO_PATH_PATTERN, (int)ppid, idx);
}

// Удаление всех созданных FIFO
static void unlink_all(const char (*fifos)[MAX_PATH], const size_t n) {
    for (size_t i = 0; i < n; ++i) {
        unlink(fifos[i]);
    }
}

// Парсинг положительного целого числа в заданном диапазоне
static int parse_positive_int(const char *s, const int min_inclusive, const int max_inclusive, int *out) {
    char *end = NULL;
    errno = 0;
    long v = strtol(s, &end, 10);

    if (errno != 0 || end == s || *end != '\0') {
        return 0;
    }
    if (v < min_inclusive || v > max_inclusive || v > INT_MAX || v < INT_MIN) {
        return 0;
    }

    *out = (int)v;
    return 1;
}

// Обработка сообщения инициализации
static void handle_init(const Msg *msg, int *k, pid_t *next_pid, char next_fifo[MAX_PATH]) {
    *k = msg->k;
    *next_pid = msg->next_pid;
    strncpy(next_fifo, msg->next_fifo, MAX_PATH - 1);
    next_fifo[MAX_PATH - 1] = '\0';
}

// Отправка сообщения о ребиндинге
static void send_rebind(const pid_t self, const pid_t target, const pid_t next_pid, const char next_fifo[MAX_PATH]) {
    Msg rebind = {0};
    rebind.type = MSG_REBIND;
    rebind.from = self;
    rebind.target = target;
    rebind.next_pid = next_pid;
    strncpy(rebind.next_fifo, next_fifo, MAX_PATH - 1);
    rebind.next_fifo[MAX_PATH - 1] = '\0';
    send_msg_to_fifo(next_fifo, &rebind);
}

// Отправка токена следующему
static void send_next_token(const pid_t self, const char next_fifo[MAX_PATH]) {
    Msg next_tkn = {0};
    next_tkn.type = MSG_TOKEN;
    next_tkn.from = self;
    next_tkn.count = 0;
    send_msg_to_fifo(next_fifo, &next_tkn);
}

// Отправка ACK удаленному процессу
static void send_ack_to_removed(const pid_t self, const pid_t removed_pid, const char next_fifo[MAX_PATH]) {
    Msg ack = {0};
    ack.type = MSG_ACK;
    ack.from = self;
    ack.target = removed_pid;
    send_msg_to_fifo(next_fifo, &ack);
}

// Цикл дочернего процесса
static void child_loop(const char *my_fifo_path) {
    const pid_t self = getpid();

    const int rfd = open(my_fifo_path, O_RDONLY);
    if (rfd < 0) {
        _exit(1);
    }

    // Удерживаем write-дескриптор, чтобы избежать EOF
    const int keep_wfd = open(my_fifo_path, O_WRONLY | O_NONBLOCK);
    if (keep_wfd < 0) {
        close(rfd);
        _exit(1);
    }

    char next_fifo[MAX_PATH] = {0};
    pid_t next_pid = -1;
    int k = -1;
    int removed = 0;

    while (1) {
        Msg msg = {0};
        const int r = read_full(rfd, &msg, sizeof(msg));

        if (r <= 0) break;

        int is_still_running = 1;
        switch (msg.type) {
            case MSG_INIT:
                handle_init(&msg, &k, &next_pid, next_fifo);
                break;

            case MSG_TOKEN:
                if (removed) {
                    send_msg_to_fifo(next_fifo, &msg);
                    break;
                }

                const int new_count = msg.count + 1;
                if (new_count >= k) {
                    send_rebind(self, msg.from, next_pid, next_fifo);
                    send_next_token(self, next_fifo);
                    removed = 1;
                } else {
                    Msg pass = {0};
                    pass.type = MSG_TOKEN;
                    pass.from = self;
                    pass.count = new_count;
                    send_msg_to_fifo(next_fifo, &pass);
                }
                break;

            case MSG_REBIND:
                if (msg.target == self) {
                    send_ack_to_removed(self, msg.from, next_fifo);
                    next_pid = msg.next_pid;
                    strncpy(next_fifo, msg.next_fifo, MAX_PATH - 1);
                    next_fifo[MAX_PATH - 1] = '\0';
                } else {
                    send_msg_to_fifo(next_fifo, &msg);
                }
                break;

            case MSG_ACK:
                if (msg.target == self) {
                    is_still_running = 0;
                } else {
                    send_msg_to_fifo(next_fifo, &msg);
                }
                break;

            default:
                send_msg_to_fifo(next_fifo, &msg);
                break;
        }
        if (!is_still_running) break;
    }

    close(rfd);
    close(keep_wfd);
    _exit(0);
}

// Создание всех FIFO
static int create_all_fifos(char (*fifos)[MAX_PATH], const size_t n, const pid_t ppid) {
    for (size_t i = 0; i < n; ++i) {
        make_fifo_name(fifos[i], MAX_PATH, ppid, i);
        unlink(fifos[i]);  // на всякий случай удаляем старый FIFO
        if (mkfifo(fifos[i], 0666) == -1) {
            perror("mkfifo");
            return 0;
        }
    }
    return 1;
}

// Форк дочерних процессов
static int fork_children(pid_t *pids, const char (*fifos)[MAX_PATH], size_t n) {
    for (size_t i = 0; i < n; ++i) {
        const pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            return 0;
        }
        if (pid == 0) {
            child_loop(fifos[i]);
            _exit(0);
        }
        pids[i] = pid;
    }
    return 1;
}

// Отправка сообщения инициализации каждому процессу
static void send_init_to_each(const char (*fifos)[MAX_PATH], const pid_t *pids, const size_t n, const int k) {
    for (size_t i = 0; i < n; ++i) {
        const size_t next = (i + 1) % n;
        Msg init = {0};
        init.type = MSG_INIT;
        init.k = k;
        init.next_pid = pids[next];
        strncpy(init.next_fifo, fifos[next], MAX_PATH - 1);
        init.next_fifo[MAX_PATH - 1] = '\0';
        send_msg_to_fifo(fifos[i], &init);
    }
}

// Запуск первого токена
static void start_first_token(const char (*fifos)[MAX_PATH]) {
    send_next_token(getpid(), fifos[0]);
}

int main(int argc, char *argv[]) {
    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        perror("signal");
        return 1;
    }

    if (argc != 3) {
        fprintf(stderr, "Usage: %s <n> <k>\n", argv[0]);
        return 1;
    }

    int n = 0, k = 0;

    if (!parse_positive_int(argv[1], 2, INT_MAX, &n)) {
        fprintf(stderr, "n must be integer > 1\n");
        return 1;
    }

    if (!parse_positive_int(argv[2], 2, n - 1, &k)) {
        fprintf(stderr, "k must be integer, 1 < k < n\n");
        return 1;
    }

    char (*fifos)[MAX_PATH] = calloc(n, sizeof(*fifos));
    if (fifos == NULL) {
        perror("calloc fifos");
        return 1;
    }

    pid_t *pids = calloc(n, sizeof(*pids));
    if (pids == NULL) {
        perror("calloc pids");
        free(fifos);
        return 1;
    }

    const pid_t ppid = getpid();
    int ok = create_all_fifos(fifos, (size_t)n, ppid);
    if (!ok) {
        unlink_all(fifos, (size_t)n);
        free(fifos);
        free(pids);
        return 1;
    }

    ok = fork_children(pids, fifos, (size_t)n);
    if (!ok) {
        unlink_all(fifos, (size_t)n);
        free(fifos);
        free(pids);
        return 1;
    }

    send_init_to_each(fifos, pids, (size_t)n, k);
    start_first_token(fifos);

    pid_t *order = calloc(n, sizeof(*order));
    if (order == NULL) {
        perror("calloc order");
        // всё равно продолжаем, просто не выводим порядок
    }

    size_t gone = 0;
    while (gone < (size_t)n) {
        int status = 0;
        const pid_t pid = waitpid(-1, &status, 0);
        if (pid > 0) {
            if (order != NULL) {
                order[gone] = pid;
            }
            gone++;
        } else if (pid == -1 && errno == EINTR) {
            continue;
        } else {
            break;
        }
    }

    printf("Josephus ring finished: n=%d, k=%d\n", n, k);
    printf("Termination order (PIDs):\n");

    if (order != NULL) {
        for (size_t i = 0; i < gone; ++i) {
            printf("%2zu) %d\n", i + 1, (int)order[i]);
        }
    }

    unlink_all(fifos, (size_t)n);
    free(order);
    free(pids);
    free(fifos);

    return 0;
}