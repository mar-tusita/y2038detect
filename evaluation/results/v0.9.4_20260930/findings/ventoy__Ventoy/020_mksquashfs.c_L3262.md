# ventoy/Ventoy — SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c:3262

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c#L3262) |
| 行 | 3262 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
access to struct stat timestamp field 'st_mtime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
  3256  		 * command line
  3257  		 */
  3258  		memset(&buf, 0, sizeof(buf));
  3259  		buf.st_mode = (root_mode_opt) ? root_mode | S_IFDIR : S_IRWXU | S_IRWXG | S_IRWXO | S_IFDIR;
  3260  		buf.st_uid = getuid();
  3261  		buf.st_gid = getgid();
> 3262  		buf.st_mtime = time(NULL);
  3263  		buf.st_dev = 0;
  3264  		buf.st_ino = 0;
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: wontfix
コメント: SquashFSの仕様上2106年2月7日06:28:15(UTC)までは問題が発覚しない。それ以降のタイムスタンプを扱う場合は注意が必要である。
