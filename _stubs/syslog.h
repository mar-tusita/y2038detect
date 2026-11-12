#pragma once
#define LOG_AUTH    (4<<3)
#define LOG_NOTICE  5
void openlog(const char *, int, int);
void syslog(int, const char *, ...);
void closelog(void);
