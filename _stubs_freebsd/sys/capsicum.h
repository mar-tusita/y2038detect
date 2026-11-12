#pragma once
#include <sys/types.h>
typedef struct { uint64_t cr_rights[2]; } cap_rights_t;
/* Common capability rights */
#define CAP_READ        ((uint64_t)1 <<  0)
#define CAP_WRITE       ((uint64_t)1 <<  1)
#define CAP_SEEK        ((uint64_t)1 <<  2)
#define CAP_PREAD       ((uint64_t)1 <<  3)
#define CAP_PWRITE      ((uint64_t)1 <<  4)
#define CAP_MMAP        ((uint64_t)1 <<  5)
#define CAP_MMAP_R      ((uint64_t)1 <<  6)
#define CAP_MMAP_W      ((uint64_t)1 <<  7)
#define CAP_MMAP_X      ((uint64_t)1 <<  8)
#define CAP_MMAP_RW     ((uint64_t)1 <<  9)
#define CAP_MMAP_RX     ((uint64_t)1 << 10)
#define CAP_MMAP_WX     ((uint64_t)1 << 11)
#define CAP_MMAP_RWX    ((uint64_t)1 << 12)
#define CAP_CREATE      ((uint64_t)1 << 13)
#define CAP_FEXECVE     ((uint64_t)1 << 14)
#define CAP_FSTAT       ((uint64_t)1 << 15)
#define CAP_FSTATAT     ((uint64_t)1 << 16)
#define CAP_FSTATFS     ((uint64_t)1 << 17)
#define CAP_FSYNC       ((uint64_t)1 << 18)
#define CAP_FTRUNCATE   ((uint64_t)1 << 19)
#define CAP_LOOKUP      ((uint64_t)1 << 20)
#define CAP_UNLINKAT    ((uint64_t)1 << 21)
#define CAP_FCNTL       ((uint64_t)1 << 22)
#define CAP_IOCTL       ((uint64_t)1 << 23)
#define CAP_ACCEPT      ((uint64_t)1 << 24)
#define CAP_BIND        ((uint64_t)1 << 25)
#define CAP_CONNECT     ((uint64_t)1 << 26)
#define CAP_GETPEERNAME ((uint64_t)1 << 27)
#define CAP_GETSOCKNAME ((uint64_t)1 << 28)
#define CAP_GETSOCKOPT  ((uint64_t)1 << 29)
#define CAP_LISTEN      ((uint64_t)1 << 30)
#define CAP_PEELOFF     ((uint64_t)1 << 31)
#define CAP_RECV        CAP_READ
#define CAP_SEND        CAP_WRITE
#define CAP_SETSOCKOPT  ((uint64_t)1 << 32)
#define CAP_SHUTDOWN    ((uint64_t)1 << 33)
#define CAP_RENAMEAT_SOURCE ((uint64_t)1 << 34)
#define CAP_RENAMEAT_TARGET ((uint64_t)1 << 35)
#define CAP_SYMLINKAT   ((uint64_t)1 << 36)
#define CAP_MKDIRAT     ((uint64_t)1 << 37)
#define CAP_MKFIFOAT    ((uint64_t)1 << 38)
#define CAP_MKNODAT     ((uint64_t)1 << 39)
#define CAP_LINKAT_SOURCE ((uint64_t)1 << 40)
#define CAP_LINKAT_TARGET ((uint64_t)1 << 41)
#define CAP_SOCK_CLIENT (CAP_CONNECT | CAP_GETPEERNAME | CAP_GETSOCKNAME | CAP_GETSOCKOPT | CAP_PEELOFF | CAP_RECV | CAP_SEND | CAP_SETSOCKOPT | CAP_SHUTDOWN)
#define CAP_SOCK_SERVER (CAP_ACCEPT | CAP_BIND | CAP_GETPEERNAME | CAP_GETSOCKNAME | CAP_GETSOCKOPT | CAP_LISTEN | CAP_PEELOFF | CAP_RECV | CAP_SEND | CAP_SETSOCKOPT | CAP_SHUTDOWN)
cap_rights_t *cap_rights_init(cap_rights_t *rights, ...);
cap_rights_t *cap_rights_set(cap_rights_t *rights, ...);
cap_rights_t *cap_rights_clear(cap_rights_t *rights, ...);
int cap_rights_limit(int fd, const cap_rights_t *rights);
int cap_rights_get(int fd, cap_rights_t *rights);
int cap_enter(void);
int cap_getmode(unsigned int *modep);
int cap_sandboxed(void);
