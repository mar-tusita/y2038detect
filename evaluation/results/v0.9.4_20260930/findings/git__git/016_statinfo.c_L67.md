# git/git — statinfo.c:67

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`statinfo.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/statinfo.c#L67) |
| 行 | 67 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
    61  }
    62  
    63  int match_stat_data(const struct stat_data *sd, struct stat *st)
    64  {
    65  	int changed = 0;
    66  
>   67  	if (sd->sd_mtime.sec != (unsigned int)st->st_mtime)
    68  		changed |= MTIME_CHANGED;
    69  	if (trust_ctime && check_stat &&
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: stat()の出力結果を32bit整数と比較しているが、桁あふれの問題は想定しており、問題はない。

statinfo.hでstruct cache_timeを定義する際、 The "cache_time" is just the low 32 bits of the time. It doesn't matter if it overflows - we only check it for equality in the 32 bits we save. とコメントがなされている。
