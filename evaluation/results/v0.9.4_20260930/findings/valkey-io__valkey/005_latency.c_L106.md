# valkey-io/valkey — src/latency.c:106

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/latency.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/latency.c#L106) |
| 行 | 106 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'int32_t' may truncate after 2038
```

## コード

```c
   100      prev = (ts->idx + LATENCY_TS_LEN - 1) % LATENCY_TS_LEN;
   101      if (ts->samples[prev].time == now) {
   102          if (latency > ts->samples[prev].latency) ts->samples[prev].latency = latency;
   103          return;
   104      }
   105  
>  106      ts->samples[ts->idx].time = now;
   107      ts->samples[ts->idx].latency = latency;
   108  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: ts->samples[i].timeが意図的にint32_t型であるため、解決できない。

timeの型はint32_t型。一方、nowの型はtime_t型であり、time(NULL)の戻り値が代入されている。
なお、src/latency.hにおいて、struct latencySampleのtimeフィールドにあるコメントでは「We don't use time_t to force 4 bytes usage everywhere.」と書かれており、時間を意図的に32bitとして扱っていると考えられる。
このため、time_t型をint32_t型に変換することは意図的な設計だと考えられる。
