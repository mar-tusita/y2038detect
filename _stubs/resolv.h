#pragma once
#include <netinet/in.h>
int  res_init(void);
int  res_query(const char *dname, int class, int type, unsigned char *answer, int anslen);
int  res_search(const char *dname, int class, int type, unsigned char *answer, int anslen);
int  dn_expand(const unsigned char *msg, const unsigned char *eomorig,
               const unsigned char *comp_dn, char *exp_dn, int length);
int  dn_comp(const char *exp_dn, unsigned char *comp_dn, int length,
             unsigned char **dnptrs, unsigned char **lastdnptr);
