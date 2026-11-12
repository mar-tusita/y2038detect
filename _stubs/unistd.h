#pragma once
#include <stddef.h>
#include <sys/types.h>

/* Standard I/O */
ssize_t read(int, void *, size_t);
ssize_t write(int, const void *, size_t);
ssize_t pread(int, void *, size_t, off_t);
ssize_t pwrite(int, const void *, size_t, off_t);
int     close(int);
int     dup(int);
int     dup2(int, int);
int     pipe(int[2]);
int     fsync(int);
int     fdatasync(int);
int     isatty(int);
char   *ttyname(int);
off_t   lseek(int, off_t, int);
int     ftruncate(int, off_t);
int     truncate(const char *, off_t);

/* File system */
int     access(const char *, int);
int     unlink(const char *);
int     rmdir(const char *);
int     chdir(const char *);
char   *getcwd(char *, size_t);
int     link(const char *, const char *);
int     symlink(const char *, const char *);
ssize_t readlink(const char *, char *, size_t);
int     chown(const char *, uid_t, gid_t);
int     fchown(int, uid_t, gid_t);
int     fchmod(int, mode_t);

/* Process */
pid_t   getpid(void);
pid_t   getppid(void);
pid_t   fork(void);
int     execv(const char *, char * const []);
int     execvp(const char *, char * const []);
int     execve(const char *, char * const [], char * const []);
void    _exit(int);

/* User/group */
uid_t   getuid(void);
uid_t   geteuid(void);
gid_t   getgid(void);
gid_t   getegid(void);
int     setuid(uid_t);
int     setgid(gid_t);

/* Misc */
unsigned int sleep(unsigned int);
int          usleep(unsigned int);
long         sysconf(int);
long         pathconf(const char *, int);
/* sysconf() name constants */
#define _SC_PAGESIZE        30
#define _SC_PAGE_SIZE       _SC_PAGESIZE
#define _SC_NPROCESSORS_ONLN 84
#define _SC_NPROCESSORS_CONF 83
#define _SC_OPEN_MAX        4
#define _SC_CLK_TCK         2
int          setenv(const char *, const char *, int);
int          unsetenv(const char *);
char        *getlogin(void);
int          gethostname(char *, size_t);

/* getopt */
int   getopt(int, char * const [], const char *);
extern char *optarg;
extern int   optind;
extern int   opterr;
extern int   optopt;

/* Standard file descriptors */
#ifndef STDIN_FILENO
#define STDIN_FILENO  0
#define STDOUT_FILENO 1
#define STDERR_FILENO 2
#endif

/* seek constants (commonly needed) */
#ifndef SEEK_SET
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#endif

/* access() mode flags */
#ifndef F_OK
#define F_OK 0
#define X_OK 1
#define W_OK 2
#define R_OK 4
#endif
