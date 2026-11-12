# git/git — date.c:1083

| 項目 | 値 |
|------|----|
| リポジトリ | [git/git](https://github.com/git/git) |
| ファイル | [`date.c`](https://github.com/git/git/blob/1666c1265231b0bc5f613fbbf3f0a9896cdef76e/date.c#L1083) |
| 行 | 1083 |
| 種別 | tm_year 上限比較 |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:08:03Z |

## 検出理由

```text
tm_year compared with 0 (year 1900): upper bound excludes dates beyond 1900
```

## コード

```c
  1077  	time_t n;
  1078  
  1079  	if (tm->tm_mday < 0)
  1080  		tm->tm_mday = now->tm_mday;
  1081  	if (tm->tm_mon < 0)
  1082  		tm->tm_mon = now->tm_mon;
> 1083  	if (tm->tm_year < 0) {
  1084  		tm->tm_year = now->tm_year;
  1085  		if (tm->tm_mon > now->tm_mon)
```

## 確認すべきポイント

種別（tm_year 上限比較）から自動生成した確認事項です。断定的な修正方法ではありません。

- これは Y2K 対応でよく使われた「2桁年」判定（`tm_year < 69` で 1900年代/2000年代を切り替える等）のパターンではありませんか？
- この判定は暗黙的に `time_t` の表現可能年（32-bit なら 1901〜2038年）を前提にしていませんか？ 64-bit `time_t` 環境ではこの前提が崩れている可能性があります
- 比較対象の年やしきい値が、実際に想定しているシステムの制約と一致しているか見直してください

## 確認結果

判定: false-positive
コメント: 変数が初期化されているか確認しており、時刻を扱っていない。
