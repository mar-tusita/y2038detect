#pragma once
struct option {
    const char *name;
    int         has_arg;
    int        *flag;
    int         val;
};
#define no_argument       0
#define required_argument 1
#define optional_argument 2
int getopt_long(int, char * const [], const char *,
                const struct option *, int *);
int getopt_long_only(int, char * const [], const char *,
                     const struct option *, int *);
