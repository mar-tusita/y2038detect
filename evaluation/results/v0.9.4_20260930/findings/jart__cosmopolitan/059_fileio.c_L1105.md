# jart/cosmopolitan — third_party/zip/fileio.c:1105

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/zip/fileio.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/zip/fileio.c#L1105) |
| 行 | 1105 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
  1099    t_even = (time_t)(((unsigned long)(*t) + 1) & (~1));
  1100                                  /* Round up to even seconds. */
  1101    s = localtime(&t_even);       /* Use local time since MSDOS does. */
  1102    if (s == (struct tm *)NULL) {
  1103        /* time conversion error; use current time as emergency value
  1104           (assuming that localtime() does at least accept this value!) */
> 1105        t_even = (time_t)(((unsigned long)time(NULL) + 1) & (~1));
  1106        s = localtime(&t_even);
  1107    }
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: time(NULL)の戻り値をunsigned long型へキャストしないようにすると修正可能。

WindowsなどのLLP64データモデル（long型は32bit）では、2106年以降に桁あふれが起きる可能性がある。
なお、FATの仕様上、表現できる時刻は2107年12月31日23:59:58まで。それ以降のタイムスタンプを扱う場合は注意が必要である。
