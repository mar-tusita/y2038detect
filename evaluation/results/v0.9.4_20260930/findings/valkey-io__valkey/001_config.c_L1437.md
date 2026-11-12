# valkey-io/valkey — src/config.c:1437

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/config.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/config.c#L1437) |
| 行 | 1437 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
  1431       */
  1432      if (!server.saveparamslen) {
  1433          rewriteConfigRewriteLine(state, name, sdsnew("save \"\""), 1);
  1434      } else {
  1435          line = sdsnew(name);
  1436          for (j = 0; j < server.saveparamslen; j++) {
> 1437              line = sdscatprintf(line, " %ld %d", (long)server.saveparams[j].seconds, server.saveparams[j].changes);
  1438          }
  1439          rewriteConfigRewriteLine(state, name, line, 1);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: この変数はRDBの保存パラメータであり（snapshotの監視ウィンドウ）、時刻を考慮していない。
