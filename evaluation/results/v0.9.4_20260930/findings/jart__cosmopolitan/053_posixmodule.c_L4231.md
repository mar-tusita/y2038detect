# jart/cosmopolitan — third_party/python/Modules/posixmodule.c:4231

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/python/Modules/posixmodule.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/python/Modules/posixmodule.c#L4231) |
| 行 | 4231 |
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
  4225  #ifndef MS_WINDOWS
  4226  
  4227  static int
  4228  utime_default(utime_t *ut, const char *path)
  4229  {
  4230      UTIME_TO_TIMESPEC;
> 4231      return utimensat(DEFAULT_DIR_FD, path, time, 0);
  4232  }
  4233  
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: utimensat()の実行結果を確認しているだけで、問題はない。
