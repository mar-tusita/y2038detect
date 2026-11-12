#pragma once
#include <time.h>

typedef long suseconds_t;

struct timeval {
    time_t tv_sec;
    long   tv_usec;
};

struct itimerval {
    struct timeval it_interval;
    struct timeval it_value;
};

int gettimeofday(struct timeval *, void *);
int settimeofday(const struct timeval *, const void *);
int getitimer(int, struct itimerval *);
int setitimer(int, const struct itimerval *, struct itimerval *);
int utimes(const char *, const struct timeval[2]);
int lutimes(const char *, const struct timeval[2]);
int futimes(int, const struct timeval[2]);

#define ITIMER_REAL     0x0
#define ITIMER_VIRTUAL  0x1
#define ITIMER_PROF     0x2
