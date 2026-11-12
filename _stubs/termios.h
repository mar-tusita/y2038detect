#pragma once
typedef unsigned int  tcflag_t;
typedef unsigned char cc_t;
typedef unsigned int  speed_t;
#define NCCS 20
struct termios {
    tcflag_t c_iflag;
    tcflag_t c_oflag;
    tcflag_t c_cflag;
    tcflag_t c_lflag;
    cc_t     c_cc[NCCS];
};
/* c_iflag */
#define IGNBRK  0000001
#define BRKINT  0000002
#define INPCK   0000020
#define ISTRIP  0000040
#define IXON    0002000
#define IXOFF   0010000
#define IXANY   0004000
/* c_oflag */
#define OPOST   0000001
/* c_cflag */
#define CSIZE   0000060
#define CS5     0000000
#define CS6     0000020
#define CS7     0000040
#define CS8     0000060
#define CSTOPB  0000100
#define CREAD   0000200
#define PARENB  0000400
#define HUPCL   0002000
#define CLOCAL  0004000
/* c_lflag */
#define ISIG    0000001
#define ICANON  0000002
#define ECHO    0000010
#define ECHOE   0000020
#define ECHOK   0000040
#define ECHONL  0000100
#define NOFLSH  0000200
#define TOSTOP  0000400
#define IEXTEN  0100000
/* c_cc indices */
#define VEOF    4
#define VEOL    11
#define VERASE  2
#define VINTR   0
#define VKILL   3
#define VMIN    6
#define VQUIT   1
#define VSTART  8
#define VSTOP   9
#define VSUSP   10
#define VTIME   5
/* tcsetattr actions */
#define TCSANOW    0
#define TCSADRAIN  1
#define TCSAFLUSH  2
/* tcflush queues */
#define TCIFLUSH   0
#define TCOFLUSH   1
#define TCIOFLUSH  2
/* baud rates */
#define B0      0000000
#define B50     0000001
#define B110    0000003
#define B300    0000005
#define B1200   0000011
#define B2400   0000013
#define B4800   0000014
#define B9600   0000015
#define B19200  0000016
#define B38400  0000017
int     tcgetattr(int fd, struct termios *t);
int     tcsetattr(int fd, int action, const struct termios *t);
int     tcdrain(int fd);
int     tcflush(int fd, int queue);
int     tcflow(int fd, int action);
speed_t cfgetispeed(const struct termios *t);
speed_t cfgetospeed(const struct termios *t);
int     cfsetispeed(struct termios *t, speed_t speed);
int     cfsetospeed(struct termios *t, speed_t speed);
