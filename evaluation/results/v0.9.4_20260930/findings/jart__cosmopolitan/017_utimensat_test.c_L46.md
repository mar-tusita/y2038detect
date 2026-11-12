# jart/cosmopolitan — test/libc/calls/utimensat_test.c:46

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/libc/calls/utimensat_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/libc/calls/utimensat_test.c#L46) |
| 行 | 46 |
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
    40    struct stat st;
    41    struct timeval tv[2] = {
    42        {1655455857, 1},  // atim: Fri Jun 17 2022 08:50:57 GMT+0000
    43        {827727928, 2},   // mtim: Mon Mar 25 1996 04:25:28 GMT+0000
    44    };
    45    EXPECT_SYS(0, 0, touch("boop", 0644));
>   46    EXPECT_SYS(0, 0, utimes("boop", tv));
    47    EXPECT_SYS(0, 0, stat("boop", &st));
    48    EXPECT_EQ(1655455857, st.st_atim.tv_sec);
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utimes()の代わりにutimensat()の使用を検討してください。
