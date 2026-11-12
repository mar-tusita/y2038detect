# robertdavidgraham/masscan — src/proto-ssl.c:1228

| 項目 | 値 |
|------|----|
| リポジトリ | [robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| ファイル | [`src/proto-ssl.c`](https://github.com/robertdavidgraham/masscan/blob/94e118ccd26c2fb263fb2fe731043f7b3240723c/src/proto-ssl.c#L1228) |
| 行 | 1228 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:38Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
  1222  /*****************************************************************************
  1223   *****************************************************************************/
  1224  char *
  1225  ssl_hello(const void *templ)
  1226  {
  1227      unsigned char *px = (unsigned char *)templ;
> 1228      unsigned now = (unsigned)time(0);
  1229      unsigned i;
  1230      
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: 古いTLSのバージョンであれば問題となるが、使用は推奨されない。
TLS1.3ではgmt_unix_timeフィールドが廃止されている。

time_t型であるtime(0)の出力をunsigned int型にキャストしている。
ただ、これははTLSの古いプロトコルにおいて用いられているgmt_unix_timeフィールドのためのもので、その幅は32bit固定として定義されている。
現在推奨されているTLS1.3ではgmt_unix_timeフィールドが廃止されており、代わりに疑似乱数で埋めることになっている。
