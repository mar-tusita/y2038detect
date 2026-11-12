# libuv/libuv — test/runner-unix.c:303

| 項目 | 値 |
|------|----|
| リポジトリ | [libuv/libuv](https://github.com/libuv/libuv) |
| ファイル | [`test/runner-unix.c`](https://github.com/libuv/libuv/blob/ea493f19895bc0cc90b28b48a4e204bc139c48d3/test/runner-unix.c#L303) |
| 行 | 303 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:40:01Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   297    for (;;) {
   298      /* Check that gettimeofday() doesn't jump back in time. */
   299      assert(tv.tv_sec > timebase.tv_sec ||
   300             (tv.tv_sec == timebase.tv_sec && tv.tv_usec >= timebase.tv_usec));
   301  
   302      elapsed_ms =
>  303          (tv.tv_sec - timebase.tv_sec) * 1000 +
   304          (tv.tv_usec / 1000) -
   305          (timebase.tv_usec / 1000);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
elapsed_msの型をunsigned int型からdouble型ないしint64_t型に変更するとより安全かもしれない。

elapsed_msの型をunsigned int型。time_t型の2変数の差分がマイクロ秒単位でelapsed_msに格納される。
通常は起き得ないがelapsed_msの値がunsigned int型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
