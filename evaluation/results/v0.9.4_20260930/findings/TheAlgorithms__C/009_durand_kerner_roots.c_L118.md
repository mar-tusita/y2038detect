# TheAlgorithms/C — numerical_methods/durand_kerner_roots.c:118

| 項目 | 値 |
|------|----|
| リポジトリ | [TheAlgorithms/C](https://github.com/TheAlgorithms/C) |
| ファイル | [`numerical_methods/durand_kerner_roots.c`](https://github.com/TheAlgorithms/C/blob/e5dad3fa8def3726ec850ca66a7f51521f8ad393/numerical_methods/durand_kerner_roots.c#L118) |
| 行 | 118 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:58:15Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   112          degree * sizeof(long double)); /* store all input coefficients */
   113      s0 = (long double complex *)malloc(
   114          (degree - 1) *
   115          sizeof(long double complex)); /* number of roots = degree-1 */
   116  
   117      /* initialize random seed: */
>  118      srand(time(NULL));
   119  
   120      if (!coeffs || !s0)
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)は単純な乱数の種として使われるだけで、時刻を考慮していない。

またsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
