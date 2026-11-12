# jart/cosmopolitan — third_party/ncurses/lib_twait.c:98

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/ncurses/lib_twait.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/ncurses/lib_twait.c#L98) |
| 行 | 98 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
    92      } else {
    93  	/* .tv_sec and .tv_usec are unsigned, be careful when subtracting */
    94  	if (t0->tv_usec > t1.tv_usec) {
    95  	    t1.tv_usec += 1000000;	/* Convert 1s in 1e6 microsecs */
    96  	    t1.tv_sec--;
    97  	}
>   98  	res = (t1.tv_sec - t0->tv_sec) * 1000
    99  	    + (t1.tv_usec - t0->tv_usec) / 1000;
   100      }
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
resの型をlong型からdouble型ないしint64_t型に変更するとより安全かもしれない。

resの型はlong型。time_t型の2変数の差分がミリ秒単位でresに格納される。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがresの値がlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
