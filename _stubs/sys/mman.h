#pragma once
#include <stddef.h>
#define PROT_NONE   0
#define PROT_READ   1
#define PROT_WRITE  2
#define PROT_EXEC   4
#define MAP_SHARED  1
#define MAP_PRIVATE 2
#define MAP_FAILED  ((void *)-1)
#define MAP_ANON      0x20
#define MAP_ANONYMOUS MAP_ANON
#define MAP_FIXED     0x10
#define MAP_POPULATE  0x08000
#define MREMAP_MAYMOVE 1
#define MREMAP_FIXED   2
void *mmap(void *, size_t, int, int, int, long);
void *mremap(void *, size_t, size_t, int, ...);
int   munmap(void *, size_t);
int   mprotect(void *, size_t, int);
int   msync(void *, size_t, int);
int   mlock(const void *, size_t);
int   munlock(const void *, size_t);
