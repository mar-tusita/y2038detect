# hashcat/hashcat — deps/zlib/examples/gzlog.c:365

| 項目 | 値 |
|------|----|
| リポジトリ | [hashcat/hashcat](https://github.com/hashcat/hashcat) |
| ファイル | [`deps/zlib/examples/gzlog.c`](https://github.com/hashcat/hashcat/blob/2d71af3718ef76f69c675e933cb4900c40788c58/deps/zlib/examples/gzlog.c#L365) |
| 行 | 365 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:41:18Z |

## 検出理由

```text
access to struct stat timestamp field 'st_mtime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
   359              continue;
   360          }
   361          sleep(2);       /* relinquish the CPU for two seconds while waiting */
   362      }
   363      close(fd);
   364      if (stat(log->path, &st) == 0)
>  365          log->lock = st.st_mtime;
   366      return 0;
   367  }
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: false-positive
コメント: 単にstat()の出力結果を代入しただけで、問題はない。

ただし、32bitで時間を扱うファイルシステムでは、2038年以降に作成されたファイルの時刻が正しく取得できない。
