#pragma once
#include <sys/types.h>
#define CPU_SETSIZE  256
#define _NCPUBITS    (sizeof(long) * 8)
#define _NCPUWORDS   (CPU_SETSIZE / _NCPUBITS)
typedef struct _cpuset { unsigned long __bits[_NCPUWORDS]; } cpuset_t;
typedef int cpusetid_t;
typedef int cpulevel_t;
typedef int cpuwhich_t;
#define CPU_LEVEL_ROOT    1
#define CPU_LEVEL_CPUSET  2
#define CPU_LEVEL_WHICH   3
#define CPU_WHICH_TID     1
#define CPU_WHICH_PID     2
#define CPU_WHICH_CPUSET  3
#define CPU_WHICH_IRQ     4
#define CPU_WHICH_JAIL    5
#define CPU_ZERO(s)       __builtin_memset(s, 0, sizeof(*(s)))
#define CPU_SET(n, s)     ((s)->__bits[(n)/_NCPUBITS] |=  (1UL << ((n) % _NCPUBITS)))
#define CPU_CLR(n, s)     ((s)->__bits[(n)/_NCPUBITS] &= ~(1UL << ((n) % _NCPUBITS)))
#define CPU_ISSET(n, s)   ((s)->__bits[(n)/_NCPUBITS] &   (1UL << ((n) % _NCPUBITS)))
int cpuset(cpusetid_t *setid);
int cpuset_getaffinity(cpulevel_t level, cpuwhich_t which, id_t id,
                       size_t setsize, cpuset_t *mask);
int cpuset_setaffinity(cpulevel_t level, cpuwhich_t which, id_t id,
                       size_t setsize, const cpuset_t *mask);
int cpuset_getid(cpulevel_t level, cpuwhich_t which, id_t id,
                 cpusetid_t *setid);
int cpuset_setid(cpuwhich_t which, id_t id, cpusetid_t setid);
