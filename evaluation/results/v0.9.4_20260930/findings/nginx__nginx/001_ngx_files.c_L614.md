# nginx/nginx — src/os/unix/ngx_files.c:614

| 項目 | 値 |
|------|----|
| リポジトリ | [nginx/nginx](https://github.com/nginx/nginx) |
| ファイル | [`src/os/unix/ngx_files.c`](https://github.com/nginx/nginx/blob/d44205284fa41662da803b796d6056fc1e59b1f3/src/os/unix/ngx_files.c#L614) |
| 行 | 614 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:35:15Z |

## 検出理由

```text
call to utimes() uses struct timeval with long tv_sec; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   608  
   609      tv[0].tv_sec = ngx_time();
   610      tv[0].tv_usec = 0;
   611      tv[1].tv_sec = s;
   612      tv[1].tv_usec = 0;
   613  
>  614      if (utimes((char *) name, tv) != -1) {
   615          return NGX_OK;
   616      }
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utimes()の代わりにutimensat()の使用を検討してください。
