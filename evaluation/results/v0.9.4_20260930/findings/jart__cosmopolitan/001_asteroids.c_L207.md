# jart/cosmopolitan — examples/asteroids.c:207

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`examples/asteroids.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/examples/asteroids.c#L207) |
| 行 | 207 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   201          }
   202          putchar('\n');
   203      }
   204      
   205      // Display score and elapsed time
   206      time_t currentTime = time(NULL);
>  207      int elapsedTime = isGameOver ? finalTime : (currentTime - startTime);
   208      printf("Score: %d | Time: %02d:%02d | %s\n", score, elapsedTime / 60, elapsedTime % 60, isGameOver ? "Game Over!" : "           ");
   209  }
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
elapsedTimeの型をint型からdouble型ないしint64_t型に変更するとより安全かもしれない。

time_t型の2変数の差分がelapsedTimeに格納される。
通常は起き得ないがelapsedTimeの値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
