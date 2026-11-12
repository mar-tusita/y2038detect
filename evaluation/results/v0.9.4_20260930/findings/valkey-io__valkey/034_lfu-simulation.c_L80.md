# valkey-io/valkey — utils/lru/lfu-simulation.c:80

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`utils/lru/lfu-simulation.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/utils/lru/lfu-simulation.c#L80) |
| 行 | 80 |
| 種別 | printf 系フォーマット不一致 |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
time_t passed to printf-family function with incompatible format specifier: may truncate after 2038
```

## コード

```c
    74      if (pos >= 10 && pos <= 14) tag = "new no access";
    75      if (pos >= 15 && pos <= 19) tag = "new accessed ";
    76      if (pos >= keyspace_size -5) tag= "old no access";
    77  
    78      printf("%ld] <%s> frequency:%d decrtime:%d [%lu hits | age:%ld sec]\n",
    79          pos, tag, e->counter, e->decrtime, (unsigned long)e->hits,
>   80              time(NULL) - e->ctime);
    81  }
    82  
```

## 確認すべきポイント

種別（printf 系フォーマット不一致）から自動生成した確認事項です。断定的な修正方法ではありません。

- `time_t` は対象プラットフォームで 64-bit ですか？ その場合、`%d` 等の 32-bit 指定子では可変長引数の型が一致せず、2038年を待たずに未定義動作（不正な値の出力）が起きる可能性があります
- フォーマット指定子を実際の型に合わせて修正してください（例: `%lld` と `(long long)` へのキャスト、または `<inttypes.h>` の `PRId64` の利用）

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
%ldを%fないしPRId64に変更するとより安全かもしれない。

time_t型の2変数の差分がprintf()で出力される際、long型と解釈してフォーマット指定子%ldが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を出力する場合は、difftime()の戻り値の型であるdouble型（printf("%f\n", num)）や、64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）が適切。
