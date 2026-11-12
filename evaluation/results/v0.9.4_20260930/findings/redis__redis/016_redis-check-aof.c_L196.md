# redis/redis — src/redis-check-aof.c:196

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`src/redis-check-aof.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/src/redis-check-aof.c#L196) |
| 行 | 196 |
| 種別 | printf 系フォーマット不一致 |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
time_t passed to printf-family function with incompatible format specifier: may truncate after 2038
```

## コード

```c
   190              printf("Invalid timestamp annotation\n");
   191              exit(1);
   192          }
   193          if (ts <= to_timestamp) return 1;
   194          if (epos == 0) {
   195              printf("AOF %s has nothing before timestamp %ld, "
>  196                      "aborting...\n", filename, to_timestamp);
   197              exit(1);
   198          }
```

## 確認すべきポイント

種別（printf 系フォーマット不一致）から自動生成した確認事項です。断定的な修正方法ではありません。

- `time_t` は対象プラットフォームで 64-bit ですか？ その場合、`%d` 等の 32-bit 指定子では可変長引数の型が一致せず、2038年を待たずに未定義動作（不正な値の出力）が起きる可能性があります
- フォーマット指定子を実際の型に合わせて修正してください（例: `%lld` と `(long long)` へのキャスト、または `<inttypes.h>` の `PRId64` の利用）

## 確認結果

判定: true-positive
コメント: %ldをPRId64に変更すると修正可能。

to_timestampがprintf()で出力される際、フォーマット指定子%ldが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）として出力するのが適切。
