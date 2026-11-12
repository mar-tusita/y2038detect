# valkey-io/valkey — src/server.c:6691

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`src/server.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/src/server.c#L6691) |
| 行 | 6691 |
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
  6685          info = sdscatprintf(info,
  6686                              "# CPU\r\n"
  6687                              "used_cpu_sys:%ld.%06ld\r\n"
  6688                              "used_cpu_user:%ld.%06ld\r\n"
  6689                              "used_cpu_sys_children:%ld.%06ld\r\n"
  6690                              "used_cpu_user_children:%ld.%06ld\r\n",
> 6691                              (long)self_ru.ru_stime.tv_sec, (long)self_ru.ru_stime.tv_usec,
  6692                              (long)self_ru.ru_utime.tv_sec, (long)self_ru.ru_utime.tv_usec, (long)c_ru.ru_stime.tv_sec,
  6693                              (long)c_ru.ru_stime.tv_usec, (long)c_ru.ru_utime.tv_sec, (long)c_ru.ru_utime.tv_usec);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: self_ruはgetrusage()が設定する値であり、時刻を考慮していない。
