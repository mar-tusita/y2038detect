#pragma once
#include <stddef.h>
#ifndef NULL
#define NULL ((void *)0)
#endif
#ifndef CLOCKS_PER_SEC
#define CLOCKS_PER_SEC 1000000
#endif
typedef long long time_t;
typedef long long clock_t;

struct tm {
    int tm_sec;
    int tm_min;
    int tm_hour;
    int tm_mday;
    int tm_mon;
    int tm_year;
    int tm_wday;
    int tm_yday;
    int tm_isdst;
};

struct timespec {
    time_t tv_sec;
    long   tv_nsec;
};

struct itimerspec {
    struct timespec it_interval;
    struct timespec it_value;
};

time_t      time(time_t *);
clock_t     clock(void);
time_t      mktime(struct tm *);
int         nanosleep(const struct timespec *, struct timespec *);
double      difftime(time_t, time_t);
struct tm  *localtime(const time_t *);
struct tm  *gmtime(const time_t *);
char       *ctime(const time_t *);
char       *asctime(const struct tm *);
size_t      strftime(char *, size_t, const char *, const struct tm *);
struct tm  *localtime_r(const time_t *, struct tm *);
struct tm  *gmtime_r(const time_t *, struct tm *);
int         clock_gettime(int, struct timespec *);
extern long timezone;
extern int  daylight;

#define CLOCK_REALTIME           0
#define CLOCK_MONOTONIC          1
#define CLOCK_PROCESS_CPUTIME_ID 2
#define CLOCK_THREAD_CPUTIME_ID  3
#define CLOCK_MONOTONIC_RAW      4
#define CLOCK_REALTIME_COARSE    5
#define CLOCK_MONOTONIC_COARSE   6
#define CLOCK_BOOTTIME           7
#define CLOCK_REALTIME_ALARM     8
#define CLOCK_BOOTTIME_ALARM     9
#define CLOCK_TAI                11
#define TIMER_ABSTIME            1
