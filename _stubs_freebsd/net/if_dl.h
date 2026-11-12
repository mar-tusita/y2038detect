#pragma once
#include <sys/types.h>
struct sockaddr_dl {
    unsigned char  sdl_len;
    unsigned char  sdl_family;
    unsigned short sdl_index;
    unsigned char  sdl_type;
    unsigned char  sdl_nlen;
    unsigned char  sdl_alen;
    unsigned char  sdl_slen;
    char           sdl_data[46];
};
#define LLADDR(s)       ((char *)((s)->sdl_data + (s)->sdl_nlen))
#define LLADDR_CONST(s) ((const char *)((s)->sdl_data + (s)->sdl_nlen))
