# redis/redis — src/localtime.c:68

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`src/localtime.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/src/localtime.c#L68) |
| 行 | 68 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
    62          /* Leap years have one day more. */
    63          time_t days_this_year = 365 + is_leap_year(tmp->tm_year);
    64          if (days_this_year > days) break;
    65          days -= days_this_year;
    66          tmp->tm_year++;
    67      }
>   68      tmp->tm_yday = days;  /* Number of day of the current year. */
    69  
    70      /* We need to calculate in which month and day of the month we are. To do
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 代入する値は値の範囲が限定されており、2038年以降でも問題は発生しない。
