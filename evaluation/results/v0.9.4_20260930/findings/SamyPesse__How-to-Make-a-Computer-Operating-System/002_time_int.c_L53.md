# SamyPesse/How-to-Make-a-Computer-Operating-System — src/sdk/src/libc/src/time/time_int.c:53

| 項目 | 値 |
|------|----|
| リポジトリ | [SamyPesse/How-to-Make-a-Computer-Operating-System](https://github.com/SamyPesse/How-to-Make-a-Computer-Operating-System) |
| ファイル | [`src/sdk/src/libc/src/time/time_int.c`](https://github.com/SamyPesse/How-to-Make-a-Computer-Operating-System/blob/eb30f8802fac9f0f1c28d3a96bb3d402bdfc4687/src/sdk/src/libc/src/time/time_int.c#L53) |
| 行 | 53 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:57:58Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
    47              timeval -= sumofdays[ i - 1 ];
    48  
    49              break;
    50          }
    51      }
    52  
>   53      ret->tm_yday = ( int )timeval;
    54  
    55      if ( ret->tm_year % 4 == 0 ) {
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: timevalはその年の最初から何日かを表しており、0〜365の範囲に限定されるため、2038年以降でも問題は発生しない。

_gmtime()の冒頭でtimevalに対して演算が行われており、時刻を扱っていない。
