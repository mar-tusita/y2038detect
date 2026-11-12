# arendst/Tasmota — lib/libesp32/berry/src/be_timelib.c:15

| 項目 | 値 |
|------|----|
| リポジトリ | [arendst/Tasmota](https://github.com/arendst/Tasmota) |
| ファイル | [`lib/libesp32/berry/src/be_timelib.c`](https://github.com/arendst/Tasmota/blob/7a2fbbe7ba168f24eccff429057bfc4766e869a4/lib/libesp32/berry/src/be_timelib.c#L15) |
| 行 | 15 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:48:24Z |

## 検出理由

```text
explicit conversion of time_t to 'bint' may truncate after 2038
```

## コード

```c
     9  #include <time.h>
    10  
    11  #if BE_USE_TIME_MODULE
    12  
    13  static int m_time(bvm *vm)
    14  {
>   15      be_pushint(vm, (bint)time(NULL));
    16      be_return(vm);
    17  }
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: wontfix
コメント: bintの型は32bit、この環境上で動作するBerryに64bit幅の変数が存在していないため、時刻をどう扱うかを決定する必要がある。

lib/libesp32/berry/src/berry.hにてbintの型はlongとして定義されるが、これは32bit幅である。
一般的なBerryでは64bit幅であるが、おそらくTasmota側でBerryを取り込む際に変更したと考えられる。
lib/libesp32/berry/src/be_object.hにてunion bvaldataが定義されるが、bintを32bit幅にするとこの構造体のサイズが小さくなるため、変更した積極的理由があったのではないかと考えられる。
