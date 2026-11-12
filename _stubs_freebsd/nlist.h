#pragma once
#include <stdint.h>
/* BSD kernel symbol name list */
struct nlist {
    union {
        char       *n_name;
        long        n_strx;
    } n_un;
    unsigned char  n_type;
    char           n_other;
    short          n_desc;
    unsigned long  n_value;
};
#define N_UNDF  0x00
#define N_ABS   0x02
#define N_TEXT  0x04
#define N_DATA  0x06
#define N_BSS   0x08
#define N_EXT   0x01
int nlist(const char *filename, struct nlist *nl);
