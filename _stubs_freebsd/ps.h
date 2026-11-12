#pragma once
/*
 * Minimal stub for FreeBSD ps(1) internal header.
 * Provides just enough for y2038detect to parse print.c.
 */
#include <sys/types.h>
#include <sys/user.h>
#define MAXSLP 20
#define __unused __attribute__((unused))
/* ps(1) display data attached to each process */
struct kd {
    char *prefix;
};
/* Extended process info as used internally by ps(1) */
typedef struct {
    struct kinfo_proc *ki_p;  /* pointer into kinfo_proc array */
    char              *ki_args;
    char              *ki_env;
    struct kd          ki_d;
    int                ki_valid;
} KINFO;
/* Column variable definition */
typedef struct var {
    const char *name;
    const char *header;
    const char *alias;
    int         flag;
    void      (*oproc)(KINFO *, struct varent *);
    int         width;
    int         type;
} VAR;
typedef struct varent {
    struct varent *next;
    VAR           *var;
} VARENT;
/* Common flags */
#define COMM    0x001
#define LJUST   0x002
#define USER    0x004
#define DSIZ    0x008
#define INF127  0x010
#define PGTOK   0x020
