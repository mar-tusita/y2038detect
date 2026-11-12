#pragma once
#include <stdint.h>
#include <signal.h>
#include <time.h>

union epoll_data {
    void     *ptr;
    int       fd;
    uint32_t  u32;
    uint64_t  u64;
};
typedef union epoll_data epoll_data_t;
struct epoll_event {
    uint32_t     events;
    epoll_data_t data;
};

int epoll_create(int size);
int epoll_create1(int flags);
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
int epoll_pwait(int epfd, struct epoll_event *events, int maxevents, int timeout,
                const sigset_t *sigmask);
int epoll_pwait2(int epfd, struct epoll_event *events, int maxevents,
                 const struct timespec *timeout, const sigset_t *sigmask);

#define EPOLLIN         0x1
#define EPOLLPRI        0x2
#define EPOLLOUT        0x4
#define EPOLLERR        0x8
#define EPOLLHUP        0x10
#define EPOLLRDNORM     0x40
#define EPOLLRDBAND     0x80
#define EPOLLWRNORM     0x100
#define EPOLLWRBAND     0x200
#define EPOLLMSG        0x400
#define EPOLLRDHUP      0x2000
#define EPOLLWAKEUP     0x20000000
#define EPOLLEXCLUSIVE  0x10000000
#define EPOLLONESHOT    0x40000000
#define EPOLLET         0x80000000
#define EPOLL_CLOEXEC   0x80000
#define EPOLL_CTL_ADD   1
#define EPOLL_CTL_DEL   2
#define EPOLL_CTL_MOD   3
