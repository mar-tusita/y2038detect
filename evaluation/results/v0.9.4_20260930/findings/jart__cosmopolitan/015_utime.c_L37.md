# jart/cosmopolitan — libc/calls/utime.c:37

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`libc/calls/utime.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/libc/calls/utime.c#L37) |
| 行 | 37 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
call to utimes() uses struct timeval with long tv_sec; limited to 32-bit range — use utimensat() instead
```

## コード

```c
    31    struct timeval tv[2];
    32    if (times) {
    33      tv[0].tv_sec = times->actime;
    34      tv[0].tv_usec = 0;
    35      tv[1].tv_sec = times->modtime;
    36      tv[1].tv_usec = 0;
>   37      return utimes(path, tv);
    38    } else {
    39      return utimes(path, NULL);
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utimes()の代わりにutimensat()の使用を検討してください。
