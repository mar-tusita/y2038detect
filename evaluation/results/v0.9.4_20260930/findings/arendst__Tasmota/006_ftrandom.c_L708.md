# arendst/Tasmota — lib/libesp32_lvgl/freetype/src/tools/ftrandom/ftrandom.c:708

| 項目 | 値 |
|------|----|
| リポジトリ | [arendst/Tasmota](https://github.com/arendst/Tasmota) |
| ファイル | [`lib/libesp32_lvgl/freetype/src/tools/ftrandom/ftrandom.c`](https://github.com/arendst/Tasmota/blob/7a2fbbe7ba168f24eccff429057bfc4766e869a4/lib/libesp32_lvgl/freetype/src/tools/ftrandom/ftrandom.c#L708) |
| 行 | 708 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:48:24Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   702      }
   703  
   704      if ( testfile )
   705        ExecuteTest( testfile );         /* This should never return */
   706  
   707      time( &now );
>  708      srandom( (unsigned int)now );
   709  
   710      FindFonts( dirs, exts );
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: nowは乱数の種として使われるだけで、時刻を考慮していない。

この変数はsrandom()の引数として使われている。
なおsrandom()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
