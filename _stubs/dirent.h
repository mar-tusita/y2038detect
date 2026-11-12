#pragma once
typedef struct _DIR DIR;
struct dirent {
    unsigned long long d_ino;
    unsigned short     d_reclen;
    unsigned char      d_type;
    char               d_name[256];
};
#define DT_UNKNOWN  0
#define DT_REG      8
#define DT_DIR      4
#define DT_LNK     10
DIR           *opendir(const char *);
struct dirent *readdir(DIR *);
int            closedir(DIR *);
int            scandir(const char *, struct dirent ***, void *, void *);
