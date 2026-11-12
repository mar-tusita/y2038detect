# valkey-io/valkey — src/replication.c:4265

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/replication.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/replication.c#L4265) |
| 行 | 4265 |
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
  4259      }
  4260  
  4261      /* Prepare a suitable temp file for bulk transfer */
  4262      if (!useDisklessLoad()) {
  4263          int dfd = -1, maxtries = 5;
  4264          while (maxtries--) {
> 4265              snprintf(tmpfile, 256, "temp-%d.%ld.rdb", (int)server.unixtime, (long int)getpid());
  4266              dfd = open(tmpfile, O_CREAT | O_WRONLY | O_EXCL, 0666);
  4267              if (dfd != -1) break;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 一時的に使用されるファイル名に使用するために時刻が使われており、問題はない。

time_t型の変数がsnprintf()で出力される際、int型へキャストしたのちフォーマット指定子%dが用いられている。
ただここでtmpfileはその後open()で使われる一時ファイルのための名前であって、時刻が正しく表記されなくとも問題はない。
