# robertdavidgraham/masscan — src/out-binary.c:245

| 項目 | 値 |
|------|----|
| リポジトリ | [robertdavidgraham/masscan](https://github.com/robertdavidgraham/masscan) |
| ファイル | [`src/out-binary.c`](https://github.com/robertdavidgraham/masscan/blob/94e118ccd26c2fb263fb2fe731043f7b3240723c/src/out-binary.c#L245) |
| 行 | 245 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:43:38Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned char' may truncate after 2038
```

## コード

```c
   239          foo[2] = (unsigned char)((length + HeaderLength) & 0x7F);
   240          i = 3;
   241      }
   242  
   243      /* [TIMESTAMP] field */
   244      foo[i+0] = (unsigned char)(timestamp>>24);
>  245      foo[i+1] = (unsigned char)(timestamp>>16);
   246      foo[i+2] = (unsigned char)(timestamp>> 8);
   247      foo[i+3] = (unsigned char)(timestamp>> 0);
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: time_t型変数の値を格納する場所としてunsigned char型4つ分しか確保されていない。
time_t型の変数を格納するには、unsigned char型8つ分が必要。

foo[i+0]〜foo[i+3]の4バイトにtime_t型の変数を格納している。time_t型の変数は64bit整数型であるため、foo[i+0]〜foo[i+7]の8バイトに格納する必要がある。
foo[]の長さが変化するため、foo[i+4]以降の格納先も変更が必要で、foo[]を参照する側の修正も必要。
