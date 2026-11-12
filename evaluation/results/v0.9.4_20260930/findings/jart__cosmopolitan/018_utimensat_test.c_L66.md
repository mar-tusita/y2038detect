# jart/cosmopolitan — test/libc/calls/utimensat_test.c:66

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/libc/calls/utimensat_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/libc/calls/utimensat_test.c#L66) |
| 行 | 66 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
call to futimes() uses struct timeval with long tv_sec; limited to 32-bit range — use futimens() instead
```

## コード

```c
    60  TEST(futimes, test) {
    61    if (IsLinux() && !__is_linux_2_6_23())
    62      return;
    63    struct stat st;
    64    struct timeval tv[2] = {{1655455857, 1}, {827727928, 2}};
    65    EXPECT_SYS(0, 3, creat("boop", 0644));
>   66    EXPECT_SYS(0, 0, futimes(3, tv));
    67    EXPECT_SYS(0, 0, fstat(3, &st));
    68    EXPECT_EQ(1655455857, st.st_atim.tv_sec);
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: futimens()の実行結果を確認しているだけで、問題はない。
