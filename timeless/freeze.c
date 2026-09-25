#define _GNU_SOURCE
#include <time.h>
#include <sys/time.h>
#include <stddef.h>

/* A timeless environment: every clock read returns the same instant. */
static const time_t T0 = 1000000000;   /* 2001-09-09T01:46:40Z */

int clock_gettime(clockid_t clk, struct timespec *tp) {
    if (tp) { tp->tv_sec = T0; tp->tv_nsec = 0; }
    return 0;
}
time_t time(time_t *t) { if (t) *t = T0; return T0; }
int gettimeofday(struct timeval *tv, void *tz) {
    if (tv) { tv->tv_sec = T0; tv->tv_usec = 0; }
    return 0;
}
