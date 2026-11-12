# valkey-io/valkey — src/util.c:1110

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/util.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/util.c#L1110) |
| 行 | 1110 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned char' may truncate after 2038
```

## コード

```c
  1104          /* Revert to a weaker seed, and in this case reseed again
  1105           * at every call.*/
  1106          for (unsigned int j = 0; j < sizeof(seed); j++) {
  1107              struct timeval tv;
  1108              gettimeofday(&tv, NULL);
  1109              pid_t pid = getpid();
> 1110              seed[j] = tv.tv_sec ^ tv.tv_usec ^ pid ^ (long)fp;
  1111          }
  1112      } else {
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: seed[]は乱数として使われるだけで、時刻を考慮していない。
