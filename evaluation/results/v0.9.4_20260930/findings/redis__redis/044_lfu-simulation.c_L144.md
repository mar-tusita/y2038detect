# redis/redis — utils/lru/lfu-simulation.c:144

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`utils/lru/lfu-simulation.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/utils/lru/lfu-simulation.c#L144) |
| 行 | 144 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   138              new_entry_time = now+10;
   139          }
   140  
   141          /* Show the first 20 entries and the last 20 entries. */
   142          if (display_time != now) {
   143              printf("=============================\n");
>  144              printf("Current minutes time: %d\n", (int)to_16bit_minutes(now));
   145              printf("Access method: %s\n",
   146                  (now-start < switch_after) ? "power-law" : "flat");
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)の値を意図的に16bitの範囲内に切り捨てて使っているので、2038年以降でも問題は発生しない。

to_16bit_minutes(x)は((x/60) & 65535)と定義されており、LFUの減算タイミングを計算するために使われていて、時刻それ自体を保持するわけではない。
