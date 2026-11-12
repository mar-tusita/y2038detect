# curl/curl — lib/cookie.c:55

| 項目 | 値 |
|------|----|
| リポジトリ | [curl/curl](https://github.com/curl/curl) |
| ファイル | [`lib/cookie.c`](https://github.com/curl/curl/blob/872c313d7647ac437c83128e6bea7a8ed16cd2ef/lib/cookie.c#L55) |
| 行 | 55 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:27:25Z |

## 検出理由

```text
implicit conversion of time_t to 'timediff_t' may truncate after 2038
```

## コード

```c
    49     For the sake of easier testing, align the capped time to an even 60 second
    50     boundary.
    51  */
    52  static void cap_expires(time_t now, struct Cookie *co)
    53  {
    54    if(co->expires && (TIME_T_MAX - COOKIES_MAXAGE - 30) > now) {
>   55      timediff_t cap = now + COOKIES_MAXAGE;
    56      if(co->expires > cap) {
    57        cap += 30;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timediff_tは64bit整数型として定義されており、2038年以降でも問題は発生しない。

include/curl/system.hにおいてtypedef CURL_TYPEOF_CURL_OFF_T curl_off_t;として型定義が行われている。
多くのアーキテクチャを考慮してCURL_TYPEOF_CURL_OFF_Tが定義されているが、32bitアーキテクチャにおいても64bit整数型となるように定義されている。
