# ventoy/Ventoy — LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c:135

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c#L135) |
| 行 | 135 |
| 種別 | 複合代入（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
compound assignment of time_t to 'int' may truncate after 2038
```

## コード

```c
   129  		int leap_day = (IS_LEAP_YEAR(year) && i == 2);
   130  		int leap_sub = (IS_LEAP_YEAR(year) && i >= 3);
   131  
   132  		if (i == 12 || days - leap_sub < days_in_year[i + 1] + leap_day)
   133  		{
   134  			month = i;
>  135  			days -= days_in_year[i] + leap_sub;
   136  			break;
   137  		}
```

## 確認すべきポイント

種別（複合代入（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: days_in_year[] の値はその月までに何日が経過したかを表す配列であり、時刻を扱っていない。

days_in_year[]はtime_t型の配列であるが、その値は[0, 0,  31,  59,  90, 120, 151, 181, 212, 243, 273, 304, 334]として定義されており、その月までに何日が経過したかを表す。
値の範囲が限定されており、2038年以降でも問題は発生しない。
