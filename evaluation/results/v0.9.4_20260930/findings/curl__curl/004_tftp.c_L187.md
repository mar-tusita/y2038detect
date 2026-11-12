# curl/curl — lib/tftp.c:187

| 項目 | 値 |
|------|----|
| リポジトリ | [curl/curl](https://github.com/curl/curl) |
| ファイル | [`lib/tftp.c`](https://github.com/curl/curl/blob/872c313d7647ac437c83128e6bea7a8ed16cd2ef/lib/tftp.c#L187) |
| 行 | 187 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:27:25Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   181      state->retry_max = 3;
   182  
   183    if(state->retry_max > 50)
   184      state->retry_max = 50;
   185  
   186    /* Compute the re-ACK interval to suit the timeout */
>  187    state->retry_time = (int)(timeout / state->retry_max);
   188    if(state->retry_time < 1)
   189      state->retry_time = 1;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timeoutはタイムアウト時間を秒単位で指定するための引数であり、時刻を考慮していない。
