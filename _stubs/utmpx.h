#pragma once
#include <sys/time.h>

#define EMPTY         0
#define BOOT_TIME     2
#define OLD_TIME      4
#define NEW_TIME      3
#define INIT_PROCESS  5
#define LOGIN_PROCESS 6
#define USER_PROCESS  7
#define DEAD_PROCESS  8

struct utmpx {
    short          ut_type;
    char           ut_id[4];
    struct timeval ut_tv;
};

void setutxent(void);
void endutxent(void);
struct utmpx *getutxent(void);
struct utmpx *getutxid(const struct utmpx *);
struct utmpx *getutxline(const struct utmpx *);
int pututxline(const struct utmpx *);
