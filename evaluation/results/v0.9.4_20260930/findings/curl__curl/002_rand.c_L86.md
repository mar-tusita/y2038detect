# curl/curl — lib/rand.c:86

| 項目 | 値 |
|------|----|
| リポジトリ | [curl/curl](https://github.com/curl/curl) |
| ファイル | [`lib/rand.c`](https://github.com/curl/curl/blob/872c313d7647ac437c83128e6bea7a8ed16cd2ef/lib/rand.c#L86) |
| 行 | 86 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:27:25Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
    80      static unsigned int randseed;
    81      static bool seeded = FALSE;
    82      unsigned int rnd;
    83      if(!seeded) {
    84        struct curltime now;
    85        curlx_pnow(&now);
>   86        randseed += (unsigned int)now.tv_usec + (unsigned int)now.tv_sec;
    87        randseed = randseed * 1103515245 + 12345;
    88        randseed = randseed * 1103515245 + 12345;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: randseedは乱数として使われるだけで、時刻を考慮していない。
