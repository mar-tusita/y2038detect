#pragma once
#define TIOCGWINSZ 0x5413
#define TIOCSWINSZ 0x5414
#define TIOCGPGRP  0x540f
#define TIOCSPGRP  0x5410
#define FIONREAD   0x541b
#define FIONBIO    0x5421
struct winsize {
    unsigned short ws_row;
    unsigned short ws_col;
    unsigned short ws_xpixel;
    unsigned short ws_ypixel;
};
int ioctl(int fd, unsigned long request, ...);
