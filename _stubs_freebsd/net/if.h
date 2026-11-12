#pragma once
#include <sys/types.h>
#include <sys/socket.h>
#define IFNAMSIZ    16
#define IF_NAMESIZE 16
#define IF_MAXUNIT  0x7fff
struct ifreq {
    char ifr_name[IFNAMSIZ];
    union {
        struct sockaddr ifru_addr;
        struct sockaddr ifru_dstaddr;
        struct sockaddr ifru_broadaddr;
        short           ifru_flags[2];
        int             ifru_index;
        int             ifru_metric;
        int             ifru_mtu;
        int             ifru_phys;
        int             ifru_media;
        int             ifru_cap[2];
    } ifr_ifru;
};
#define ifr_addr        ifr_ifru.ifru_addr
#define ifr_dstaddr     ifr_ifru.ifru_dstaddr
#define ifr_broadaddr   ifr_ifru.ifru_broadaddr
#define ifr_flags       ifr_ifru.ifru_flags[0]
#define ifr_flagshigh   ifr_ifru.ifru_flags[1]
#define ifr_index       ifr_ifru.ifru_index
#define ifr_metric      ifr_ifru.ifru_metric
#define ifr_mtu         ifr_ifru.ifru_mtu
#define ifr_phys        ifr_ifru.ifru_phys
#define ifr_media       ifr_ifru.ifru_media
/* Interface flags */
#define IFF_UP          0x0001
#define IFF_BROADCAST   0x0002
#define IFF_DEBUG       0x0004
#define IFF_LOOPBACK    0x0008
#define IFF_POINTOPOINT 0x0010
#define IFF_SMART       0x0020
#define IFF_RUNNING     0x0040
#define IFF_NOARP       0x0080
#define IFF_PROMISC     0x0100
#define IFF_ALLMULTI    0x0200
#define IFF_OACTIVE     0x0400
#define IFF_SIMPLEX     0x0800
#define IFF_LINK0       0x1000
#define IFF_LINK1       0x2000
#define IFF_LINK2       0x4000
#define IFF_MULTICAST   0x8000
#define IFF_CANTCONFIG  0x10000
#define IFF_PPROMISC    0x20000
#define IFF_MONITOR     0x40000
#define IFF_STATICARP   0x80000
char        *if_indextoname(unsigned int ifindex, char *ifname);
unsigned int if_nametoindex(const char *ifname);
struct if_nameindex {
    unsigned int  if_index;
    char         *if_name;
};
struct if_nameindex *if_nameindex(void);
void         if_freenameindex(struct if_nameindex *ptr);
