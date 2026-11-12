# openssl/openssl — apps/s_time.c:370

| 項目 | 値 |
|------|----|
| リポジトリ | [openssl/openssl](https://github.com/openssl/openssl) |
| ファイル | [`apps/s_time.c`](https://github.com/openssl/openssl/blob/0a396bdd1ce5dc773b7684de56b6f1c7bae1f077/apps/s_time.c#L370) |
| 行 | 370 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:37:47Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   364      if ((fd = SSL_get_fd(scon)) >= 0)
   365          BIO_closesocket(fd);
   366  
   367      nConn = 0;
   368      totalTime = 0.0;
   369  
>  370      finishtime = (long)time(NULL) + maxtime;
   371  
   372      printf("starting\n");
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: finishtimeをlong型からtime_t型に変更すると修正可能。

time(NULL)の結果にmaxtime（初期値30）を加算した結果をlong型の変数に代入している。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
