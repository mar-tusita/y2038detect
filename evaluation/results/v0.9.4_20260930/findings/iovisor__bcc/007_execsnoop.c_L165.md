# iovisor/bcc — libbpf-tools/execsnoop.c:165

| 項目 | 値 |
|------|----|
| リポジトリ | [iovisor/bcc](https://github.com/iovisor/bcc) |
| ファイル | [`libbpf-tools/execsnoop.c`](https://github.com/iovisor/bcc/blob/a3dcb9a53f289a1cabc8f6d9e33acc84e810f1c4/libbpf-tools/execsnoop.c#L165) |
| 行 | 165 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:50Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   159  	long nsec, sec;
   160  	static struct timespec cur_time;
   161  	double time_diff;
   162  
   163  	clock_gettime(CLOCK_MONOTONIC, &cur_time);
   164  	nsec = cur_time.tv_nsec - start_time.tv_nsec;
>  165  	sec = cur_time.tv_sec - start_time.tv_sec;
   166  	if (nsec < 0) {
   167  		nsec += NSEC_PER_SEC;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
secの型をlong型からdouble型ないしint64_t型に変更するとより安全かもしれない。

secの型はlong型。time_t型の2変数の差分がsecに格納される。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがsecの値がlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
