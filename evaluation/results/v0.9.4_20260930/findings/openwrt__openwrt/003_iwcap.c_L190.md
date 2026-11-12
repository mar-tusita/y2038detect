# openwrt/openwrt — package/network/utils/iwcap/src/iwcap.c:190

| 項目 | 値 |
|------|----|
| リポジトリ | [openwrt/openwrt](https://github.com/openwrt/openwrt) |
| ファイル | [`package/network/utils/iwcap/src/iwcap.c`](https://github.com/openwrt/openwrt/blob/805098d8b62fdd5894738fa5080ad66347d1340b/package/network/utils/iwcap/src/iwcap.c#L190) |
| 行 | 190 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:39:30Z |

## 検出理由

```text
implicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
   184  	else
   185  	{
   186  		tv.tv_sec  = *sec;
   187  		tv.tv_usec = *usec;
   188  	}
   189  
>  190  	fhdr.ts_sec   = tv.tv_sec;
   191  	fhdr.ts_usec  = tv.tv_usec;
   192  	fhdr.incl_len = len;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: PCAPが規定している構造体におけるts_secはuint32_t型であり、2106年以降は問題になりうるが、問題を修正するにはPCAPの仕様を変更する必要がある。
