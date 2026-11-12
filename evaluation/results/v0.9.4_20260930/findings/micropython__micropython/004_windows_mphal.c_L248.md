# micropython/micropython — ports/windows/windows_mphal.c:248

| 項目 | 値 |
|------|----|
| リポジトリ | [micropython/micropython](https://github.com/micropython/micropython) |
| ファイル | [`ports/windows/windows_mphal.c`](https://github.com/micropython/micropython/blob/44a569b637b56764582c3b652e7bc51b53c0df1d/ports/windows/windows_mphal.c#L248) |
| 行 | 248 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:58:55Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   242      return tv.tv_sec * 1000 + tv.tv_usec / 1000;
   243  }
   244  
   245  mp_uint_t mp_hal_ticks_us(void) {
   246      struct timeval tv;
   247      gettimeofday(&tv, NULL);
>  248      return tv.tv_sec * 1000000 + tv.tv_usec;
   249  }
   250  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: mp_hal_ticks_us()の戻り値は時刻を扱っていないため、桁あふれが発生しても問題ない。

mp_hal_ticks_us()はマイクロ秒単位のごく短い経過時間を測定するための関数であり、桁あふれは起きるものの、その目的は達成できるため問題はない。
