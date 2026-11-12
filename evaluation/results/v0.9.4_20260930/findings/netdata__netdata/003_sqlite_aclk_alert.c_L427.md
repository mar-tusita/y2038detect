# netdata/netdata — src/database/sqlite/sqlite_aclk_alert.c:427

| 項目 | 値 |
|------|----|
| リポジトリ | [netdata/netdata](https://github.com/netdata/netdata) |
| ファイル | [`src/database/sqlite/sqlite_aclk_alert.c`](https://github.com/netdata/netdata/blob/44d5e9c9fd651ec12b385c6ea7e5dab6db1bafc4/src/database/sqlite/sqlite_aclk_alert.c#L427) |
| 行 | 427 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:58:40Z |

## 検出理由

```text
implicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
   421                                 strdupz((char *)sqlite3_column_text(res, EXEC)) :
   422                                 strdupz((char *)string2str(host->health.default_exec));
   423  
   424      alarm_log->conf_source = source ? strdupz(source) : strdupz("");
   425  
   426      time_t duration = sqlite3_column_int64(res, DURATION);
>  427      alarm_log->duration =  (duration > 0) ? duration : 0;
   428  
   429      int64_t non_clear_duration = sqlite3_column_int64(res, NON_CLEAR_DURATION);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: durationは経過時間を表す変数であり、時刻を考慮していない。
