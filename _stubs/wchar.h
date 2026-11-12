#pragma once
#include <stddef.h>
#ifndef _WCHAR_T_DECLARED
#define _WCHAR_T_DECLARED
typedef __WCHAR_TYPE__ wchar_t;
#endif
typedef unsigned int wint_t;
size_t   wcslen(const wchar_t *);
wchar_t *wcscpy(wchar_t *, const wchar_t *);
wchar_t *wcsncpy(wchar_t *, const wchar_t *, size_t);
wchar_t *wcscat(wchar_t *, const wchar_t *);
int      wcscmp(const wchar_t *, const wchar_t *);
int      wcsncmp(const wchar_t *, const wchar_t *, size_t);
int      wprintf(const wchar_t *, ...);
int      fwprintf(void *, const wchar_t *, ...);
