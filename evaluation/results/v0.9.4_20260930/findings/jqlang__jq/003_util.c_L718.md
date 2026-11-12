# jqlang/jq — src/util.c:718

| 項目 | 値 |
|------|----|
| リポジトリ | [jqlang/jq](https://github.com/jqlang/jq) |
| ファイル | [`src/util.c`](https://github.com/jqlang/jq/blob/df924eae91af10cc236a907cdadd97813827aa1f/src/util.c#L718) |
| 行 | 718 |
| 種別 | tm_year 上限比較 |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:30:01Z |

## 検出理由

```text
tm_year compared with 68 (year 1968): upper bound excludes dates beyond 1968
```

## コード

```c
   712              const int year = split_year ? tm->tm_year : 0;
   713  
   714              bp = (const unsigned char *)strptime((const char *)bp,
   715                                  new_fmt, tm);
   716              LEGAL_ALT(ALT_E);
   717              tm->tm_year += year;
>  718              if (split_year && tm->tm_year % (2000 - TM_YEAR_BASE) <= 68)
   719                  tm->tm_year -= 2000 - TM_YEAR_BASE;
   720              split_year = 1;
```

## 確認すべきポイント

種別（tm_year 上限比較）から自動生成した確認事項です。断定的な修正方法ではありません。

- これは Y2K 対応でよく使われた「2桁年」判定（`tm_year < 69` で 1900年代/2000年代を切り替える等）のパターンではありませんか？
- この判定は暗黙的に `time_t` の表現可能年（32-bit なら 1901〜2038年）を前提にしていませんか？ 64-bit `time_t` 環境ではこの前提が崩れている可能性があります
- 比較対象の年やしきい値が、実際に想定しているシステムの制約と一致しているか見直してください

## 確認結果

判定: true-positive
コメント: 2069年以降に対応するためには、tm_yearの計算方法を変更する必要がある。

2038年で直ちに問題とはならないものの、2069年のとき（下2桁が69となるため）1969年だと解釈してしまう。
