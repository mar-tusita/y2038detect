# mpv-player/mpv — player/configfiles.c:196

| 項目 | 値 |
|------|----|
| リポジトリ | [mpv-player/mpv](https://github.com/mpv-player/mpv) |
| ファイル | [`player/configfiles.c`](https://github.com/mpv-player/mpv/blob/f239c2dd767ee52729f73dda4f6c9face0ca7d56/player/configfiles.c#L196) |
| 行 | 196 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:29:40Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   190  
   191      struct utimbuf ut = {
   192          .actime = st2.st_atime,  // we want to pass this through intact
   193          .modtime = st1.st_mtime,
   194      };
   195  
>  196      if (utime(f2, &ut) != 0)
   197          return false;
   198  
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。
