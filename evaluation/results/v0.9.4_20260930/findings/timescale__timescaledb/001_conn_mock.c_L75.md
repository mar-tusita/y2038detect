# timescale/timescaledb — test/src/net/conn_mock.c:75

| 項目 | 値 |
|------|----|
| リポジトリ | [timescale/timescaledb](https://github.com/timescale/timescaledb) |
| ファイル | [`test/src/net/conn_mock.c`](https://github.com/timescale/timescaledb/blob/14583bd4905cb18897983847f6db42816998e168/test/src/net/conn_mock.c#L75) |
| 行 | 75 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:38Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
    69  	return bytes_to_read;
    70  }
    71  
    72  static int
    73  mock_init(Connection *conn)
    74  {
>   75  	srand(time(0));
    76  	return 0;
    77  }
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(0)は単純な乱数の種として使われるだけで、時刻を考慮していない。

なおsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
