# SamyPesse/How-to-Make-a-Computer-Operating-System — src/sdk/src/libc/src/sys/utimes.c:17

| 項目 | 値 |
|------|----|
| リポジトリ | [SamyPesse/How-to-Make-a-Computer-Operating-System](https://github.com/SamyPesse/How-to-Make-a-Computer-Operating-System) |
| ファイル | [`src/sdk/src/libc/src/sys/utimes.c`](https://github.com/SamyPesse/How-to-Make-a-Computer-Operating-System/blob/eb30f8802fac9f0f1c28d3a96bb3d402bdfc4687/src/sdk/src/libc/src/sys/utimes.c#L17) |
| 行 | 17 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:58Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
    11  
    12      /* NOTE: no microsecond precision */
    13      tmp.actime = times[ 0 ].tv_sec;
    14      tmp.modtime = times[ 1 ].tv_sec;
    15  
    16      /* This is a wrapper around utime() */
>   17      return utime( filename, &tmp );
    18  }
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。
