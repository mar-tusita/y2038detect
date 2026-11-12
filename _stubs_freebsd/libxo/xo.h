#pragma once
#include <stddef.h>
#include <stdarg.h>
/* Opaque handle */
typedef struct xo_handle_s xo_handle_t;
/* XO flags */
#define XOF_COLOR       (1<<0)
#define XOF_COLOR_ALLOWED (1<<1)
#define XOF_CLOSE_FP    (1<<2)
#define XOF_DTRT        (1<<3)
#define XOF_FLUSH       (1<<4)
#define XOF_FLUSH_LINE  (1<<5)
#define XOF_INFO        (1<<6)
#define XOF_KEYS        (1<<7)
#define XOF_LOG_GETTEXT (1<<8)
#define XOF_LOG_SYSLOG  (1<<9)
#define XOF_NO_ENV      (1<<10)
#define XOF_NO_HUMANIZE (1<<11)
#define XOF_PRETTY      (1<<12)
#define XOF_RETAIN_ALL  (1<<13)
#define XOF_RETAIN_NONE (1<<14)
#define XOF_UNDERSCORES (1<<15)
#define XOF_UNITS       (1<<16)
#define XOF_WARN        (1<<17)
#define XOF_WARN_XML    (1<<18)
#define XOF_XPATH       (1<<19)
/* Output styles */
typedef enum { XO_STYLE_TEXT, XO_STYLE_XML, XO_STYLE_JSON, XO_STYLE_HTML, XO_STYLE_SDPARAMS } xo_style_t;
/* Global API */
xo_handle_t *xo_create(xo_style_t style, unsigned flags);
xo_handle_t *xo_create_to_file(FILE *fp, xo_style_t style, unsigned flags);
void         xo_destroy(xo_handle_t *xop);
int          xo_finish(void);
int          xo_finish_h(xo_handle_t *xop);
void         xo_flush(void);
void         xo_flush_h(xo_handle_t *xop);
void         xo_set_flags(xo_handle_t *xop, unsigned flags);
unsigned     xo_get_flags(xo_handle_t *xop);
void         xo_clear_flags(xo_handle_t *xop, unsigned flags);
void         xo_set_style(xo_handle_t *xop, xo_style_t style);
xo_style_t   xo_get_style(xo_handle_t *xop);
int          xo_set_style_name(xo_handle_t *xop, const char *name);
/* Emit */
int xo_emit(const char *fmt, ...);
int xo_emit_h(xo_handle_t *xop, const char *fmt, ...);
int xo_emit_hv(xo_handle_t *xop, const char *fmt, va_list vap);
/* Containers and lists */
int xo_open_container(const char *name);
int xo_open_container_h(xo_handle_t *xop, const char *name);
int xo_close_container(const char *name);
int xo_close_container_h(xo_handle_t *xop, const char *name);
int xo_open_list(const char *name);
int xo_open_list_h(xo_handle_t *xop, const char *name);
int xo_close_list(const char *name);
int xo_close_list_h(xo_handle_t *xop, const char *name);
int xo_open_instance(const char *name);
int xo_open_instance_h(xo_handle_t *xop, const char *name);
int xo_close_instance(const char *name);
int xo_close_instance_h(xo_handle_t *xop, const char *name);
/* Error reporting */
void xo_warn(const char *fmt, ...);
void xo_warn_c(int code, const char *fmt, ...);
void xo_warnx(const char *fmt, ...);
void xo_err(int eval, const char *fmt, ...);
void xo_errc(int eval, int code, const char *fmt, ...);
void xo_errx(int eval, const char *fmt, ...);
void xo_message(const char *fmt, ...);
void xo_message_c(int code, const char *fmt, ...);
/* Argument parsing */
int  xo_parse_args(int argc, char **argv);
void xo_set_program(const char *name);
void xo_set_version(const char *version);
