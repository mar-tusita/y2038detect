# jart/cosmopolitan — test/libc/calls/utimensat_test.c:147

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/libc/calls/utimensat_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/libc/calls/utimensat_test.c#L147) |
| 行 | 147 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
call to futimens() may set timestamps limited to 32-bit time_t on 32-bit systems
```

## コード

```c
   141    ASSERT_SYS(0, 0, futimens(fd, ts));
   142    sleep(1);
   143    ts[0].tv_nsec = UTIME_NOW;   // change access time
   144    ts[1].tv_nsec = UTIME_OMIT;  // don't change modified time
   145    close(fd);
   146    fd = open("foo", O_RDONLY);
>  147    ASSERT_SYS(0, 0, futimens(fd, ts));
   148    ASSERT_SYS(0, 0, fstat(fd, &st));
   149    // check time of last status change equals access time
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: futimens()の実行結果を確認しているだけで、問題はない。
