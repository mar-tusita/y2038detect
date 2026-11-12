# jart/cosmopolitan — third_party/readline/history.c:268

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/readline/history.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/readline/history.c#L268) |
| 行 | 268 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
   262    char ts[64], *ret;
   263  
   264    t = (time_t) time ((time_t *)0);
   265  #if defined (HAVE_VSNPRINTF)		/* assume snprintf if vsnprintf exists */
   266    snprintf (ts, sizeof (ts) - 1, "X%lu", (unsigned long) t);
   267  #else
>  268    sprintf (ts, "X%lu", (unsigned long) t);
   269  #endif
   270    ret = savestring (ts);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: unsigned longのキャストをやめ、%luをPRId64に変更すると修正可能。

time_t型の変数がsprintf()で出力される際、unsigned long型へキャストしたのちフォーマット指定子%luが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2106年以降に桁あふれが起きる可能性がある。
64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）として出力するのが適切。
