#pragma once
#ifndef _PID_T_DECLARED
#define _PID_T_DECLARED
typedef int pid_t;
#endif
#define WNOHANG     1
#define WUNTRACED   2
#define WCONTINUED  8
#define WEXITED     4
#define WNOWAIT     0x01000000
#define WIFEXITED(s)    (((s) & 0177) == 0)
#define WIFSIGNALED(s)  (((s) & 0177) != 0 && ((s) & 0177) != 0177)
#define WIFSTOPPED(s)   (((s) & 0177) == 0177)
#define WEXITSTATUS(s)  (((s) >> 8) & 0xff)
#define WTERMSIG(s)     ((s) & 0177)
#define WSTOPSIG(s)     (((s) >> 8) & 0xff)
pid_t wait(int *);
pid_t waitpid(pid_t, int *, int);
