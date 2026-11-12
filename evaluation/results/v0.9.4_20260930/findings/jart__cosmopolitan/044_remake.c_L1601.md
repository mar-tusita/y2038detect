# jart/cosmopolitan — third_party/make/remake.c:1601

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/make/remake.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/make/remake.c#L1601) |
| 行 | 1601 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
access to struct stat timestamp field 'st_mtime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
  1595        }
  1596    }
  1597  #else
  1598    EINTRLOOP (e, stat (name, &st));
  1599  #endif
  1600    if (e == 0)
> 1601      mtime = FILE_TIMESTAMP_STAT_MODTIME (name, st);
  1602    else if (errno == ENOENT || errno == ENOTDIR)
  1603      mtime = NONEXISTENT_MTIME;
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
