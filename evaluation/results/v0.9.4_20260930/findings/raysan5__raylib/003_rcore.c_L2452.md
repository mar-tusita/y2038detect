# raysan5/raylib — src/rcore.c:2452

| 項目 | 値 |
|------|----|
| リポジトリ | [raysan5/raylib](https://github.com/raysan5/raylib) |
| ファイル | [`src/rcore.c`](https://github.com/raysan5/raylib/blob/10a889c482bc001533536162cc2cc9d193845eae/src/rcore.c#L2452) |
| 行 | 2452 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:31:51Z |

## 検出理由

```text
explicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
  2446      struct stat result = { 0 };
  2447      long modTime = 0;
  2448  
  2449      if (stat(fileName, &result) == 0)
  2450      {
  2451          time_t mod = result.st_mtime;
> 2452          modTime = (long)mod;
  2453      }
  2454  
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: modTimeをlong型からtime_t型に変更することで修正可能。

stat()をで取得したファイルの時刻をmodに代入した後、その値をlong型の変数に代入している。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
