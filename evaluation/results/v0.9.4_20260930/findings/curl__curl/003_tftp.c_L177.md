# curl/curl — lib/tftp.c:177

| 項目 | 値 |
|------|----|
| リポジトリ | [curl/curl](https://github.com/curl/curl) |
| ファイル | [`lib/tftp.c`](https://github.com/curl/curl/blob/872c313d7647ac437c83128e6bea7a8ed16cd2ef/lib/tftp.c#L177) |
| 行 | 177 |
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
   171      /* do the calculation only if the timeout is "reasonable" */
   172      timeout = (time_t)(timeout_ms + 500) / 1000;
   173    else
   174      timeout = 15;
   175  
   176    /* Average reposting an ACK after 5 seconds */
>  177    state->retry_max = (int)timeout / 5;
   178  
   179    /* Bound the total number */
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timeoutはタイムアウト時間を秒単位で指定するための引数であり、時刻を考慮していない。
