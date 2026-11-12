# coolsnowwolf/lede — scripts/config/conf.c:109

| 項目 | 値 |
|------|----|
| リポジトリ | [coolsnowwolf/lede](https://github.com/coolsnowwolf/lede) |
| ファイル | [`scripts/config/conf.c`](https://github.com/coolsnowwolf/lede/blob/fc71ece17d477b0e4f322511defebfb73931dcaa/scripts/config/conf.c#L109) |
| 行 | 109 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:34:25Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   103  
   104  		/*
   105  		 * Use microseconds derived seed, compensate for systems where it may
   106  		 * be zero.
   107  		 */
   108  		gettimeofday(&now, NULL);
>  109  		seed = (now.tv_sec + 1) * (now.tv_usec + 1);
   110  	}
   111  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: seedは乱数の種として使われるだけで、時刻を考慮していない。

この変数は後にsrand()の引数として使われている。
なおsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
