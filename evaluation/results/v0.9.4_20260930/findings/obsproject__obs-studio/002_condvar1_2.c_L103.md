# obsproject/obs-studio — deps/w32-pthreads/tests/condvar1_2.c:103

| 項目 | 値 |
|------|----|
| リポジトリ | [obsproject/obs-studio](https://github.com/obsproject/obs-studio) |
| ファイル | [`deps/w32-pthreads/tests/condvar1_2.c`](https://github.com/obsproject/obs-studio/blob/686ee75a0575b5772d54ccba6b0e8ba67ed7b5b7/deps/w32-pthreads/tests/condvar1_2.c#L103) |
| 行 | 103 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:04:21Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
    97        for (i = 0; i < NUM_CV; i++)
    98          {
    99            assert(pthread_cond_init(&cv[i], NULL) == 0);
   100          }
   101  
   102        j = NUM_CV;
>  103        (void) srand((unsigned)time(NULL));
   104  
   105        /* Traverse the list asynchronously. */
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)は単純な乱数の種として使われるだけで、時刻を考慮していない。

またsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
