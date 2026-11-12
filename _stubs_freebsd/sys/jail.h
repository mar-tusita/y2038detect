#pragma once
#include <sys/types.h>
#include <netinet/in.h>
#define JAIL_API_VERSION 2
struct jail {
    uint32_t        version;
    char           *path;
    char           *hostname;
    char           *jailname;
    unsigned int    ip4s;
    unsigned int    ip6s;
    struct in_addr *ip4;
    struct in6_addr *ip6;
};
#define JAIL_CREATE   0x01
#define JAIL_UPDATE   0x02
#define JAIL_ATTACH   0x04
#define JAIL_DYING    0x08
#define JAIL_SET_MASK (JAIL_CREATE | JAIL_UPDATE | JAIL_ATTACH | JAIL_DYING)
#define JAIL_GET_MASK (JAIL_DYING)
int jail(struct jail *jail);
int jail_set(struct iovec *iov, unsigned int niov, int flags);
int jail_get(struct iovec *iov, unsigned int niov, int flags);
int jail_attach(int jid);
int jail_remove(int jid);
