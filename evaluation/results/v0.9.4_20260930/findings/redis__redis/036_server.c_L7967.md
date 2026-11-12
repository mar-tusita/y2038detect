# redis/redis — src/server.c:7967

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`src/server.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/src/server.c#L7967) |
| 行 | 7967 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
  7961      tzset(); /* Populates 'timezone' global. */
  7962      zmalloc_set_oom_handler(redisOutOfMemoryHandler);
  7963  
  7964      /* To achieve entropy, in case of containers, their time() and getpid() can
  7965       * be the same. But value of tv_usec is fast enough to make the difference */
  7966      gettimeofday(&tv,NULL);
> 7967      srand(time(NULL)^getpid()^tv.tv_usec);
  7968      srandom(time(NULL)^getpid()^tv.tv_usec);
  7969      init_genrand64(((long long) tv.tv_sec * 1000000 + tv.tv_usec) ^ getpid());
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)は単純な乱数の種として使われるだけで、時刻を考慮していない。

またsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
