#pragma once
#define FNM_PATHNAME (1 << 0)
#define FNM_NOESCAPE (1 << 1)
#define FNM_PERIOD   (1 << 2)
#define FNM_NOMATCH  1
int fnmatch(const char *pattern, const char *string, int flags);
