# mpv-player/mpv — video/out/vo_gpu_next.c:2097

| 項目 | 値 |
|------|----|
| リポジトリ | [mpv-player/mpv](https://github.com/mpv-player/mpv) |
| ファイル | [`video/out/vo_gpu_next.c`](https://github.com/mpv-player/mpv/blob/f239c2dd767ee52729f73dda4f6c9face0ca7d56/video/out/vo_gpu_next.c#L2097) |
| 行 | 2097 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:29:40Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
  2091      size_t size;
  2092      time_t atime;
  2093  };
  2094  
  2095  static int compare_atime(const void *a, const void *b)
  2096  {
> 2097      return (((struct file_entry *)b)->atime - ((struct file_entry *)a)->atime);
  2098  }
  2099  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
compare_atime()の戻り値の型をint型からdouble型ないしint64_t型に変更するとより安全かもしれない。

time_t型の2変数の差分がcompare_atime()の結果として返される。
通常は起き得ないがcompare_atime()の戻り値がint型に納まらない可能性は否定されない。
time_t型の変数の差分の結果を格納できる型としては、difftime()の戻り値の型であるdouble型や、64bit整数型であるint64_t型が適切。
POSIX準拠環境であれば、time_t型は整数であるので、int64_t型で対応可能。
