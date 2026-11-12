# jart/cosmopolitan — test/posix/signal_latency_test.c:45

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/posix/signal_latency_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/posix/signal_latency_test.c#L45) |
| 行 | 45 |
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
    39  
    40  void receiver_signal_handler(int signo) {
    41    struct timespec receive_time;
    42    if (clock_gettime(CLOCK_MONOTONIC, &receive_time) == -1)
    43      exit(1);
    44  
>   45    long sec_diff = receive_time.tv_sec - send_time.tv_sec;
    46    long nsec_diff = receive_time.tv_nsec - send_time.tv_nsec;
    47    double latency_ns = sec_diff * 1e9 + nsec_diff;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
sec_diffの型をlong型からdouble型ないしint64_t型に変更するとより安全かもしれない。

sec_diffの型はlong型。time_t型の2変数の差分がsec_diffに格納される。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがsec_diffの値がlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
