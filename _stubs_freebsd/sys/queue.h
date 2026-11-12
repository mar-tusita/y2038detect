#pragma once
/*
 * BSD queue macros — minimal stub for parsing purposes.
 * Covers SLIST, LIST, STAILQ, TAILQ.
 */

/* Singly-linked list */
#define SLIST_HEAD(name, type)  struct name { struct type *slh_first; }
#define SLIST_HEAD_INITIALIZER(head)  { NULL }
#define SLIST_ENTRY(type)       struct { struct type *sle_next; }
#define SLIST_INIT(head)        ((head)->slh_first = NULL)
#define SLIST_EMPTY(head)       ((head)->slh_first == NULL)
#define SLIST_FIRST(head)       ((head)->slh_first)
#define SLIST_NEXT(elm, field)  ((elm)->field.sle_next)
#define SLIST_FOREACH(var, head, field) \
    for ((var) = SLIST_FIRST((head)); (var); (var) = SLIST_NEXT((var), field))
#define SLIST_INSERT_HEAD(head, elm, field) do { \
    (elm)->field.sle_next = (head)->slh_first; \
    (head)->slh_first = (elm); \
} while (0)
#define SLIST_REMOVE_HEAD(head, field) do { \
    (head)->slh_first = (head)->slh_first->field.sle_next; \
} while (0)

/* Doubly-linked list */
#define LIST_HEAD(name, type)   struct name { struct type *lh_first; }
#define LIST_HEAD_INITIALIZER(head) { NULL }
#define LIST_ENTRY(type)        struct { struct type *le_next; struct type **le_prev; }
#define LIST_INIT(head)         ((head)->lh_first = NULL)
#define LIST_EMPTY(head)        ((head)->lh_first == NULL)
#define LIST_FIRST(head)        ((head)->lh_first)
#define LIST_NEXT(elm, field)   ((elm)->field.le_next)
#define LIST_FOREACH(var, head, field) \
    for ((var) = LIST_FIRST((head)); (var); (var) = LIST_NEXT((var), field))
#define LIST_INSERT_HEAD(head, elm, field) do { \
    if (((elm)->field.le_next = (head)->lh_first) != NULL) \
        (head)->lh_first->field.le_prev = &(elm)->field.le_next; \
    (head)->lh_first = (elm); \
    (elm)->field.le_prev = &(head)->lh_first; \
} while (0)
#define LIST_INSERT_BEFORE(listelm, elm, field) do { \
    (elm)->field.le_prev = (listelm)->field.le_prev; \
    (elm)->field.le_next = (listelm); \
    *(listelm)->field.le_prev = (elm); \
    (listelm)->field.le_prev = &(elm)->field.le_next; \
} while (0)
#define LIST_INSERT_AFTER(listelm, elm, field) do { \
    if (((elm)->field.le_next = (listelm)->field.le_next) != NULL) \
        (listelm)->field.le_next->field.le_prev = &(elm)->field.le_next; \
    (listelm)->field.le_next = (elm); \
    (elm)->field.le_prev = &(listelm)->field.le_next; \
} while (0)
#define LIST_REMOVE(elm, field) do { \
    if ((elm)->field.le_next != NULL) \
        (elm)->field.le_next->field.le_prev = (elm)->field.le_prev; \
    *(elm)->field.le_prev = (elm)->field.le_next; \
} while (0)

/* Singly-linked tail queue */
#define STAILQ_HEAD(name, type) struct name { struct type *stqh_first; struct type **stqh_last; }
#define STAILQ_HEAD_INITIALIZER(head) { NULL, &(head).stqh_first }
#define STAILQ_ENTRY(type)      struct { struct type *stqe_next; }
#define STAILQ_INIT(head) do { (head)->stqh_first = NULL; (head)->stqh_last = &(head)->stqh_first; } while (0)
#define STAILQ_EMPTY(head)      ((head)->stqh_first == NULL)
#define STAILQ_FIRST(head)      ((head)->stqh_first)
#define STAILQ_NEXT(elm, field) ((elm)->field.stqe_next)
#define STAILQ_FOREACH(var, head, field) \
    for ((var) = STAILQ_FIRST((head)); (var); (var) = STAILQ_NEXT((var), field))
#define STAILQ_INSERT_HEAD(head, elm, field) do { \
    if (((elm)->field.stqe_next = (head)->stqh_first) == NULL) \
        (head)->stqh_last = &(elm)->field.stqe_next; \
    (head)->stqh_first = (elm); \
} while (0)
#define STAILQ_INSERT_TAIL(head, elm, field) do { \
    (elm)->field.stqe_next = NULL; \
    *(head)->stqh_last = (elm); \
    (head)->stqh_last = &(elm)->field.stqe_next; \
} while (0)
#define STAILQ_REMOVE_HEAD(head, field) do { \
    if (((head)->stqh_first = (head)->stqh_first->field.stqe_next) == NULL) \
        (head)->stqh_last = &(head)->stqh_first; \
} while (0)

/* Doubly-linked tail queue */
#define TAILQ_HEAD(name, type)  struct name { struct type *tqh_first; struct type **tqh_last; }
#define TAILQ_HEAD_INITIALIZER(head) { NULL, &(head).tqh_first }
#define TAILQ_ENTRY(type)       struct { struct type *tqe_next; struct type **tqe_prev; }
#define TAILQ_INIT(head) do { (head)->tqh_first = NULL; (head)->tqh_last = &(head)->tqh_first; } while (0)
#define TAILQ_EMPTY(head)       ((head)->tqh_first == NULL)
#define TAILQ_FIRST(head)       ((head)->tqh_first)
#define TAILQ_NEXT(elm, field)  ((elm)->field.tqe_next)
#define TAILQ_LAST(head, headname) (*(((struct headname *)((head)->tqh_last))->tqh_last))
#define TAILQ_PREV(elm, headname, field) (*(((struct headname *)((elm)->field.tqe_prev))->tqh_last))
#define TAILQ_FOREACH(var, head, field) \
    for ((var) = TAILQ_FIRST((head)); (var); (var) = TAILQ_NEXT((var), field))
#define TAILQ_FOREACH_REVERSE(var, head, headname, field) \
    for ((var) = TAILQ_LAST((head), headname); (var); (var) = TAILQ_PREV((var), headname, field))
#define TAILQ_INSERT_HEAD(head, elm, field) do { \
    if (((elm)->field.tqe_next = (head)->tqh_first) != NULL) \
        (head)->tqh_first->field.tqe_prev = &(elm)->field.tqe_next; \
    else \
        (head)->tqh_last = &(elm)->field.tqe_next; \
    (head)->tqh_first = (elm); \
    (elm)->field.tqe_prev = &(head)->tqh_first; \
} while (0)
#define TAILQ_INSERT_TAIL(head, elm, field) do { \
    (elm)->field.tqe_next = NULL; \
    (elm)->field.tqe_prev = (head)->tqh_last; \
    *(head)->tqh_last = (elm); \
    (head)->tqh_last = &(elm)->field.tqe_next; \
} while (0)
#define TAILQ_INSERT_BEFORE(listelm, elm, field) do { \
    (elm)->field.tqe_prev = (listelm)->field.tqe_prev; \
    (elm)->field.tqe_next = (listelm); \
    *(listelm)->field.tqe_prev = (elm); \
    (listelm)->field.tqe_prev = &(elm)->field.tqe_next; \
} while (0)
#define TAILQ_INSERT_AFTER(head, listelm, elm, field) do { \
    if (((elm)->field.tqe_next = (listelm)->field.tqe_next) != NULL) \
        (elm)->field.tqe_next->field.tqe_prev = &(elm)->field.tqe_next; \
    else \
        (head)->tqh_last = &(elm)->field.tqe_next; \
    (listelm)->field.tqe_next = (elm); \
    (elm)->field.tqe_prev = &(listelm)->field.tqe_next; \
} while (0)
#define TAILQ_REMOVE(head, elm, field) do { \
    if (((elm)->field.tqe_next) != NULL) \
        (elm)->field.tqe_next->field.tqe_prev = (elm)->field.tqe_prev; \
    else \
        (head)->tqh_last = (elm)->field.tqe_prev; \
    *(elm)->field.tqe_prev = (elm)->field.tqe_next; \
} while (0)
