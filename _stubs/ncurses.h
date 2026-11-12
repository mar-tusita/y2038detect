#pragma once
#include <stdio.h>
#include <stdarg.h>

typedef unsigned long  chtype;
typedef unsigned long  attr_t;
typedef unsigned short mmask_t;

#ifndef bool
typedef unsigned char bool;
#define true  1
#define false 0
#endif

typedef struct _win_st WINDOW;
typedef struct screen  SCREEN;

extern WINDOW *stdscr;
extern WINDOW *curscr;
extern int     LINES;
extern int     COLS;

/* return values */
#define ERR  (-1)
#define OK   0

/* attributes */
#define A_NORMAL    0UL
#define A_BOLD      (1UL << 21)
#define A_REVERSE   (1UL << 18)
#define A_UNDERLINE (1UL << 17)
#define A_DIM       (1UL << 19)
#define A_BLINK     (1UL << 20)
#define A_STANDOUT  (1UL << 16)

/* colors */
#define COLOR_BLACK   0
#define COLOR_RED     1
#define COLOR_GREEN   2
#define COLOR_YELLOW  3
#define COLOR_BLUE    4
#define COLOR_MAGENTA 5
#define COLOR_CYAN    6
#define COLOR_WHITE   7

#define COLOR_PAIR(n) ((chtype)(n) << 8)
#define PAIR_NUMBER(a) (((a) >> 8) & 0xff)

/* key codes */
#define KEY_CODE_YES  0400
#define KEY_DOWN      0402
#define KEY_UP        0403
#define KEY_LEFT      0404
#define KEY_RIGHT     0405
#define KEY_BACKSPACE 0407
#define KEY_ENTER     0527
#define KEY_RESIZE    0632
#define KEY_MOUSE     0631
#define KEY_PPAGE     0523
#define KEY_NPAGE     0522
#define KEY_HOME      0406
#define KEY_END       0550
#define KEY_F(n)      (0410 + (n))
#define KEY_DC        0512
#define KEY_IC        0513
#define KEY_BTAB      0541

/* mouse */
#define BUTTON1_PRESSED       0000002L
#define BUTTON1_RELEASED      0000001L
#define BUTTON1_CLICKED       0000004L
#define BUTTON1_DOUBLE_CLICKED 0000010L
#define BUTTON4_PRESSED       0020000000L
#define BUTTON5_PRESSED       0200000000L
#define REPORT_MOUSE_POSITION 0400000000L
#define ALL_MOUSE_EVENTS      0777777777L

typedef struct {
    short id;
    int   x, y, z;
    mmask_t bstate;
} MEVENT;

/* initialization */
extern WINDOW *initscr(void);
extern int     endwin(void);
extern SCREEN *newterm(const char *, FILE *, FILE *);
extern SCREEN *set_term(SCREEN *);
extern void    delscreen(SCREEN *);
extern bool    isendwin(void);

/* window management */
extern WINDOW *newwin(int, int, int, int);
extern int     delwin(WINDOW *);
extern WINDOW *subwin(WINDOW *, int, int, int, int);
extern WINDOW *derwin(WINDOW *, int, int, int, int);
extern int     mvwin(WINDOW *, int, int);
extern int     wresize(WINDOW *, int, int);

/* output */
extern int  refresh(void);
extern int  wrefresh(WINDOW *);
extern int  wnoutrefresh(WINDOW *);
extern int  doupdate(void);
extern int  addch(chtype);
extern int  waddch(WINDOW *, chtype);
extern int  mvaddch(int, int, chtype);
extern int  mvwaddch(WINDOW *, int, int, chtype);
extern int  printw(const char *, ...);
extern int  wprintw(WINDOW *, const char *, ...);
extern int  mvprintw(int, int, const char *, ...);
extern int  mvwprintw(WINDOW *, int, int, const char *, ...);
extern int  addstr(const char *);
extern int  waddstr(WINDOW *, const char *);
extern int  mvaddstr(int, int, const char *);
extern int  mvwaddstr(WINDOW *, int, int, const char *);
extern int  addnstr(const char *, int);
extern int  waddnstr(WINDOW *, const char *, int);

/* input */
extern int  getch(void);
extern int  wgetch(WINDOW *);
extern int  ungetch(int);
extern int  getstr(char *);
extern int  wgetstr(WINDOW *, char *);

/* cursor movement */
extern int  move(int, int);
extern int  wmove(WINDOW *, int, int);

/* attributes */
extern int  attron(int);
extern int  attroff(int);
extern int  attrset(int);
extern int  wattron(WINDOW *, int);
extern int  wattroff(WINDOW *, int);
extern int  wattrset(WINDOW *, int);

/* color */
extern int  start_color(void);
extern int  init_pair(short, short, short);
extern bool has_colors(void);
extern bool can_change_color(void);

/* clear */
extern int  clear(void);
extern int  wclear(WINDOW *);
extern int  erase(void);
extern int  werase(WINDOW *);
extern int  clrtoeol(void);
extern int  wclrtoeol(WINDOW *);
extern int  clrtobot(void);
extern int  wclrtobot(WINDOW *);

/* settings */
extern int  noecho(void);
extern int  echo(void);
extern int  cbreak(void);
extern int  nocbreak(void);
extern int  raw(void);
extern int  noraw(void);
extern int  nl(void);
extern int  nonl(void);
extern int  nodelay(WINDOW *, bool);
extern int  keypad(WINDOW *, bool);
extern int  scrollok(WINDOW *, bool);
extern int  idlok(WINDOW *, bool);
extern int  halfdelay(int);
extern int  timeout(int);
extern int  wtimeout(WINDOW *, int);
extern int  curs_set(int);
extern int  use_default_colors(void);

/* box / border */
extern int  box(WINDOW *, chtype, chtype);
extern int  wborder(WINDOW *, chtype, chtype, chtype, chtype,
                    chtype, chtype, chtype, chtype);
extern int  hline(chtype, int);
extern int  vline(chtype, int);
extern int  whline(WINDOW *, chtype, int);
extern int  wvline(WINDOW *, chtype, int);
extern int  mvhline(int, int, chtype, int);
extern int  mvvline(int, int, chtype, int);
extern int  mvwhline(WINDOW *, int, int, chtype, int);
extern int  mvwvline(WINDOW *, int, int, chtype, int);

/* dimensions */
extern int  getmaxy(WINDOW *);
extern int  getmaxx(WINDOW *);
extern int  getbegy(WINDOW *);
extern int  getbegx(WINDOW *);
#define getmaxyx(w, y, x)  ((y) = getmaxy(w), (x) = getmaxx(w))
#define getbegyx(w, y, x)  ((y) = getbegy(w), (x) = getbegx(w))
#define getcuryx(w, y, x)  ((y) = getcury(w), (x) = getcurx(w))
extern int  getcury(WINDOW *);
extern int  getcurx(WINDOW *);

/* mouse */
extern int      mousemask(mmask_t, mmask_t *);
extern int      getmouse(MEVENT *);
extern int      ungetmouse(MEVENT *);
extern bool     wenclose(const WINDOW *, int, int);

/* misc */
extern char    *unctrl(chtype);
extern int      beep(void);
extern int      flash(void);
extern chtype   ACS_HLINE;
extern chtype   ACS_VLINE;
extern chtype   ACS_ULCORNER;
extern chtype   ACS_URCORNER;
extern chtype   ACS_LLCORNER;
extern chtype   ACS_LRCORNER;
extern chtype   ACS_PLUS;
extern chtype   ACS_LTEE;
extern chtype   ACS_RTEE;
extern chtype   ACS_TTEE;
extern chtype   ACS_BTEE;
