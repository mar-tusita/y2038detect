#pragma once
#include <sys/time.h>
#include <sys/types.h>
typedef struct { unsigned long fds_bits[16]; } fd_set;
#define FD_SETSIZE 1024
#define FD_ZERO(s)   do { int _i; for(_i=0;_i<(int)(sizeof(fd_set)/sizeof(long));_i++) ((unsigned long*)(s))[_i]=0; } while(0)
#define FD_SET(d,s)  ((s)->fds_bits[(d)/8/sizeof(long)] |=  (1UL<<((d)%(8*sizeof(long)))))
#define FD_CLR(d,s)  ((s)->fds_bits[(d)/8/sizeof(long)] &= ~(1UL<<((d)%(8*sizeof(long)))))
#define FD_ISSET(d,s)((s)->fds_bits[(d)/8/sizeof(long)] &   (1UL<<((d)%(8*sizeof(long)))))
int select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds,
           struct timeval *timeout);
