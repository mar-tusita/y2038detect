#pragma once
#include <sys/socket.h>
struct ifaddrs {
    struct ifaddrs  *ifa_next;
    char            *ifa_name;
    unsigned int     ifa_flags;
    struct sockaddr *ifa_addr;
    struct sockaddr *ifa_netmask;
    struct sockaddr *ifa_dstaddr;
    void            *ifa_data;
};
#define ifa_broadaddr ifa_dstaddr
int  getifaddrs(struct ifaddrs **ifap);
void freeifaddrs(struct ifaddrs *ifa);
