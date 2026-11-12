# coolsnowwolf/lede — package/utils/px5g-wolfssl/px5g-wolfssl.c:129

| 項目 | 値 |
|------|----|
| リポジトリ | [coolsnowwolf/lede](https://github.com/coolsnowwolf/lede) |
| ファイル | [`package/utils/px5g-wolfssl/px5g-wolfssl.c`](https://github.com/coolsnowwolf/lede/blob/fc71ece17d477b0e4f322511defebfb73931dcaa/package/utils/px5g-wolfssl/px5g-wolfssl.c#L129) |
| 行 | 129 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:34:25Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
   123    char fstr[20], tstr[20];
   124    bool pem = true;
   125    Cert newCert;
   126  #ifdef __USE_TIME_BITS64
   127    time_t to, from = time(NULL);
   128  #else
>  129    unsigned long to, from = time(NULL);
   130  #endif
   131    byte derBuf[FOURK_SZ] = {};
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: to, fromの型をtime_t型へ変更すると修正可能。

time_t型であるtime(NULL)をunsigned int型として利用している。
2106年までは問題がないが、その後time_t型の変数がunsigned int型に納まらない（33bit以上の値になる）場合に問題となる。
