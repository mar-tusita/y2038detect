# jart/cosmopolitan — third_party/readline/input.c:640

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/readline/input.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/readline/input.c#L640) |
| 行 | 640 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   634  	(current_time.tv_sec == timeout_point.tv_sec &&
   635  	 current_time.tv_usec >= timeout_point.tv_usec))
   636      return 0;
   637  
   638    if (secs && usecs)
   639      {
>  640        *secs = timeout_point.tv_sec - current_time.tv_sec;
   641        *usecs = timeout_point.tv_usec - current_time.tv_usec;
   642        if (timeout_point.tv_usec < current_time.tv_usec)
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
secsをunsigned int *型からdouble型ないしint64_t型に変更するとより安全かもしれない。

secsはunsigned int *型。time_t型の2変数の差分がsecsに格納される。
通常は起き得ないがsecsの値がunsigned int型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
