# ggreer/the_silver_searcher — src/main.c:213

| 項目 | 値 |
|------|----|
| リポジトリ | [ggreer/the_silver_searcher](https://github.com/ggreer/the_silver_searcher) |
| ファイル | [`src/main.c`](https://github.com/ggreer/the_silver_searcher/blob/a61f1780b64266587e7bc30f0f5f71c6cca97c0f/src/main.c#L213) |
| 行 | 213 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:38:43Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   207              }
   208          }
   209      }
   210  
   211      if (opts.stats) {
   212          gettimeofday(&(stats.time_end), NULL);
>  213          double time_diff = ((long)stats.time_end.tv_sec * 1000000 + stats.time_end.tv_usec) -
   214                             ((long)stats.time_start.tv_sec * 1000000 + stats.time_start.tv_usec);
   215          time_diff /= 1000000;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: longへのキャストをやめることによって修正可能。

おそらくこのコードはlong型が64bitであることを前提にしていると考えられる。
WindowsなどのLLP64データモデル（long型は32bit）では、stats.time_end.tv_secをlong型へキャストすることで桁あふれが発生する。
