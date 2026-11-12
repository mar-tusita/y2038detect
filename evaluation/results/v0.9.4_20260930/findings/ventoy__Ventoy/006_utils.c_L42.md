# ventoy/Ventoy — LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/utils.c:42

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/utils.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/utils.c#L42) |
| 行 | 42 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
access to struct stat timestamp field 'st_atime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
    36  	stbuf->st_nlink = 1;
    37  	stbuf->st_uid = ef->uid;
    38  	stbuf->st_gid = ef->gid;
    39  	stbuf->st_size = node->size;
    40  	stbuf->st_blocks = ROUND_UP(node->size, CLUSTER_SIZE(*ef->sb)) / 512;
    41  	stbuf->st_mtime = node->mtime;
>   42  	stbuf->st_atime = node->atime;
    43  	/* set ctime to mtime to ensure we don't break programs that rely on ctime
    44  	   (e.g. rsync) */
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: wontfix
コメント: exFATの仕様上2107年12月31日23:59:58までは問題が発覚しない。それ以降のタイムスタンプを扱う場合は注意が必要である。
