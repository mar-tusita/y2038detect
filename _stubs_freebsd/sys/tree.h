#pragma once
/*
 * BSD red-black tree macros — type and macro definitions only.
 * Full implementation omitted; provides enough for parsing.
 */
#define RB_HEAD(name, type)  struct name { struct type *rbh_root; }
#define RB_INITIALIZER(root) { NULL }
#define RB_ENTRY(type)       struct { struct type *rbe_left; struct type *rbe_right; struct type *rbe_parent; int rbe_color; }
#define RB_ROOT(head)        ((head)->rbh_root)
#define RB_EMPTY(head)       (RB_ROOT(head) == NULL)
#define RB_LEFT(elm, field)  ((elm)->field.rbe_left)
#define RB_RIGHT(elm, field) ((elm)->field.rbe_right)
#define RB_PARENT(elm, field)((elm)->field.rbe_parent)
#define RB_COLOR(elm, field) ((elm)->field.rbe_color)
#define RB_FOREACH(x, name, head) \
    for ((x) = name##_RB_MINMAX(head, -1); (x) != NULL; (x) = name##_RB_NEXT(x))
#define RB_FOREACH_REVERSE(x, name, head) \
    for ((x) = name##_RB_MINMAX(head, 1); (x) != NULL; (x) = name##_RB_PREV(x))
#define RB_FOREACH_SAFE(x, name, head, y) \
    for ((x) = name##_RB_MINMAX(head, -1); \
        ((x) != NULL) && ((y) = name##_RB_NEXT(x), 1); (x) = (y))
#define RB_GENERATE_STATIC(name, type, field, cmp) \
    RB_GENERATE(name, type, field, cmp)
#define RB_GENERATE(name, type, field, cmp) \
    static struct type *name##_RB_MINMAX(struct name *head, int val) { return NULL; } \
    static struct type *name##_RB_NEXT(struct type *elm) { return NULL; } \
    static struct type *name##_RB_PREV(struct type *elm) { return NULL; } \
    static struct type *name##_RB_INSERT(struct name *head, struct type *elm) { return NULL; } \
    static struct type *name##_RB_REMOVE(struct name *head, struct type *elm) { return NULL; } \
    static struct type *name##_RB_FIND(struct name *head, struct type *elm) { return NULL; } \
    static struct type *name##_RB_NFIND(struct name *head, struct type *elm) { return NULL; }
#define RB_PROTOTYPE(name, type, field, cmp)
#define RB_PROTOTYPE_STATIC(name, type, field, cmp)
