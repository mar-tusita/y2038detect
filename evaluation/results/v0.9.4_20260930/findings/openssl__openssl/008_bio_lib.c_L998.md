# openssl/openssl — crypto/bio/bio_lib.c:998

| 項目 | 値 |
|------|----|
| リポジトリ | [openssl/openssl](https://github.com/openssl/openssl) |
| ファイル | [`crypto/bio/bio_lib.c`](https://github.com/openssl/openssl/blob/0a396bdd1ce5dc773b7684de56b6f1c7bae1f077/crypto/bio/bio_lib.c#L998) |
| 行 | 998 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:37:47Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   992          if (ret != -1)
   993              return ret;
   994      }
   995  #endif
   996      /* fall back to polling since no sockets are available */
   997  
>  998      sec_diff = (long)(max_time - time(NULL)); /* might overflow */
   999      if (sec_diff < 0)
  1000          return 0; /* clearly timeout */
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
sec_diffの型をlong型からdouble型ないしint64_t型に変更するとより安全かもしれない。

sec_diffの型はlong型。time_t型の2変数の差分がsec_diffに格納される。
WindowsなどのLLP64データモデル（long型は32bit）では、通常は起き得ないがsec_diffの値がlong型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
