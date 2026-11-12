# redis/redis — src/server.c:6899

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`src/server.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/src/server.c#L6899) |
| 行 | 6899 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
  6893          "# CPU\r\n"
  6894          "used_cpu_sys:%ld.%06ld\r\n"
  6895          "used_cpu_user:%ld.%06ld\r\n"
  6896          "used_cpu_sys_children:%ld.%06ld\r\n"
  6897          "used_cpu_user_children:%ld.%06ld\r\n",
  6898          (long)self_ru.ru_stime.tv_sec, (long)self_ru.ru_stime.tv_usec,
> 6899          (long)self_ru.ru_utime.tv_sec, (long)self_ru.ru_utime.tv_usec,
  6900          (long)c_ru.ru_stime.tv_sec, (long)c_ru.ru_stime.tv_usec,
  6901          (long)c_ru.ru_utime.tv_sec, (long)c_ru.ru_utime.tv_usec);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: self_ruはgetrusage()が設定する値であり、時刻を考慮していない。
