# mpv-player/mpv — player/javascript.c:924

| 項目 | 値 |
|------|----|
| リポジトリ | [mpv-player/mpv](https://github.com/mpv-player/mpv) |
| ファイル | [`player/javascript.c`](https://github.com/mpv-player/mpv/blob/f239c2dd767ee52729f73dda4f6c9face0ca7d56/player/javascript.c#L924) |
| 行 | 924 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:29:40Z |

## 検出理由

```text
access to struct stat timestamp field 'st_atime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
   918          "mode", "size",
   919          "atime", "mtime", "ctime", NULL
   920      };
   921      const double stat_values[] = {
   922          statbuf.st_mode,
   923          statbuf.st_size,
>  924          statbuf.st_atime,
   925          statbuf.st_mtime,
   926          statbuf.st_ctime
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
