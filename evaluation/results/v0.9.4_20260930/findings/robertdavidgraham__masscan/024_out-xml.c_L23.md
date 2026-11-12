# robertdavidgraham/masscan — src/out-xml.c:23

| 項目 | 値 |
|------|----|
| リポジトリ | [robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| ファイル | [`src/out-xml.c`](https://github.com/robertdavidgraham/masscan/blob/94e118ccd26c2fb263fb2fe731043f7b3240723c/src/out-xml.c#L23) |
| 行 | 23 |
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
    17      if (out->xml.stylesheet && out->xml.stylesheet[0]) {
    18          fprintf(fp, "<?xml-stylesheet href=\"%s\" type=\"text/xsl\"?>\r\n",
    19              out->xml.stylesheet);
    20      }
    21      fprintf(fp, "<nmaprun scanner=\"%s\" start=\"%u\" version=\"%s\"  xmloutputversion=\"%s\">\r\n",
    22          "masscan",
>   23          (unsigned)time(0),
    24          "1.0-BETA",
    25          "1.03" /* xml output version I copied from their site */
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: %uをPRId64に変更すると修正可能。

time_t型の変数がfprintf()で出力される際、unsigned int型へキャストしたのちフォーマット指定子%uが用いられている。
64bit整数型であるint64_t型（fprintf("%" PRId64 "\n", num)）として出力するのが適切。
