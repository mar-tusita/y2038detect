# hashcat/hashcat — deps/zlib/examples/gzlog.c:389

| 項目 | 値 |
|------|----|
| リポジトリ | [hashcat/hashcat](https://github.com/hashcat/hashcat) |
| ファイル | [`deps/zlib/examples/gzlog.c`](https://github.com/hashcat/hashcat/blob/2d71af3718ef76f69c675e933cb4900c40788c58/deps/zlib/examples/gzlog.c#L389) |
| 行 | 389 |
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
   383     this is not our lock.  If it is our lock, touch it to keep it. */
   384  local int log_check(struct log *log)
   385  {
   386      struct stat st;
   387  
   388      strcpy(log->end, ".lock");
>  389      if (stat(log->path, &st) || st.st_mtime != log->lock)
   390          return 1;
   391      log_touch(log);
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
