# redis/redis — src/replication.c:3359

| 項目 | 値 |
|------|----|
| リポジトリ | [redis/redis](https://github.com/redis/redis) |
| ファイル | [`src/replication.c`](https://github.com/redis/redis/blob/8fcf3dc86600f8f1bf9bb6e7aa69b2d4e67f5957/src/replication.c#L3359) |
| 行 | 3359 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:02:00Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
  3353      }
  3354  
  3355      /* Prepare a suitable temp file for bulk transfer */
  3356      if (!useDisklessLoad()) {
  3357          while(maxtries--) {
  3358              snprintf(tmpfile,256,
> 3359                  "temp-%d.%ld.rdb",(int)server.unixtime,(long int)getpid());
  3360              dfd = open(tmpfile,O_CREAT|O_WRONLY|O_EXCL,0644);
  3361              if (dfd != -1) break;
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 一時的に使用されるファイル名に使用するために時刻が使われており、問題はない。

time_t型の変数がsnprintf()で出力される際、int型へキャストしたのちフォーマット指定子%dが用いられている。
ただここでtmpfileはその後open()で使われる一時ファイルのための名前であって、時刻が正しく表記されなくとも問題はない。
