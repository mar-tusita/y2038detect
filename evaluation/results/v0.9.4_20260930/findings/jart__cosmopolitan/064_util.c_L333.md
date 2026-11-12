# jart/cosmopolitan — third_party/zstd/programs/util.c:333

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/zstd/programs/util.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/zstd/programs/util.c#L333) |
| 行 | 333 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   327      }
   328  #else
   329      {
   330          struct utimbuf timebuf;
   331          timebuf.actime = time(NULL);
   332          timebuf.modtime = statbuf->st_mtime;
>  333          ret = utime(filename, &timebuf);
   334      }
   335  #endif
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。

このコードではZSTD_USE_UTIMENSATが真ならutimensat()を使用するように書かれているため、その場合この部分は実行されない。
古いPOSIX環境ではutimensat()が使えないため、utime()を使用するようにしているが、time_tが64bitであれば問題はない。
