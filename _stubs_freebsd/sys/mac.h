#pragma once
#include <sys/types.h>
/* Opaque MAC label handle */
typedef struct mac *mac_t;
/* Label operations */
int  mac_prepare(mac_t *label, const char *elements);
int  mac_prepare_file_label(mac_t *label);
int  mac_prepare_ifnet_label(mac_t *label);
int  mac_prepare_process_label(mac_t *label);
int  mac_prepare_type(mac_t *label, const char *name);
void mac_free(mac_t label);
/* Retrieve labels */
int  mac_get_fd(int fd, mac_t label);
int  mac_get_file(const char *path, mac_t label);
int  mac_get_link(const char *path, mac_t label);
int  mac_get_peer(int fd, mac_t label);
int  mac_get_pid(pid_t pid, mac_t label);
int  mac_get_proc(mac_t label);
/* Set labels */
int  mac_set_fd(int fd, const mac_t label);
int  mac_set_file(const char *path, const mac_t label);
int  mac_set_link(const char *path, const mac_t label);
int  mac_set_proc(const mac_t label);
/* Text conversion */
int  mac_from_text(mac_t *label, const char *text);
int  mac_to_text(mac_t label, char **text);
/* System information */
int  mac_is_present(const char *policyname);
