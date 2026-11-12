# openwrt/openwrt — package/network/services/hostapd/src/hostapd/radius.c:178

| 項目 | 値 |
|------|----|
| リポジトリ | [openwrt/openwrt](https://github.com/openwrt/openwrt) |
| ファイル | [`package/network/services/hostapd/src/hostapd/radius.c`](https://github.com/openwrt/openwrt/blob/805098d8b62fdd5894738fa5080ad66347d1340b/package/network/services/hostapd/src/hostapd/radius.c#L178) |
| 行 | 178 |
| 種別 | struct stat タイムスタンプフィールドアクセス |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:39:30Z |

## 検出理由

```text
access to struct stat timestamp field 'st_mtime': filesystem may not preserve timestamps beyond 2038
```

## コード

```c
   172  	struct stat st;
   173  	int rem;
   174  
   175  	if (stat(s->user_file, &st))
   176  		return;
   177  
>  178  	if (s->user_file_ts == st.st_mtime)
   179  		return;
   180  
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: false-positive
コメント: 単純な時間の比較であり、問題はない。
