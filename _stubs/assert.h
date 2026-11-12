#pragma once
/* Evaluate expr for side effects; never abort in stub context. */
#define assert(expr) ((void)(expr))
