# openssl/openssl — doc/designs/ddd/ddd-02-conn-nonblocking.c:311

| 項目 | 値 |
|------|----|
| リポジトリ | [openssl/openssl](https://github.com/openssl/openssl) |
| ファイル | [`doc/designs/ddd/ddd-02-conn-nonblocking.c`](https://github.com/openssl/openssl/blob/0a396bdd1ce5dc773b7684de56b6f1c7bae1f077/doc/designs/ddd/ddd-02-conn-nonblocking.c#L311) |
| 行 | 311 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:37:47Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   305      t->tv_sec = ms < 0 ? -1 : ms / 1000;
   306      t->tv_usec = ms < 0 ? 0 : (ms % 1000) * 1000;
   307  }
   308  
   309  static inline int timeval_to_ms(const struct timeval *t)
   310  {
>  311      return t->tv_sec * 1000 + t->tv_usec / 1000;
   312  }
   313  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timeval_to_ms()の引数はイベントまでの残り時間を表す変数であり、時刻を考慮していない。
