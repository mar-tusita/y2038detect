# valkey-io/valkey — src/localtime.c:106

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/localtime.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/localtime.c#L106) |
| 行 | 106 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   100      tmp->tm_mon = 0;
   101      while (days >= mdays[tmp->tm_mon]) {
   102          days -= mdays[tmp->tm_mon];
   103          tmp->tm_mon++;
   104      }
   105  
>  106      tmp->tm_mday = days + 1; /* Add 1 since our 'days' is zero-based. */
   107      tmp->tm_year -= 1900;    /* Surprisingly tm_year is year-1900. */
   108  }
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 代入する値は値の範囲が限定されており、2038年以降でも問題は発生しない。
