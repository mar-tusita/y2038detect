# ventoy/Ventoy — LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c:148

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/LinuxGUI/Ventoy2Disk/Lib/exfat/src/libexfat/time.c#L148) |
| 行 | 148 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
implicit conversion of time_t to 'uint8_t' may truncate after 2038
```

## コード

```c
   142  	min = (unix_time % SEC_IN_HOUR) / SEC_IN_MIN;
   143  	twosec = (unix_time % SEC_IN_MIN) / 2;
   144  
   145  	*date = cpu_to_le16(day | (month << 5) | (year << 9));
   146  	*time = cpu_to_le16(twosec | (min << 5) | (hour << 11));
   147  	if (centisec)
>  148  		*centisec = (unix_time % 2) * 100;
   149  }
   150  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: *centisec は 0 または 100 のいずれかの値しか取り得ないため、2038年以降も正しく動作する。

unix_time % 2 の結果は 0 または 1 のいずれかであり、*centisec に代入される値は 0 または 100 のいずれかとなる。
値の範囲が限定されており、2038年以降でも問題は発生しない。
なお、centisecはexFATにおける時刻を表すフィールドであり、仕様上0〜199の範囲の値しか取り得ない。
