# ventoy/Ventoy — Plugson/src/Lib/libhttp/include/civetweb.c:6509

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`Plugson/src/Lib/libhttp/include/civetweb.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/Plugson/src/Lib/libhttp/include/civetweb.c#L6509) |
| 行 | 6509 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
  6503  	if (filep != NULL && buf != NULL) {
  6504  		mg_snprintf(NULL,
  6505  		            NULL, /* All calls to construct_etag use 64 byte buffer */
  6506  		            buf,
  6507  		            buf_len,
  6508  		            "\"%lx.%" INT64_FMT "\"",
> 6509  		            (unsigned long)filep->last_modified,
  6510  		            filep->size);
  6511  	}
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: %lxを他と同様INT64_FMTに変更すると修正可能。

time_t型の変数がfprintf()で出力される際、unsigned long型へキャストしたのちフォーマット指定子%lxが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2106年以降に桁あふれが起きる可能性がある。
filep->size同様INT64_FMTを使用するのが適切。
