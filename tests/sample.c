#include <time.h>
#include <stdint.h>

/* ---- should be flagged ---- */

void bad_implicit(void)
{
    int       t1 = time(NULL);   /* time_t -> int   (implicit) */
    long      t2 = time(NULL);   /* time_t -> long  (32-bit on Windows) */
    int32_t   t3 = time(NULL);   /* time_t -> int32_t (implicit) */
    uint32_t  t4 = time(NULL);   /* time_t -> uint32_t (implicit) */

    time_t now = time(NULL);
    int    t5  = now;            /* time_t variable -> int (implicit) */
}

void bad_explicit(void)
{
    time_t now = time(NULL);
    int t1 = (int)now;           /* time_t -> int (explicit cast) */
    int t2 = (int)time(NULL);    /* time_t -> int (explicit cast) */
}

/* ---- should NOT be flagged ---- */

void good_examples(void)
{
    time_t    t1 = time(NULL);   /* time_t -> time_t */
    int64_t   t2 = time(NULL);   /* time_t -> int64_t  (64-bit) */
    long long t3 = time(NULL);   /* time_t -> long long (64-bit) */

    time_t now = time(NULL);
    time_t t4  = now;
}
