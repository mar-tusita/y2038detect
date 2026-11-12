# ventoy/Ventoy — SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c:6343

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/SQUASHFS/squashfs-tools-4.4/squashfs-tools/mksquashfs.c#L6343) |
| 行 | 6343 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
  6337  	sBlk.s_minor = SQUASHFS_MINOR;
  6338  	sBlk.block_size = block_size;
  6339  	sBlk.block_log = block_log;
  6340  	sBlk.flags = SQUASHFS_MKFLAGS(noI, noD, noF, noX, noId, no_fragments,
  6341  		always_use_fragments, duplicate_checking, exportable,
  6342  		no_xattrs, comp_opts);
> 6343  	sBlk.mkfs_time = mkfs_time_opt ? mkfs_time : time(NULL);
  6344  
  6345  	disable_info();
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: SquashFSの仕様上2106年2月7日06:28:15(UTC)までは問題が発覚しない。それ以降のタイムスタンプを扱う場合は注意が必要である。
