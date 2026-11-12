# jart/cosmopolitan — libc/calls/futimesat.c:36

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`libc/calls/futimesat.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/libc/calls/futimesat.c#L36) |
| 行 | 36 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
call to utimensat() may set timestamps limited to 32-bit time_t on 32-bit systems
```

## コード

```c
    30    struct timespec ts[2];
    31    if (tv) {
    32      ts[0].tv_sec = tv[0].tv_sec;
    33      ts[0].tv_nsec = tv[0].tv_usec * 1000;
    34      ts[1].tv_sec = tv[1].tv_sec;
    35      ts[1].tv_nsec = tv[1].tv_usec * 1000;
>   36      return utimensat(dirfd, pathname, ts, 0);
    37    } else {
    38      return utimensat(dirfd, pathname, NULL, 0);
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: utimensat()の実行結果を確認しているだけで、問題はない。
