# git/git — date.c:942

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`date.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/date.c#L942) |
| 行 | 942 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   936  		/* gmtime_r() in match_digit() may have clobbered it */
   937  		tm.tm_isdst = -1;
   938  		temp_time = mktime(&tm);
   939  		if ((time_t)*timestamp > temp_time) {
   940  			*offset = ((time_t)*timestamp - temp_time) / 60;
   941  		} else {
>  942  			*offset = -(int)((temp_time - (time_t)*timestamp) / 60);
   943  		}
   944  	}
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 代入する値は値の範囲が限定されており、2038年以降でも問題は発生しない。
