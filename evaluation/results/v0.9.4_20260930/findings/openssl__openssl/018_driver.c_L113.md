# openssl/openssl — test/testutil/driver.c:113

| 項目 | 値 |
|------|----|
| リポジトリ | [openssl/openssl](https://github.com/openssl/openssl) |
| ファイル | [`test/testutil/driver.c`](https://github.com/openssl/openssl/blob/0a396bdd1ce5dc773b7684de56b6f1c7bae1f077/test/testutil/driver.c#L113) |
| 行 | 113 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:37:47Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   107  }
   108  
   109  static void set_seed(int s)
   110  {
   111      seed = s;
   112      if (seed <= 0)
>  113          seed = (int)time(NULL);
   114      test_random_seed(seed);
   115  }
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: 負数にならないよう、キャスト先をint型からunsigned int型に変更すると修正可能。

seedが0もしくは負数である場合にseedへ(int)time(NULL)の値を代入するが、2038年以降にこの値が負数になる。
test_random_seed()の引数はunsigned int型であるため、負数を与えることが直ちに問題にならない可能性がある一方、112行目のif文の条件節並びにsetup_test_framework()冒頭での処理を考えると、set_seed()の引数には負数が与えられないことが想定される。
113行目でseedの値を決定する際、負数とならないようにするためには、キャスト先をint型からunsigned int型に変更することが適切である。
