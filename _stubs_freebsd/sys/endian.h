#pragma once
#include <stdint.h>
/* Byte-swap primitives */
static __inline uint16_t __bswap16(uint16_t x) { return (uint16_t)((x >> 8) | (x << 8)); }
static __inline uint32_t __bswap32(uint32_t x) {
    return ((x >> 24) | ((x >> 8) & 0xff00) | ((x << 8) & 0xff0000) | (x << 24));
}
static __inline uint64_t __bswap64(uint64_t x) {
    return (((uint64_t)__bswap32((uint32_t)x) << 32) | __bswap32((uint32_t)(x >> 32)));
}
/* Host to big-endian */
#define htobe16(x) __bswap16(x)
#define htobe32(x) __bswap32(x)
#define htobe64(x) __bswap64(x)
/* Big-endian to host */
#define be16toh(x) __bswap16(x)
#define be32toh(x) __bswap32(x)
#define be64toh(x) __bswap64(x)
/* Host to little-endian (assuming little-endian host) */
#define htole16(x) ((uint16_t)(x))
#define htole32(x) ((uint32_t)(x))
#define htole64(x) ((uint64_t)(x))
/* Little-endian to host */
#define le16toh(x) ((uint16_t)(x))
#define le32toh(x) ((uint32_t)(x))
#define le64toh(x) ((uint64_t)(x))
/* Aliases */
#define bswap16(x) __bswap16(x)
#define bswap32(x) __bswap32(x)
#define bswap64(x) __bswap64(x)
