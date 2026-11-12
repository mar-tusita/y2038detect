# coolsnowwolf/lede — package/firmware/quantenna/src/qcsapi_rpc/generated/qcsapi_rpc_clnt_adapter.c:22394

| 項目 | 値 |
|------|----|
| リポジトリ | [coolsnowwolf/lede](https://github.com/coolsnowwolf/lede) |
| ファイル | [`package/firmware/quantenna/src/qcsapi_rpc/generated/qcsapi_rpc_clnt_adapter.c`](https://github.com/coolsnowwolf/lede/blob/fc71ece17d477b0e4f322511defebfb73931dcaa/package/firmware/quantenna/src/qcsapi_rpc/generated/qcsapi_rpc_clnt_adapter.c#L22394) |
| 行 | 22394 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:34:25Z |

## 検出理由

```text
explicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
  22388  	memset(&__req, 0, sizeof(__req));
  22389  	memset(&__resp, 0, sizeof(__resp));
  22390  	__rpc_string __rpcifname = {(char *)ifname};
  22391  	__rpc_string *p__rpcifname = (ifname) ? &__rpcifname : NULL;
  22392  	__req.ifname = p__rpcifname;
  22393  
> 22394  	__req.timeout = (uint32_t)timeout;
  22395  
  22396  	if (debug) { fprintf(stderr, "%s:%d %s pre\n", __FILE__, __LINE__, __FUNCTION__); }
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timeoutはタイムアウト時間を秒単位で指定するための引数であり、時刻を考慮していない。
