# hashcat/hashcat — deps/zlib/examples/gzlog.c:377

| 項目 | 値 |
|------|----|
| リポジトリ | [hashcat/hashcat](https://github.com/hashcat/hashcat) |
| ファイル | [`deps/zlib/examples/gzlog.c`](https://github.com/hashcat/hashcat/blob/2d71af3718ef76f69c675e933cb4900c40788c58/deps/zlib/examples/gzlog.c#L377) |
| 行 | 377 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:41:18Z |

## 検出理由

```text
call to utimes() uses struct timeval with long tv_sec; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   371     for verification of ownership. */
   372  local void log_touch(struct log *log)
   373  {
   374      struct stat st;
   375  
   376      strcpy(log->end, ".lock");
>  377      utimes(log->path, NULL);
   378      if (stat(log->path, &st) == 0)
   379          log->lock = st.st_mtime;
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。
