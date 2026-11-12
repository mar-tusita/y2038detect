# ventoy/Ventoy — Plugson/src/Lib/libhttp/include/civetweb.c:10792

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`Plugson/src/Lib/libhttp/include/civetweb.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/Plugson/src/Lib/libhttp/include/civetweb.c#L10792) |
| 行 | 10792 |
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
  10786  	    && conn->ctx->callbacks.init_ssl == NULL) {
  10787  		return 0;
  10788  	}
  10789  
  10790  	t = data_check;
  10791  	if (stat(pem, &cert_buf) != -1) {
> 10792  		t = (long int)cert_buf.st_mtime;
  10793  	}
  10794  
```

## 確認すべきポイント

種別（struct stat タイムスタンプフィールドアクセス）から自動生成した確認事項です。断定的な修正方法ではありません。

- この値の最終的な使い道を確認してください。狭い型に代入している場合は、別途 narrowing として検出されているはずです（本項目はファイルシステム層のタイムスタンプ精度自体に関する注意です）
- 対象のファイルシステムは 64-bit タイムスタンプに対応していますか？（ext4 の 64-bit inode 拡張など、対応状況はファイルシステムにより異なります）
- 長期間（数十年単位）保存・比較される値ですか？ アーカイブ・ライセンス期限・キャッシュ有効期限など、長期の時刻比較に使われる場合は特に注意が必要です

## 確認結果

判定: true-positive
コメント: long intのキャストをやめ、tの型をtime_t型に変更すると修正可能。

tの型はlong int型。stat()の出力であるst_mtimeが代入される。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
