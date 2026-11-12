# pbatard/rufus — src/format_ext.c:466

| 項目 | 値 |
|------|----|
| リポジトリ | [pbatard/rufus](https://github.com/pbatard/rufus) |
| ファイル | [`src/format_ext.c`](https://github.com/pbatard/rufus/blob/74b11028144156e3e932811435d177f34d4246ac/src/format_ext.c#L466) |
| 行 | 466 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:28:43Z |

## 検出理由

```text
explicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
   460  			ctime = UINT32_MAX;
   461  		inode.i_mode = 0100644;
   462  		inode.i_links_count = 1;
   463  		// coverity[store_truncates_time_t]
   464  		inode.i_atime = (uint32_t)ctime;
   465  		// coverity[store_truncates_time_t]
>  466  		inode.i_ctime = (uint32_t)ctime;
   467  		// coverity[store_truncates_time_t]
   468  		inode.i_mtime = (uint32_t)ctime;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: ext2fsの仕様上2038年1月19日03:14:07(UTC)までは問題が発覚しない。それ以降のタイムスタンプを扱う場合は注意が必要である。
