#pragma once
#include <stdarg.h>
#include <stddef.h>
#include <sys/types.h>
#ifndef FILENAME_MAX
#define FILENAME_MAX 4096
#endif
#ifndef EOF
#define EOF (-1)
#endif
#ifndef SEEK_SET
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#endif
typedef struct _FILE FILE;
extern FILE *stdin;
extern FILE *stdout;
extern FILE *stderr;
int  printf(const char *, ...);
int  fprintf(FILE *, const char *, ...);
int  sprintf(char *, const char *, ...);
int  snprintf(char *, size_t, const char *, ...);
int  dprintf(int, const char *, ...);
int  sscanf(const char *, const char *, ...);
int  fflush(FILE *);
int  putchar(int);
int  puts(const char *);
int  vfprintf(FILE *, const char *, va_list);
int  vsnprintf(char *, size_t, const char *, va_list);
FILE  *fopen(const char *, const char *);
FILE  *fdopen(int, const char *);
int    fclose(FILE *);
size_t fread(void *, size_t, size_t, FILE *);
size_t fwrite(const void *, size_t, size_t, FILE *);
char  *fgets(char *, int, FILE *);
int    getc(FILE *);
int    fseek(FILE *, long, int);
int    fseeko(FILE *, off_t, int);
long   ftell(FILE *);
off_t  ftello(FILE *);
int    feof(FILE *);
int    ferror(FILE *);
void   clearerr(FILE *);
int    fileno(FILE *);
void   perror(const char *);
