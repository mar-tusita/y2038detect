# iovisor/bcc — libbpf-tools/tcprtt.c:315

| 項目 | 値 |
|------|----|
| リポジトリ | [iovisor/bcc](https://github.com/iovisor/bcc) |
| ファイル | [`libbpf-tools/tcprtt.c`](https://github.com/iovisor/bcc/blob/a3dcb9a53f289a1cabc8f6d9e33acc84e810f1c4/libbpf-tools/tcprtt.c#L315) |
| 行 | 315 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:50Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   309  	/* setup duration */
   310  	if (env.duration)
   311  		time_end = get_ktime_ns() + env.duration * NSEC_PER_SEC;
   312  
   313  	/* main: poll */
   314  	while (1) {
>  315  		sleep(env.interval);
   316  		printf("\n");
   317  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: env.intervalはインターバル時間を表す変数であり、時刻を考慮していない。
