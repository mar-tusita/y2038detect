# git/git — builtin/pack-objects.c:1437

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`builtin/pack-objects.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/builtin/pack-objects.c#L1437) |
| 行 | 1437 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
  1431  			} else if (!last_mtime) {
  1432  				last_mtime = st.st_mtime;
  1433  			} else {
  1434  				struct utimbuf utb;
  1435  				utb.actime = st.st_atime;
  1436  				utb.modtime = --last_mtime;
> 1437  				if (utime(pack_tmp_name, &utb) < 0)
  1438  					warning_errno(_("failed utime() on %s"), pack_tmp_name);
  1439  			}
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: false-positive
コメント: ただし、utime()の代わりにutimensat()の使用を検討してください。
