# valkey-io/valkey — src/server.c:6604

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/server.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/server.c#L6604) |
| 行 | 6604 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
  6598                  double perc = 0;
  6599                  if (repl_transfer_size_stat) {
  6600                      perc = ((double)repl_transfer_read_stat / repl_transfer_size_stat) * 100;
  6601                  }
  6602                  info = sdscatprintf(
  6603                      info,
> 6604                      FMTARGS(
  6605                          "master_sync_total_bytes:%lld\r\n", (long long)repl_transfer_size_stat,
  6606                          "master_sync_read_bytes:%lld\r\n", (long long)repl_transfer_read_stat,
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
(server.unixtime - server.repl_transfer_lastio)を出力する際、intへのキャストを行わず、%dから%fないしPRId64に変更すると安全かもしれない。

time_t型の2変数の差分がprintf()で出力される際、int型へキャストしたのちフォーマット指定子%dが用いられている。
通常は起き得ないがそのの値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を出力する場合は、difftime()の戻り値の型であるdouble型（printf("%f\n", num)）や、64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）が適切。
