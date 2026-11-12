# ventoy/Ventoy — LinuxGUI/Ventoy2Disk/Lib/libhttp/include/civetweb.c:10778

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`LinuxGUI/Ventoy2Disk/Lib/libhttp/include/civetweb.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/LinuxGUI/Ventoy2Disk/Lib/libhttp/include/civetweb.c#L10778) |
| 行 | 10778 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
  10772  	    && conn->ctx->callbacks.init_ssl == NULL) {
  10773  		return 0;
  10774  	}
  10775  
  10776  	t = data_check;
  10777  	if (stat(pem, &cert_buf) != -1) {
> 10778  		t = (long int)cert_buf.st_mtime;
  10779  	}
  10780  
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: long intのキャストをやめ、tの型をtime_t型に変更すると修正可能。

tの型はlong int型。stat()の出力であるst_mtimeが代入される。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
