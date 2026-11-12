# valkey-io/valkey — src/replication.c:705

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/replication.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/replication.c#L705) |
| 行 | 705 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   699      int j;
   700      sds cmdrepr = sdsnew("+");
   701      robj *cmdobj;
   702      struct timeval tv;
   703  
   704      gettimeofday(&tv, NULL);
>  705      cmdrepr = sdscatprintf(cmdrepr, "%ld.%06ld ", (long)tv.tv_sec, (long)tv.tv_usec);
   706      if (c->flag.script) {
   707          cmdrepr = sdscatprintf(cmdrepr, "[%d lua] ", dictid);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: tv.tv_secをlong型にキャストせず、%ldをPRId64に変更すると修正可能。

gettimeofday()で得た現在の時間のうち秒単位の値がprintf()で出力される際、long型へキャストしたのちフォーマット指定子%ldが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）として出力するのが適切。
