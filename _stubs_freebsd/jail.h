#pragma once
#include <sys/jail.h>
/*
 * FreeBSD libjail userland API (top-level jail.h).
 * Distinct from <sys/jail.h> which defines the jail syscall interface.
 */
struct jailparam {
    char *jp_name;
    void *jp_value;
    size_t jp_valuelen;
    size_t jp_elemlen;
    int jp_ctltype;
    int jp_structtype;
    unsigned jp_flags;
};
#define JAIL_CREATE  0x01
#define JAIL_UPDATE  0x02
#define JAIL_ATTACH  0x04
#define JAIL_DYING   0x08
int   jail_getid(const char *name);
char *jail_getname(int jid);
int   jail_setv(int flags, ...);
int   jail_getv(int flags, ...);
int   jailparam_init(struct jailparam *jp, const char *name);
int   jailparam_import(struct jailparam *jp, const char *value);
int   jailparam_import_raw(struct jailparam *jp, void *value, size_t valuelen);
int   jailparam_set(struct jailparam *params, unsigned int length, int flags);
int   jailparam_get(struct jailparam *params, unsigned int length, int flags);
char *jailparam_export(struct jailparam *jp);
void  jailparam_free(struct jailparam *params, unsigned int length);
