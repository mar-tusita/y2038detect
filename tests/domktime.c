#include <time.h>

static void adjhour(struct tm *t, char type, int h, int m);

static int
domktime(struct tm *t, char type)
{
  time_t ret;

  while ((ret = mktime(t)) == -1 && t->tm_year > 68 && t->tm_year < 138)
    /* While mktime() fails, adjust by an hour */
    adjhour(t, type == '-' ? type : '+', 1, 0);

  return ret;
}
