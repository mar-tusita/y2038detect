#pragma once
#include <sys/socket.h>
struct hostent {
    char  *h_name;
    char **h_aliases;
    int    h_addrtype;
    int    h_length;
    char **h_addr_list;
};
#define h_addr h_addr_list[0]
struct addrinfo {
    int              ai_flags;
    int              ai_family;
    int              ai_socktype;
    int              ai_protocol;
    socklen_t        ai_addrlen;
    struct sockaddr *ai_addr;
    char            *ai_canonname;
    struct addrinfo *ai_next;
};
#define AI_PASSIVE      0x0001
#define AI_CANONNAME    0x0002
#define AI_NUMERICHOST  0x0004
#define AI_NUMERICSERV  0x0008
#define AI_ALL          0x0100
#define AI_V4MAPPED     0x0800
#define NI_NUMERICHOST  1
#define NI_NUMERICSERV  2
#define NI_MAXHOST      1025
#define NI_MAXSERV      32
#define EAI_AGAIN       -3
#define EAI_BADFLAGS    -1
#define EAI_FAIL        -4
#define EAI_FAMILY      -6
#define EAI_MEMORY      -10
#define EAI_NONAME      -2
#define EAI_SERVICE     -8
#define EAI_SOCKTYPE    -7
struct protoent {
    char  *p_name;
    char **p_aliases;
    int    p_proto;
};
struct servent {
    char  *s_name;
    char **s_aliases;
    int    s_port;
    char  *s_proto;
};
struct hostent *gethostbyname(const char *name);
struct hostent *gethostbyaddr(const void *addr, socklen_t len, int type);
int             getaddrinfo(const char *node, const char *service,
                            const struct addrinfo *hints, struct addrinfo **res);
void            freeaddrinfo(struct addrinfo *res);
int             getnameinfo(const struct sockaddr *addr, socklen_t addrlen,
                            char *host, socklen_t hostlen,
                            char *serv, socklen_t servlen, int flags);
const char     *gai_strerror(int errcode);
struct protoent *getprotobyname(const char *name);
struct protoent *getprotobynumber(int proto);
struct servent  *getservbyname(const char *name, const char *proto);
struct servent  *getservbyport(int port, const char *proto);
