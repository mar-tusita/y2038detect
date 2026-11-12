#pragma once
#include <time.h>

int timerfd_create(int clockid, int flags);
int timerfd_settime(int fd, int flags, const struct itimerspec *new_value,
                    struct itimerspec *old_value);
int timerfd_gettime(int fd, struct itimerspec *curr_value);

#define TFD_CLOEXEC             0x80000
#define TFD_NONBLOCK            0x800
#define TFD_TIMER_ABSTIME       0x1
#define TFD_TIMER_CANCEL_ON_SET 0x2
