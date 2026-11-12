# mpv-player/mpv — video/out/vo_gpu_next.c:2136

| 項目 | 値 |
|------|----|
| リポジトリ | [mpv-player/mpv](https://github.com/mpv-player/mpv) |
| ファイル | [`video/out/vo_gpu_next.c`](https://github.com/mpv-player/mpv/blob/f239c2dd767ee52729f73dda4f6c9face0ca7d56/video/out/vo_gpu_next.c#L2136) |
| 行 | 2136 |
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
  2130          if (fname.len != 16) // %016x
  2131              continue;
  2132          MP_TARRAY_APPEND(ta_ctx, files, num_files,
  2133                           (struct file_entry){
  2134                               .filepath = filepath,
  2135                               .size     = filestat.st_size,
> 2136                               .atime    = filestat.st_atime,
  2137                           });
  2138      }
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
