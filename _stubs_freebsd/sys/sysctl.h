#pragma once
#include <sys/types.h>
/* Top-level sysctl names */
#define CTL_KERN    1
#define CTL_VM      2
#define CTL_VFS     3
#define CTL_NET     4
#define CTL_DEBUG   5
#define CTL_HW      6
#define CTL_MACHDEP 7
#define CTL_USER    8
/* kern subtypes */
#define KERN_OSTYPE        1
#define KERN_OSRELEASE     2
#define KERN_OSREV         3
#define KERN_VERSION       4
#define KERN_MAXVNODES     5
#define KERN_MAXPROC       6
#define KERN_MAXFILES      7
#define KERN_ARGMAX        8
#define KERN_HOSTNAME      10
#define KERN_DOMAINNAME    22
#define KERN_BOOTTIME      21
#define KERN_PROC          14
#define KERN_PROC_ALL      0
#define KERN_PROC_PID      1
#define KERN_PROC_PGRP     2
#define KERN_PROC_SESSION  3
#define KERN_PROC_TTY      4
#define KERN_PROC_UID      5
#define KERN_PROC_RUID     6
#define KERN_PROC_ARGS     7
#define KERN_PROC_PATHNAME 12
#define KERN_PROC_VMMAP    32
#define KERN_PROC_FILEDESC 33
#define KERN_PROC_GROUPS   34
#define KERN_PROC_INC_THREAD 0x10
/* hw subtypes */
#define HW_MACHINE   1
#define HW_MODEL     2
#define HW_NCPU      3
#define HW_BYTEORDER 4
#define HW_PHYSMEM   5
#define HW_USERMEM   6
#define HW_PAGESIZE  7
#define HW_REALMEM   19
/* CTLTYPE */
#define CTLTYPE_NODE   1
#define CTLTYPE_INT    2
#define CTLTYPE_STRING 3
#define CTLTYPE_QUAD   4
#define CTLTYPE_OPAQUE 5
#define CTLTYPE_UINT   6
#define CTLTYPE_LONG   7
#define CTLTYPE_ULONG  8
#define CTLTYPE_S8     11
#define CTLTYPE_S16    12
#define CTLTYPE_S32    13
#define CTLTYPE_S64    14
#define CTLTYPE_U8     15
#define CTLTYPE_U16    16
#define CTLTYPE_U32    17
#define CTLTYPE_U64    18
/* CTLFLAG */
#define CTLFLAG_RD     0x80000000
#define CTLFLAG_WR     0x40000000
#define CTLFLAG_RW     (CTLFLAG_RD|CTLFLAG_WR)
#define CTLFLAG_ANYBODY 0x10000000
#define CTLFLAG_SECURE 0x08000000
struct ctlname {
    char *ctl_name;
    int   ctl_type;
};
int sysctl(const int *name, unsigned int namelen, void *oldp, size_t *oldlenp,
           const void *newp, size_t newlen);
int sysctlbyname(const char *name, void *oldp, size_t *oldlenp,
                 const void *newp, size_t newlen);
int sysctlnametomib(const char *name, int *mibp, size_t *sizep);
