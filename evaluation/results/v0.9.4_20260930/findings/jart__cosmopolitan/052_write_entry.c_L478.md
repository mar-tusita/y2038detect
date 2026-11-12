# jart/cosmopolitan — third_party/ncurses/write_entry.c:478

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/ncurses/write_entry.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/ncurses/write_entry.c#L478) |
| 行 | 478 |
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
   472  		    LEAF_FMT "/%.*s", ptr[0],
   473  		    (int) sizeof(linkname) - (2 + LEAF_LEN), ptr);
   474  
   475  	if (strcmp(filename, linkname) == 0) {
   476  	    _nc_warning("self-synonym ignored");
   477  	} else if (stat(linkname, &statbuf) >= 0 &&
>  478  		   statbuf.st_mtime < start_time) {
   479  	    _nc_warning("alias %s multiply defined.", ptr);
   480  	} else if (_nc_access(linkname, W_OK) == 0)
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: false-positive
コメント: 単にstat()で取得したファイルの時刻を比較しただけであり、問題はない。

ただし、32bitで時刻を扱うファイルシステムでは、2038年以降に作成されたファイルの時刻が正しく取得できない。
