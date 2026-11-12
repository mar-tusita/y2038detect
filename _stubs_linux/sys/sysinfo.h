#pragma once

struct sysinfo {
    long           uptime;
    unsigned long  loads[3];
    unsigned long  totalram;
    unsigned long  freeram;
    unsigned long  sharedram;
    unsigned long  bufferram;
    unsigned long  totalswap;
    unsigned long  freeswap;
    unsigned short procs;
    unsigned short pad;
    unsigned long  totalhigh;
    unsigned long  freehigh;
    unsigned int   mem_unit;
    char           _f[0];
};

int  sysinfo(struct sysinfo *info);
int  get_nprocs_conf(void);
int  get_nprocs(void);
long get_phys_pages(void);
long get_avphys_pages(void);

#define SI_LOAD_SHIFT 16
