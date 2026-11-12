# openssl/openssl — ssl/bio_ssl.c:198

| 項目 | 値 |
|------|----|
| リポジトリ | [openssl/openssl](https://github.com/openssl/openssl) |
| ファイル | [`ssl/bio_ssl.c`](https://github.com/openssl/openssl/blob/0a396bdd1ce5dc773b7684de56b6f1c7bae1f077/ssl/bio_ssl.c#L198) |
| 行 | 198 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:37:47Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
   192                  r = 1;
   193              }
   194          }
   195          if ((bs->renegotiate_timeout > 0) && (!r)) {
   196              unsigned long tm;
   197  
>  198              tm = (unsigned long)time(NULL);
   199              if (tm > bs->last_time + bs->renegotiate_timeout) {
   200                  bs->last_time = tm;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: tmの型をunsigned longからtime_tに変更すると修正可能。

tmの型はunsigned long型。time(NULL)の戻り値が代入される。
WindowsなどのLLP64データモデル（unsined long型は32bit）では、2106年以降の時間を正しく扱えない。
