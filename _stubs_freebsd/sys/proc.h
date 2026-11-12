#pragma once
#include <sys/types.h>
#include <sys/queue.h>
/* Process flags (ki_flag / p_flag) */
#define P_ADVLOCK    0x00000001
#define P_CONTROLT   0x00000002
#define P_KPROC      0x00000004
#define P_FOLLOWFORK 0x00000008
#define P_PPWAIT     0x00000010
#define P_PROFIL     0x00000020
#define P_STOPPROF   0x00000040
#define P_HADTHREADS 0x00000080
#define P_SUGID      0x00000100
#define P_SYSTEM     0x00000200
#define P_SINGLE_EXIT 0x00000400
#define P_TRACED     0x00000800
#define P_WAITED     0x00001000
#define P_WEXIT      0x00002000
#define P_EXEC       0x00004000
#define P_WKILLED    0x00008000
#define P_CONTINUED  0x00010000
#define P_STOPPED_SIG 0x00020000
#define P_STOPPED_TRACE 0x00040000
#define P_STOPPED_SINGLE 0x00080000
#define P_PROTECTED  0x00100000
#define P_SIGEVENT   0x00200000
#define P_SINGLE_BOUNDARY 0x00400000
#define P_HWPMC      0x00800000
#define P_JAILED     0x01000000
#define P_TOTAL_STOP 0x02000000
#define P_INEXEC     0x04000000
/* Process status */
#define SSLEEP  1
#define SWAIT   2
#define SRUN    3
#define SIDL    4
#define SZOMB   5
#define SSTOP   6
#define SDEAD   7
/* forward declaration only — struct proc is kernel-internal */
struct proc;
struct thread;
