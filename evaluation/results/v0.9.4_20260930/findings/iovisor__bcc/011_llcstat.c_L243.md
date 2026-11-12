# iovisor/bcc — libbpf-tools/llcstat.c:243

| 項目 | 値 |
|------|----|
| リポジトリ | [iovisor/bcc](https://github.com/iovisor/bcc) |
| ファイル | [`libbpf-tools/llcstat.c`](https://github.com/iovisor/bcc/blob/a3dcb9a53f289a1cabc8f6d9e33acc84e810f1c4/libbpf-tools/llcstat.c#L243) |
| 行 | 243 |
| 種別 | printf 系フォーマット不一致 |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:50Z |

## 検出理由

```text
time_t passed to printf-family function with incompatible format specifier: may truncate after 2038
```

## コード

```c
   237  		goto cleanup;
   238  	if (open_and_attach_perf_event(PERF_COUNT_HW_CACHE_REFERENCES,
   239  					env.sample_period,
   240  					obj->progs.on_cache_ref, rlinks))
   241  		goto cleanup;
   242  
>  243  	printf("Running for %ld seconds or Hit Ctrl-C to end.\n", env.duration);
   244  
   245  	signal(SIGINT, sig_handler);
```

## 確認すべきポイント

種別（printf 系フォーマット不一致）から自動生成した確認事項です。断定的な修正方法ではありません。

- `time_t` は対象プラットフォームで 64-bit ですか？ その場合、`%d` 等の 32-bit 指定子では可変長引数の型が一致せず、2038年を待たずに未定義動作（不正な値の出力）が起きる可能性があります
- フォーマット指定子を実際の型に合わせて修正してください（例: `%lld` と `(long long)` へのキャスト、または `<inttypes.h>` の `PRId64` の利用）

## 確認結果

判定: false-positive
コメント: env.durationは実行時間を表す変数であり、時刻を考慮していない。
