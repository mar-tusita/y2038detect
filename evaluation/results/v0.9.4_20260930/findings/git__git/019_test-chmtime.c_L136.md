# git/git — t/helper/test-chmtime.c:136

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`t/helper/test-chmtime.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/t/helper/test-chmtime.c#L136) |
| 行 | 136 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   130  		if (get) {
   131  			printf("%"PRIuMAX"\n", mtime);
   132  		} else if (verbose) {
   133  			printf("%"PRIuMAX"\t%s\n", mtime, argv[i]);
   134  		}
   135  
>  136  		if (utb.modtime != sb.st_mtime && utime(argv[i], &utb) < 0) {
   137  #ifdef GIT_WINDOWS_NATIVE
   138  			if (S_ISDIR(sb.st_mode)) {
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。
