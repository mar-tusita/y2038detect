# allinurl/goaccess — src/wsauth.c:138

| 項目 | 値 |
|------|----|
| リポジトリ | [allinurl/goaccess](https://github.com/allinurl/goaccess) |
| ファイル | [`src/wsauth.c`](https://github.com/allinurl/goaccess/blob/2bd25460a2a23ae8c66354a9c892fff3f9fff392/src/wsauth.c#L138) |
| 行 | 138 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:54Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   132  create_jwt_token (void) {
   133    char *jwt = NULL, *payload = NULL, report_id[50];
   134    time_t now = time (NULL);
   135    struct tm *jwt_now_tm = localtime (&now);
   136    // Configure token lifetime in seconds
   137    long token_lifetime = conf.ws_auth_expire > 0 ? conf.ws_auth_expire : DEFAULT_EXPIRE_TIME;
>  138    long iat = now;
   139    long exp = now + token_lifetime;
   140  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: iatをlong型からtime_t型に変更することで修正可能。

time(NULL)の結果をlong型の変数に代入している。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
この変数が使われるcreate_jwt_payload()では、snprintf()で出力する際にフォーマット指定子%ldが使われている。
iatをtime_t型に変更する場合は、フォーマット指定子%ldを64bit整数型であるint64_t型（snprintf("%" PRId64 "\n", num)）に変更する必要がある。
