#pragma once
#include <sys/types.h>
#include <sys/time.h>
#include <sys/proc.h>
#define WMESGLEN     8
#define LOCKNAMELEN  8
#define TDNAMLEN     16
#define COMMLEN      16
#define KI_NGROUPS   16
#define KI_MAXCOMLEN 19
#define KI_MAXLOGNAME 33
#define KI_MAXGROUPS 16
/*
 * Minimal kinfo_proc — contains the fields most commonly accessed in
 * userland programs such as ps(1).  Time-related fields (ki_start,
 * ki_childtime) are kept accurate because y2038detect needs them.
 */
struct kinfo_proc {
    int            ki_structsize;
    int            ki_layout;
    pid_t          ki_pid;
    pid_t          ki_ppid;
    pid_t          ki_pgid;
    pid_t          ki_tpgid;
    pid_t          ki_sid;
    pid_t          ki_tsid;
    short          ki_jobc;
    uid_t          ki_uid;
    uid_t          ki_ruid;
    uid_t          ki_svuid;
    gid_t          ki_rgid;
    gid_t          ki_svgid;
    short          ki_ngroups;
    gid_t          ki_groups[KI_NGROUPS];
    size_t         ki_size;
    long           ki_rssize;
    long           ki_swrss;
    long           ki_tsize;
    long           ki_dsize;
    long           ki_ssize;
    unsigned short ki_xstat;
    unsigned short ki_acflag;
    int            ki_estcpu;
    int            ki_slptime;
    int            ki_swtime;
    unsigned long long ki_runtime;   /* total runtime (microseconds) */
    struct timeval ki_start;         /* process start time */
    struct timeval ki_childtime;     /* sum of children's times */
    long           ki_flag;
    long           ki_kiflag;
    int            ki_traceflag;
    char           ki_stat;
    signed char    ki_nice;
    char           ki_lock;
    char           ki_rqindex;
    unsigned char  ki_oncpu;
    unsigned char  ki_lastcpu;
    char           ki_tdname[TDNAMLEN + 1];
    char           ki_wmesg[WMESGLEN + 1];
    char           ki_login[KI_MAXLOGNAME];
    char           ki_lockname[LOCKNAMELEN + 1];
    char           ki_comm[COMMLEN + 1];
    char           ki_emul[KI_MAXLOGNAME];
    char           ki_loginclass[KI_MAXLOGNAME];
    int            ki_sigmask;
    int            ki_siglist;
    int            ki_sigcatch;
    int            ki_sigignore;
    short          ki_numthreads;
    pid_t          ki_tid;
    int            ki_pri;
    int            ki_rusage;
    int            ki_rusage_ch;
    int            ki_pcb;
    void          *ki_kstack;
    void          *ki_udata;
    void          *ki_tdaddr;
    int            ki_sflag;
    int            ki_tdflags;
};
