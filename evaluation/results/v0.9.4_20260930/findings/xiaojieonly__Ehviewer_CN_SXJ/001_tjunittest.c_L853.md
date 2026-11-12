# xiaojieonly/Ehviewer_CN_SXJ — app/src/main/cpp/jni/libjpeg-turbo/libjpeg-turbo/tjunittest.c:853

| 項目 | 値 |
|------|----|
| リポジトリ | [xiaojieonly/Ehviewer_CN_SXJ](https://github.com/xiaojieonly/Ehviewer_CN_SXJ) |
| ファイル | [`app/src/main/cpp/jni/libjpeg-turbo/libjpeg-turbo/tjunittest.c`](https://github.com/xiaojieonly/Ehviewer_CN_SXJ/blob/b26fe03781f5b5d066e30fd83c8afe27c4ab4ea8/app/src/main/cpp/jni/libjpeg-turbo/libjpeg-turbo/tjunittest.c#L853) |
| 行 | 853 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | `--strict` 限定 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:49:43Z |

## 検出理由

```text
explicit conversion of time_t to 'unsigned int' may truncate after 2106
```

## コード

```c
   847  
   848  int main(int argc, char *argv[])
   849  {
   850    int i, num4bf = 5;
   851  
   852  #ifdef _WIN32
>  853    srand((unsigned int)time(NULL));
   854  #endif
   855    if (argc > 1) {
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: time(NULL)は単純な乱数の種として使われるだけで、時刻を考慮していない。

またsrand()の第1引数はunsigned int型であるため、乱数の種として考えた場合であっても、2106年までは重複した値になることはない。
