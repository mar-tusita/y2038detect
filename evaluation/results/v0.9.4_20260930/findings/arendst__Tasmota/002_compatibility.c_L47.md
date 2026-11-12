# arendst/Tasmota — lib/lib_rf/RF24/utility/SPIDEV/compatibility.c:47

| 項目 | 値 |
|------|----|
| リポジトリ | [arendst/Tasmota](https://github.com/arendst/Tasmota) |
| ファイル | [`lib/lib_rf/RF24/utility/SPIDEV/compatibility.c`](https://github.com/arendst/Tasmota/blob/7a2fbbe7ba168f24eccff429057bfc4766e869a4/lib/lib_rf/RF24/utility/SPIDEV/compatibility.c#L47) |
| 行 | 47 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:48:24Z |

## 検出理由

```text
implicit conversion of time_t to 'uint32_t' may truncate after 2106
```

## コード

```c
    41  }
    42  
    43  uint32_t __millis()
    44  {
    45  	//gettimeofday(&end, NULL);
    46  	clock_gettime(CLOCK_MONOTONIC_RAW,&end);
>   47      seconds  = end.tv_sec  - start.tv_sec;
    48      useconds = (end.tv_nsec - start.tv_nsec)/1000;
    49  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
secondsの型をlong型からdouble型ないしint64_t型に変更するとより安全かもしれない。

secondsの型はlong型。time_t型の2変数の差分がsecondsに格納される。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
