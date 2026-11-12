# allinurl/goaccess — src/goaccess.c:1476

| 項目 | 値 |
|------|----|
| リポジトリ | [allinurl/goaccess](https://github.com/allinurl/goaccess) |
| ファイル | [`src/goaccess.c`](https://github.com/allinurl/goaccess/blob/2bd25460a2a23ae8c66354a9c892fff3f9fff392/src/goaccess.c#L1476) |
| 行 | 1476 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:54Z |

## 検出理由

```text
implicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
  1470   * if elapsed time == 0, we will bump it to 1.
  1471   */
  1472  static void
  1473  set_accumulated_time (void) {
  1474    time_t elapsed = end_proc - start_proc;
  1475    elapsed = (!elapsed) ? !elapsed : elapsed;
> 1476    ht_inc_cnt_overall ("processing_time", elapsed);
  1477  }
  1478  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
ht_inc_cnt_overall() の第2引数をuint32_t型からdouble型ないしint64_t型に変更するとより安全かもしれない。

ht_inc_cnt_overall() の第2引数はuint32_t型。time_t型の2変数の差分がelapsedに格納される。
通常は起き得ないがelapsedの値がuint32_t型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
