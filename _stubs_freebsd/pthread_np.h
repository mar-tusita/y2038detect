#pragma once
#include <pthread.h>
int   pthread_getthreadid_np(void);
void  pthread_set_name_np(pthread_t tid, const char *name);
void  pthread_get_name_np(pthread_t tid, char *name, size_t len);
int   pthread_setaffinity_np(pthread_t tid, size_t cpusetsize, const void *cpuset);
int   pthread_getaffinity_np(pthread_t tid, size_t cpusetsize, void *cpuset);
int   pthread_attr_setaffinity_np(pthread_attr_t *attr, size_t cpusetsize, const void *cpuset);
int   pthread_attr_getaffinity_np(const pthread_attr_t *attr, size_t cpusetsize, void *cpuset);
int   pthread_main_np(void);
int   pthread_stackseg_np(pthread_t thread, void *sinfo);
int   pthread_suspend_np(pthread_t thread);
int   pthread_resume_np(pthread_t thread);
