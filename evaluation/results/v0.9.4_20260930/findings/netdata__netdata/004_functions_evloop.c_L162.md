# netdata/netdata — src/libnetdata/functions_evloop/functions_evloop.c:162

| 項目 | 値 |
|------|----|
| リポジトリ | [netdata/netdata](https://github.com/netdata/netdata) |
| ファイル | [`src/libnetdata/functions_evloop/functions_evloop.c`](https://github.com/netdata/netdata/blob/44d5e9c9fd651ec12b385c6ea7e5dab6db1bafc4/src/libnetdata/functions_evloop/functions_evloop.c#L162) |
| 行 | 162 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:58:40Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   156          const char *msg = "No function with this name found";
   157          bool found = false;
   158          struct rrd_functions_expectation *we;
   159          for(we = wg->expectations; we ;we = we->next) {
   160              if(strncmp(function, we->function, we->function_length) == 0) {
   161                  if(timeout <= 0)
>  162                      timeout = (int)we->default_timeout;
   163  
   164                  struct functions_evloop_worker_job t = {
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timeoutはタイムアウト時間を表しており、時刻を考慮していない。
