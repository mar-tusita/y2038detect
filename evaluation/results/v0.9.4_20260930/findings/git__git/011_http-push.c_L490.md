# git/git — http-push.c:490

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`http-push.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/http-push.c#L490) |
| 行 | 490 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   484  {
   485  	struct remote_lock *lock = repo->locks;
   486  	time_t current_time = time(NULL);
   487  	int time_remaining;
   488  
   489  	while (lock) {
>  490  		time_remaining = lock->start_time + lock->timeout -
   491  			current_time;
   492  		if (!lock->refreshing && time_remaining < LOCK_REFRESH) {
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
time_remainingの型をint型からdouble型ないしint64_t型に変更するとより安全かもしれない。

time_t型の2変数の差分がtime_remainingに格納される。
通常は起き得ないがtime_remainingの値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
