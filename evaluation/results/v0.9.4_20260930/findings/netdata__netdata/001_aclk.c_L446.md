# netdata/netdata — src/aclk/aclk.c:446

| 項目 | 値 |
|------|----|
| リポジトリ | [netdata/netdata](https://github.com/netdata/netdata) |
| ファイル | [`src/aclk/aclk.c`](https://github.com/netdata/netdata/blob/44d5e9c9fd651ec12b385c6ea7e5dab6db1bafc4/src/aclk/aclk.c#L446) |
| 行 | 446 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:58:40Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
   440          return 60 * MSEC_PER_SEC;
   441      }
   442  
   443      now = now_monotonic_sec();
   444      if (aclk_block_until) {
   445          if (now < aclk_block_until) {
>  446              recon_delay = aclk_block_until - now;
   447              recon_delay *= MSEC_PER_SEC;
   448              aclk_block_until = 0;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: clock_gettime(CLOCK_MONOTONIC)は時刻を扱っていない。

aclk_block_until, nowの変数は、now_monotonic_sec()の戻り値が代入されている。
変数はtime_t型で定義されているが、now_monotonic_sec()の中ではclock_gettime(CLOCK_MONOTONIC)が呼ばれており、その値が返される。
