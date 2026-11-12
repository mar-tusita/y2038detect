#pragma once
#include <stddef.h>
/* C11 atomic types — _Atomic qualifier is built in to Clang */
typedef _Atomic _Bool              atomic_bool;
typedef _Atomic char               atomic_char;
typedef _Atomic unsigned char      atomic_uchar;
typedef _Atomic short              atomic_short;
typedef _Atomic unsigned short     atomic_ushort;
typedef _Atomic int                atomic_int;
typedef _Atomic unsigned int       atomic_uint;
typedef _Atomic long               atomic_long;
typedef _Atomic unsigned long      atomic_ulong;
typedef _Atomic long long          atomic_llong;
typedef _Atomic unsigned long long atomic_ullong;
typedef _Atomic size_t             atomic_size_t;
typedef enum {
    memory_order_relaxed = 0,
    memory_order_consume = 1,
    memory_order_acquire = 2,
    memory_order_release = 3,
    memory_order_acq_rel = 4,
    memory_order_seq_cst = 5
} memory_order;
#define ATOMIC_BOOL_LOCK_FREE     2
#define ATOMIC_CHAR_LOCK_FREE     2
#define ATOMIC_SHORT_LOCK_FREE    2
#define ATOMIC_INT_LOCK_FREE      2
#define ATOMIC_LONG_LOCK_FREE     2
#define ATOMIC_LLONG_LOCK_FREE    2
#define ATOMIC_POINTER_LOCK_FREE  2
#define atomic_init(obj, val)        ((void)(*(obj) = (val)))
#define atomic_load(obj)             (*(obj))
#define atomic_store(obj, val)       ((void)(*(obj) = (val)))
#define atomic_load_explicit(obj, order)            atomic_load(obj)
#define atomic_store_explicit(obj, val, order)      atomic_store(obj, val)
#define atomic_fetch_add(obj, arg)  __atomic_fetch_add(obj, arg, __ATOMIC_SEQ_CST)
#define atomic_fetch_sub(obj, arg)  __atomic_fetch_sub(obj, arg, __ATOMIC_SEQ_CST)
#define atomic_fetch_or(obj, arg)   __atomic_fetch_or(obj, arg, __ATOMIC_SEQ_CST)
#define atomic_fetch_and(obj, arg)  __atomic_fetch_and(obj, arg, __ATOMIC_SEQ_CST)
#define atomic_fetch_xor(obj, arg)  __atomic_fetch_xor(obj, arg, __ATOMIC_SEQ_CST)
#define atomic_fetch_add_explicit(obj, arg, order)  atomic_fetch_add(obj, arg)
#define atomic_fetch_sub_explicit(obj, arg, order)  atomic_fetch_sub(obj, arg)
#define atomic_fetch_or_explicit(obj, arg, order)   atomic_fetch_or(obj, arg)
#define atomic_fetch_and_explicit(obj, arg, order)  atomic_fetch_and(obj, arg)
#define atomic_compare_exchange_strong(obj, exp, des) \
    __atomic_compare_exchange_n(obj, exp, des, 0, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST)
#define atomic_compare_exchange_weak(obj, exp, des) \
    __atomic_compare_exchange_n(obj, exp, des, 1, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST)
#define atomic_compare_exchange_strong_explicit(obj, exp, des, s, f) \
    atomic_compare_exchange_strong(obj, exp, des)
#define atomic_compare_exchange_weak_explicit(obj, exp, des, s, f) \
    atomic_compare_exchange_weak(obj, exp, des)
#define atomic_exchange(obj, val)   __atomic_exchange_n(obj, val, __ATOMIC_SEQ_CST)
#define atomic_exchange_explicit(obj, val, order)   atomic_exchange(obj, val)
#define atomic_thread_fence(order)  __atomic_thread_fence(__ATOMIC_SEQ_CST)
#define atomic_signal_fence(order)  __atomic_signal_fence(__ATOMIC_SEQ_CST)
#define atomic_is_lock_free(obj)    __atomic_is_lock_free(sizeof(*(obj)), obj)
