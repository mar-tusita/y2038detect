#pragma once
#include <sys/types.h>
#include <time.h>
typedef long long  intptr_t;
typedef unsigned long long uintptr_t;
struct kevent {
    uintptr_t      ident;
    short          filter;
    unsigned short flags;
    unsigned int   fflags;
    intptr_t       data;
    void          *udata;
};
#define EVFILT_READ     (-1)
#define EVFILT_WRITE    (-2)
#define EVFILT_AIO      (-3)
#define EVFILT_VNODE    (-4)
#define EVFILT_PROC     (-5)
#define EVFILT_SIGNAL   (-6)
#define EVFILT_TIMER    (-7)
#define EVFILT_USER     (-11)
#define EV_ADD       0x0001
#define EV_DELETE    0x0002
#define EV_ENABLE    0x0004
#define EV_DISABLE   0x0008
#define EV_ONESHOT   0x0010
#define EV_CLEAR     0x0020
#define EV_RECEIPT   0x0040
#define EV_DISPATCH  0x0080
#define EV_EOF       0x8000
#define EV_ERROR     0x4000
#define NOTE_DELETE  0x0001
#define NOTE_WRITE   0x0002
#define NOTE_EXTEND  0x0004
#define NOTE_ATTRIB  0x0008
#define NOTE_LINK    0x0010
#define NOTE_RENAME  0x0020
#define NOTE_REVOKE  0x0040
#define NOTE_EXIT    0x80000000U
#define NOTE_FORK    0x40000000U
#define NOTE_EXEC    0x20000000U
#define NOTE_SECONDS    0x00000001U
#define NOTE_MSECONDS   0x00000002U
#define NOTE_USECONDS   0x00000004U
#define NOTE_NSECONDS   0x00000008U
#define EV_SET(kevp, a, b, c, d, e, f) do {    \
    struct kevent *__kevp__ = (kevp);           \
    __kevp__->ident  = (a);                     \
    __kevp__->filter = (b);                     \
    __kevp__->flags  = (c);                     \
    __kevp__->fflags = (d);                     \
    __kevp__->data   = (e);                     \
    __kevp__->udata  = (f);                     \
} while (0)
int kqueue(void);
int kevent(int kq, const struct kevent *changelist, int nchanges,
           struct kevent *eventlist, int nevents,
           const struct timespec *timeout);
