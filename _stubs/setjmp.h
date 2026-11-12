#pragma once
typedef long jmp_buf[64];
typedef long sigjmp_buf[128];

int  setjmp(jmp_buf);
void longjmp(jmp_buf, int);
int  sigsetjmp(sigjmp_buf, int);
void siglongjmp(sigjmp_buf, int);
