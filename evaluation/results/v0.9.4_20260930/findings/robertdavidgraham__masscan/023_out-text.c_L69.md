# robertdavidgraham/masscan — src/out-text.c:69

| 項目 | 値 |
|------|----|
| リポジトリ | [robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| ファイル | [`src/out-text.c`](https://github.com/robertdavidgraham/masscan/blob/94e118ccd26c2fb263fb2fe731043f7b3240723c/src/out-text.c#L69) |
| 行 | 69 |
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
    63  
    64      fprintf(fp, "%s %s %u %s %u %s %s\n",
    65          "banner",
    66          name_from_ip_proto(ip_proto),
    67          port,
    68          fmt.string,
>   69          (unsigned)timestamp,
    70          masscan_app_to_string(proto),
    71          normalize_string(px, length, banner_buffer, sizeof(banner_buffer))
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: %uをPRId64に変更すると修正可能。

time_t型の変数をfprintf()ではunsigned int型と解釈して出力している。
2106年までは問題がないが、その後time_t型の変数がunsigned int型に納まらない（33bit以上の値になる）場合に問題となる。
64bit整数型であるint64_t型（fprintf("%" PRId64 "\n", num)）として出力するのが適切。
