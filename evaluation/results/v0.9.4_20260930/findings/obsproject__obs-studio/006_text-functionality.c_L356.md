# obsproject/obs-studio — plugins/text-freetype2/text-functionality.c:356

| 項目 | 値 |
|------|----|
| リポジトリ | [obsproject/obs-studio](https://github.com/obsproject/obs-studio) |
| ファイル | [`plugins/text-freetype2/text-functionality.c`](https://github.com/obsproject/obs-studio/blob/686ee75a0575b5772d54ccba6b0e8ba67ed7b5b7/plugins/text-freetype2/text-functionality.c#L356) |
| 行 | 356 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:04:21Z |

## 検出理由

```text
access to struct stat timestamp field 'st_mtime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
   350  
   351  	// stat is apparently terrifying and horrible, but we only call it once
   352  	// every second at most.
   353  	if (os_stat(filename, &stats) != 0)
   354  		return -1;
   355  
>  356  	return stats.st_mtime;
   357  }
   358  
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: false-positive
コメント: 単にstat()で取得したファイルの時刻を返すだけで、問題はない。

ただし、32bitで時刻を扱うファイルシステムでは、2038年以降に作成されたファイルの時刻が正しく取得できない。
