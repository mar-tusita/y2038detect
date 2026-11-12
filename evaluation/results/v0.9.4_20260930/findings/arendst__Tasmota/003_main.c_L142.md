# arendst/Tasmota — lib/libesp32/JPEGDEC/linux/examples/c_cmdline/main.c:142

| 項目 | 値 |
|------|----|
| リポジトリ | [arendst/Tasmota](https://github.com/arendst/Tasmota) |
| ファイル | [`lib/libesp32/JPEGDEC/linux/examples/c_cmdline/main.c`](https://github.com/arendst/Tasmota/blob/7a2fbbe7ba168f24eccff429057bfc4766e869a4/lib/libesp32/JPEGDEC/linux/examples/c_cmdline/main.c#L142) |
| 行 | 142 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:48:24Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   136  long micros(void)
   137  {
   138  long iTime;
   139  struct timespec res;
   140  
   141      clock_gettime(CLOCK_MONOTONIC, &res);
>  142      iTime = 1000000*res.tv_sec + res.tv_nsec/1000;
   143  
   144      return iTime;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: clock_gettime(CLOCK_MONOTONIC)は時刻を扱っていない。
