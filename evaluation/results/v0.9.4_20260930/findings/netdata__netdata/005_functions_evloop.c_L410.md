# netdata/netdata — src/libnetdata/functions_evloop/functions_evloop.c:410

| 項目 | 値 |
|------|----|
| リポジトリ | [netdata/netdata](https://github.com/netdata/netdata) |
| ファイル | [`src/libnetdata/functions_evloop/functions_evloop.c`](https://github.com/netdata/netdata/blob/44d5e9c9fd651ec12b385c6ea7e5dab6db1bafc4/src/libnetdata/functions_evloop/functions_evloop.c#L410) |
| 行 | 410 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:58:40Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   404  
   405      CLEAN_BUFFER *result = buffer_create(1024, NULL);
   406      int code = dyncfg_node_find_and_call(wg->dyncfg.nodes, transaction, function, stop_monotonic_ut,
   407                                           cancelled, payload, access, source, result);
   408  
   409      netdata_mutex_lock(wg->stdout_mutex);
>  410      pluginsd_function_result_begin_to_stdout(transaction, code, content_type_id2string(result->content_type), result->expires);
   411      printf("%s", buffer_tostring(result));
   412      pluginsd_function_result_end_to_stdout();
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: pluginsd_function_result_begin_to_stdout()マクロ中で使われる%ldをPRId64に変更すると修正可能。

time_t型の変数がfprintf()で出力される際、long int型へキャストしたのちフォーマット指定子%ldが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
64bit整数型であるint64_t型（fprintf("%" PRId64 "\n", num)）として出力するのが適切。
