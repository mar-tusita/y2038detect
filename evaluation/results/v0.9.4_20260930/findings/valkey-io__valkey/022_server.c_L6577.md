# valkey-io/valkey — src/server.c:6577

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/server.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/server.c#L6577) |
| 行 | 6577 |
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
  6571                  replica_repl_offset = server.cached_primary->repl_data->reploff;
  6572                  replica_read_repl_offset = server.cached_primary->repl_data->read_reploff;
  6573              }
  6574  
  6575              info = sdscatprintf(
  6576                  info,
> 6577                  FMTARGS(
  6578                      "master_host:%s\r\n", server.primary_host,
  6579                      "master_port:%d\r\n", server.primary_port,
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
(server.unixtime - server.primary->last_interaction)を出力する際、intへのキャストを行わず、%dから%fないしPRId64に変更すると安全かもしれない。

time_t型の2変数の差分がprintf()で出力される際、int型へキャストしたのちフォーマット指定子%dが用いられている。
通常は起き得ないがそのの値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を出力する場合は、difftime()の戻り値の型であるdouble型（printf("%f\n", num)）や、64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）が適切。
