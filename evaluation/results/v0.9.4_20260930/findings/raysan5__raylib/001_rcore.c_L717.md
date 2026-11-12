# raysan5/raylib — src/rcore.c:717

| 項目 | 値 |
|------|----|
| リポジトリ | [raysan5/raylib](https://github.com/raysan5/raylib) |
| ファイル | [`src/rcore.c`](https://github.com/raysan5/raylib/blob/10a889c482bc001533536162cc2cc9d193845eae/src/rcore.c#L717) |
| 行 | 717 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:31:51Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   711  #endif
   712  
   713      CORE.Time.frameCounter = 0;
   714      CORE.Window.shouldClose = false;
   715  
   716      // Initialize random seed
>  717      SetRandomSeed((unsigned int)time(NULL));
   718  
   719      TRACELOG(LOG_INFO, "SYSTEM: Working Directory: %s", GetWorkingDirectory());
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)は単純な乱数の種として使われるだけで、時刻を考慮していない。
