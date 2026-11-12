# jart/cosmopolitan — test/c11/thrd_sleep_test.c:33

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`test/c11/thrd_sleep_test.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/test/c11/thrd_sleep_test.c#L33) |
| 行 | 33 |
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
    27  
    28    timespec_get(&a, TIME_UTC);
    29    if (thrd_sleep(&dur, 0) != 0)
    30      exit(10);
    31    timespec_get(&b, TIME_UTC);
    32  
>   33    elapsed_ms = (b.tv_sec - a.tv_sec) * 1000 + (b.tv_nsec - a.tv_nsec) / 1000000;
    34    if (elapsed_ms < 90)  // must not wake appreciably early
    35      exit(11);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: ごく短い時刻の差分計算を行っているだけなので、桁あふれの可能性は実質ない。

a, bはそれぞれstruct timespec型の変数で時刻を表しているが、thrd_sleep()の呼び出しで100ms程度のスリープを行っているため、b.tv_sec - a.tv_secは0か1程度の値しか取らない。誤差等は考えられるものの、elapsed_msの値は1000前後の値に収まるため、long型に代入しても桁あふれは起きないと考えられる。
