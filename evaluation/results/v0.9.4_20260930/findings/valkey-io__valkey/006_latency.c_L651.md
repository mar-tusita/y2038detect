# valkey-io/valkey — src/latency.c:651

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/latency.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/latency.c#L651) |
| 行 | 651 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   645          } else {
   646              if (ts->samples[i].latency > max) max = ts->samples[i].latency;
   647              if (ts->samples[i].latency < min) min = ts->samples[i].latency;
   648          }
   649          /* Use as label the number of seconds / minutes / hours / days
   650           * ago the event happened. */
>  651          elapsed = time(NULL) - ts->samples[i].time;
   652          if (elapsed < 60)
   653              snprintf(buf, sizeof(buf), "%ds", elapsed);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: elapsedの型をint型からdouble型ないしint64_t型に変更すると修正可能。
ただし、ts->samples[i].timeが意図的にint32_t型であるため、問題はそれだけでは解決しない。

elapsedの型はint型。time_t型の2変数の差分がelapsedに格納される。
通常は起き得ないがelapsedの値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
なお、src/latency.hにおいて、struct latencySampleのtimeフィールドにあるコメントでは「We don't use time_t to force 4 bytes usage everywhere.」と書かれており、時間を意図的に32bitとして扱っていると考えられる。
このため、time_t型をint32_t型に変換することは意図的な設計だと考えられる。
