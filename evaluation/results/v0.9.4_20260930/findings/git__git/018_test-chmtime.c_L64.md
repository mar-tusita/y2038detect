# git/git — t/helper/test-chmtime.c:64

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`t/helper/test-chmtime.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/t/helper/test-chmtime.c#L64) |
| 行 | 64 |
| 種別 | 複合代入（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
compound assignment of time_t to 'long' may truncate after 2038
```

## コード

```c
    58  	*set_time = strtol(timespec, &test, 10);
    59  	if (*test) {
    60  		return 0;
    61  	}
    62  	if ((*set_eq && *set_time < 0) || *set_eq == 2) {
    63  		time_t now = time(NULL);
>   64  		*set_time += now;
    65  	}
    66  	return 1;
```

## 確認すべきポイント

種別（複合代入（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: *set_timeをlong型からtime_t型に変更することで修正可能。

*set_timeの値にtime(NULL)の結果を加算した結果をlong型の変数に代入している。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
