#pragma once
#include <sys/types.h>
#include <sys/time.h>

struct rlimit {
    unsigned long long rlim_cur;
    unsigned long long rlim_max;
};
struct rusage {
    struct timeval ru_utime;
    struct timeval ru_stime;
};

#define RLIMIT_CPU    0
#define RLIMIT_FSIZE  1
#define RLIMIT_DATA   2
#define RLIMIT_STACK  3
#define RLIMIT_CORE   4
#define RLIMIT_NOFILE 7
#define RLIMIT_AS     9
#define RLIMIT_NPROC  6
#define RLIM_INFINITY (~0ULL)
#define PRIO_PROCESS  0
#define PRIO_PGRP     1
#define PRIO_USER     2
#define PRIO_MAX      20
#define RUSAGE_SELF      0
#define RUSAGE_CHILDREN (-1)

int getrlimit(int resource, struct rlimit *rlim);
int setrlimit(int resource, const struct rlimit *rlim);
int getrusage(int who, struct rusage *usage);
int getpriority(int which, unsigned int who);
int setpriority(int which, unsigned int who, int prio);
