# jart/cosmopolitan — examples/spawn_bench.c:139

| 項目 | 値 |
|------|----|
| リポジトリ | [jart/cosmopolitan](https://github.com/jart/cosmopolitan) |
| ファイル | [`examples/spawn_bench.c`](https://github.com/jart/cosmopolitan/blob/036845632f29034161a6d7f33b3b12bfe36f2e55/examples/spawn_bench.c#L139) |
| 行 | 139 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T15:07:31Z |

## 検出理由

```text
implicit conversion of time_t to 'unsigned long' may truncate after 2106
```

## コード

```c
   133    BENCH("mmap(128mb, MAP_SHARED) + fork() + exec(tiny)", ForkExecWait(prog));
   134    BENCH("mmap(128mb, MAP_SHARED) + posix_spawn(tiny)", PosixSpawnWait(prog));
   135    munmap(p, n);
   136  
   137    n = 128L * 1024 * 1024;
   138    p = pFillMemory(malloc(n), n);
>  139    BENCH("malloc(128mb) + fork() + exec(tiny)", ForkExecWait(prog));
   140    BENCH("malloc(128mb) + posix_spawn(tiny)", PosixSpawnWait(prog));
   141    free(p);
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: ごく短い時刻の差分計算を行っているだけなので、桁あふれの可能性は実質ない。

BENCH()マクロの中で、Ithoa()関数を使いForkExecWait(prog)の実行時間を文字列に変換している。
Ithoa()の第2引数はunsigned long型であり、この引数として渡されるToNanoseconds(SubtractTime(t2, t1))の戻り値はtime_t型である。
t2, t1はそれぞれstruct timespec型の変数で時刻を表しているが、両者の差はごくわずかだと考えられるため、ToNanoseconds(SubtractTime(t2, t1))の結果は大きな数字にならない。
このため、unsigned long型に代入しても桁あふれは起きないと考えられる。
