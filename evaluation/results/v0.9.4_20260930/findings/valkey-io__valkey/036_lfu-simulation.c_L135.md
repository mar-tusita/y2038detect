# valkey-io/valkey — utils/lru/lfu-simulation.c:135

| 項目 | 値 |
|------|----|
| リポジトリ | [valkey-io/valkey](https://github.com/valkey-io/valkey) |
| ファイル | [`utils/lru/lfu-simulation.c`](https://github.com/valkey-io/valkey/blob/7abe49a6ce6933434410022be8459cfd01cfc2bc/utils/lru/lfu-simulation.c#L135) |
| 行 | 135 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:17Z |

## 検出理由

```text
implicit conversion of time_t to 'uint16_t' may truncate after 2038
```

## コード

```c
   129  
   130          /* Simulate the addition of new entries at positions between
   131           * 10 and 19, a random one every 10 seconds. */
   132          if (new_entry_time <= now) {
   133              idx = 10+(rand()%10);
   134              entries[idx].counter = LFU_INIT_VAL;
>  135              entries[idx].decrtime = to_16bit_minutes(time(NULL));
   136              entries[idx].hits = 0;
   137              entries[idx].ctime = time(NULL);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)の値を意図的に16bitの範囲内に切り捨てて使っているため、2038年以降でも問題は発生しない。

to_16bit_minutes(x)は((x/60) & 65535)と定義されており、LFUの減算タイミングを計算するために使われていて、時刻それ自体を保持するわけではない。
