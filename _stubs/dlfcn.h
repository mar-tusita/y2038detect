#pragma once
#define RTLD_LAZY   1
#define RTLD_NOW    2
#define RTLD_GLOBAL 0x100
#define RTLD_LOCAL  0
void  *dlopen(const char *, int);
void  *dlsym(void *, const char *);
int    dlclose(void *);
char  *dlerror(void);
