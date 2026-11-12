#pragma once
#ifndef NAN
#define NAN (__builtin_nanf(""))
#endif
#ifndef INFINITY
#define INFINITY (__builtin_inff())
#endif
#define isnan(x)    __builtin_isnan(x)
#define isinf(x)    __builtin_isinf(x)
#define isnormal(x) __builtin_isnormal(x)
double sqrt(double);
double fabs(double);
double floor(double);
double ceil(double);
double pow(double, double);
double log(double);
double log10(double);
double log2(double);
double exp(double);
double sin(double);
double cos(double);
double tan(double);
double atan2(double, double);
double fmod(double, double);
double modf(double, double *);
float  sqrtf(float);
float  fabsf(float);
float  floorf(float);
float  ceilf(float);
