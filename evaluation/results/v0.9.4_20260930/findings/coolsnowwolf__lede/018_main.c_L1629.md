# coolsnowwolf/lede — package/wwan/app/fibocom-dial/src/main.c:1629

| 項目 | 値 |
|------|----|
| リポジトリ | [coolsnowwolf/lede](https://github.com/coolsnowwolf/lede) |
| ファイル | [`package/wwan/app/fibocom-dial/src/main.c`](https://github.com/coolsnowwolf/lede/blob/fc71ece17d477b0e4f322511defebfb73931dcaa/package/wwan/app/fibocom-dial/src/main.c#L1629) |
| 行 | 1629 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:34:25Z |

## 検出理由

```text
implicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
  1623                  }
  1624  #ifdef CONFIG_RESET_RADIO
  1625                  if( ((profile.ipv4_flag)&&(IPv4ConnectionStatus != QWDS_PKT_DATA_CONNECTED))||
  1626                      ((profile.ipv6_flag)&&(IPV6ConnectionStatus != QWDS_PKT_DATA_CONNECTED)))
  1627                      {
  1628                          gettimeofday(&nowTime, (struct timezone *)NULL);
> 1629                          if( ((abs(nowTime.tv_sec - FailDailRadioTime.tv_sec) > CONFIG_RESET_RADIO))
  1630                              &&(FailDailRadioTime.tv_sec > resetRadioTime.tv_sec)){
  1631                          resetRadioTime = nowTime;
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: 実用上の問題はない。
abs()からllabs()に変更すると安全かもしれない。

time_t型の2変数の差分がabs()の引数として渡されている。
abs()はint型の引数を受け取るところ、可能性はおそらくないが、nowTime.tv_sec - FailDailRadioTime.tv_secの値がint型の範囲を超える可能性が否定できない。
llabs()を使用することで、64bitの整数値を安全に扱える。
