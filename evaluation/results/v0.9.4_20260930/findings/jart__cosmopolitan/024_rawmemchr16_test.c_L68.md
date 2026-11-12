# jart/cosmopolitan — test/libc/str/rawmemchr16_test.c:68

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/libc/str/rawmemchr16_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/libc/str/rawmemchr16_test.c#L68) |
| 行 | 68 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
    62  void *eat(const void *x) {
    63    return (void *)x;
    64  }
    65  void *(*pEat)(const void *x) = eat;
    66  
    67  long tonanos(struct timespec x) {
>   68    return x.tv_sec * 1000000000ul + x.tv_nsec;
    69  }
    70  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
tonanos()の戻り型をlongからint64_tなどのよりビット幅が大きい型に変更するとより安全かもしれない。

tonanos()はstruct timespecで与えられる時刻をナノ秒に変換している。
ただ、tonanos()に与える引数は、2つのstruct timespecで与えられる時刻の差分を計算するtub()の戻り値である。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがその値がlong型に納まらない可能性は否定されない。
