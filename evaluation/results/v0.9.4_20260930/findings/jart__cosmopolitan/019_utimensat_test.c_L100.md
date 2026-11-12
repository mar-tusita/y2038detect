# jart/cosmopolitan — test/libc/calls/utimensat_test.c:100

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/libc/calls/utimensat_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/libc/calls/utimensat_test.c#L100) |
| 行 | 100 |
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
    94    struct timespec ts[2] = {
    95        {1655455857},  // atim: Fri Jun 17 2022 08:50:57 GMT+0000
    96        {827727928},   // mtim: Mon Mar 25 1996 04:25:28 GMT+0000
    97    };
    98    EXPECT_SYS(0, 0, touch("boop", 0644));
    99    EXPECT_SYS(0, 3, open("boop", O_RDWR));
>  100    EXPECT_SYS(0, 0, futimens(3, ts));
   101    EXPECT_SYS(0, 0, fstat(3, &st));
   102    EXPECT_SYS(0, 0, close(3));
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: futimens()の実行結果を確認しているだけで、問題はない。
