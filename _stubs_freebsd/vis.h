#pragma once
#include <stddef.h>
/* Flags for strvis/strunvis */
#define VIS_OCTAL   0x0001  /* use octal \ddd format */
#define VIS_CSTYLE  0x0002  /* use C \x format */
#define VIS_SP      0x0004  /* also encode space */
#define VIS_TAB     0x0008  /* also encode tab */
#define VIS_NL      0x0010  /* also encode newline */
#define VIS_WHITE   (VIS_SP | VIS_TAB | VIS_NL)
#define VIS_SAFE    0x0020  /* only encode "unsafe" characters */
#define VIS_NOBACKSLASH 0x0040
#define VIS_HTTPSTYLE 0x0080
#define VIS_GLOB    0x0100
#define VIS_NOSLASH 0x0200  /* don't decode NUL via \/ */
/* unvis return codes */
#define UNVIS_VALID      1
#define UNVIS_VALIDPUSH  2
#define UNVIS_NOCHAR     3
#define UNVIS_SYNBAD    -1
#define UNVIS_ERROR     -2
/* state for unvis */
#define UNVIS_END        1
char *vis(char *dst, int c, int flag, int nextc);
char *nvis(char *dst, size_t dlen, int c, int flag, int nextc);
int   strvis(char *dst, const char *src, int flag);
int   strnvis(char *dst, size_t dlen, const char *src, int flag);
int   strvisx(char *dst, const char *src, size_t len, int flag);
int   strnvisx(char *dst, size_t dlen, const char *src, size_t len, int flag);
int   strunvis(char *dst, const char *src);
int   strunvisx(char *dst, const char *src, int flag);
int   unvis(char *cp, int c, int *astate, int flag);
