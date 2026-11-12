# jart/cosmopolitan — third_party/zip/timezone.c:663

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`third_party/zip/timezone.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/third_party/zip/timezone.c#L663) |
| 行 | 663 |
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
   657       be sure, we allow a third try, but then the loop is stopped. */
   658    bailout_cnt = 3;
   659    then = loctime;
   660    do {
   661      ltm = localtime(&then);
   662      if (ltm == (struct tm *)NULL ||
>  663          (tzoffset_adj = loctime - mkgmtime(ltm)) == 0L)
   664        break;
   665      then += tzoffset_adj;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: tzoffset_adjの値は高々-86400～+86400の範囲に限定されるため、2038年以降も正しく動作する。

ここでは、UTC時刻とローカル時刻の差を計算しており、タイムゾーンの差は高々-24時間～+24時間の範囲に収まる（現実にはもっと狭い範囲である）。
値の範囲が限定されており、2038年以降でも問題は発生しない。
