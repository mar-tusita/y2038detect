#pragma once
#include <sys/types.h>
/* VM totals — as returned by KERN_VMMETER sysctl */
struct vmtotal {
    int16_t t_rq;      /* length of the run queue */
    int16_t t_dw;      /* jobs in disk wait */
    int16_t t_pw;      /* jobs in page wait */
    int16_t t_sl;      /* jobs sleeping in core */
    int16_t t_sw;      /* swapped out runnable/running */
    int32_t t_vm;      /* total virtual memory */
    int32_t t_avm;     /* active virtual memory */
    int32_t t_rm;      /* total real memory in use */
    int32_t t_arm;     /* active real memory */
    int32_t t_vmshr;   /* shared virtual memory */
    int32_t t_avmshr;  /* active shared virtual memory */
    int32_t t_rmshr;   /* real memory shared */
    int32_t t_armshr;  /* active real memory shared */
    int32_t t_free;    /* free memory pages */
};
/* VM event counters */
struct vmmeter {
    unsigned int v_swtch;       /* context switches */
    unsigned int v_trap;        /* calls to trap */
    unsigned int v_syscall;     /* calls to syscall() */
    unsigned int v_intr;        /* device interrupts */
    unsigned int v_soft;        /* software interrupts */
    unsigned int v_vm_faults;   /* number of address memory faults */
    unsigned int v_io_faults;   /* page faults requiring I/O */
    unsigned int v_cow_faults;  /* copy-on-write faults */
    unsigned int v_zfod;        /* pages zero-filled on demand */
    unsigned int v_ozfod;       /* optimized zero-fill pages */
    unsigned int v_swapin;      /* swap pager pageins */
    unsigned int v_swapout;     /* swap pager pageouts */
    unsigned int v_swappgsin;   /* swap pager pages paged in */
    unsigned int v_swappgsout;  /* swap pager pages paged out */
    unsigned int v_vnodein;     /* vnode pager pageins */
    unsigned int v_vnodeout;    /* vnode pager pageouts */
    unsigned int v_vnodepgsin;  /* vnode_pager pages paged in */
    unsigned int v_vnodepgsout; /* vnode pager pages paged out */
    unsigned int v_intrans;     /* intransit blocking page faults */
    unsigned int v_reactivated; /* number of pages reactivated */
    unsigned int v_pdwakeups;   /* times daemon has awakened */
    unsigned int v_pdpages;     /* pages analyzed by daemon */
    unsigned int v_tcached;     /* total pages cached */
    unsigned int v_dfree;       /* pages freed by daemon */
    unsigned int v_pfree;       /* pages freed by exiting processes */
    unsigned int v_tfree;       /* total pages freed */
    unsigned int v_page_size;   /* page size in bytes */
    unsigned int v_page_count;  /* total number of pages in system */
    unsigned int v_free_reserved;   /* pages reserved for deadlock */
    unsigned int v_free_target;     /* pages desired free */
    unsigned int v_free_min;        /* minimum free pages */
    unsigned int v_free_count;      /* pages free */
    unsigned int v_wire_count;      /* pages wired down */
    unsigned int v_active_count;    /* pages active */
    unsigned int v_inactive_target; /* pages desired inactive */
    unsigned int v_inactive_count;  /* pages inactive */
};
