# valkey-io/valkey — src/localtime.c:74

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/localtime.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/localtime.c#L74) |
| 行 | 74 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
    68      t -= tz;                       /* Adjust for timezone. */
    69      t += 3600 * dst;               /* Adjust for daylight time. */
    70      time_t days = t / secs_day;    /* Days passed since epoch. */
    71      time_t seconds = t % secs_day; /* Remaining seconds. */
    72  
    73      tmp->tm_isdst = dst;
>   74      tmp->tm_hour = seconds / secs_hour;
    75      tmp->tm_min = (seconds % secs_hour) / secs_min;
    76      tmp->tm_sec = (seconds % secs_hour) % secs_min;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 代入する値は値の範囲が限定されており、2038年以降でも問題は発生しない。
