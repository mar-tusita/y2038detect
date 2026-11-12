/* minimal vary.h stub for y2038detect testing */
struct vary {
    char        *arg;
    struct vary *next;
};
struct vary       *vary_append(struct vary *, char *);
const struct vary *vary_apply(const struct vary *, struct tm *);
void               vary_destroy(struct vary *);
