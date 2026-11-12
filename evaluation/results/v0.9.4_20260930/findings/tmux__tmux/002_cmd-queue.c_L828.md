# tmux/tmux — cmd-queue.c:828

| 項目 | 値 |
|------|----|
| リポジトリ | [tmux/tmux](https://github.com/tmux/tmux) |
| ファイル | [`cmd-queue.c`](https://github.com/tmux/tmux/blob/e778f7f805a3d159be00c9048e1a692c5727edbc/cmd-queue.c#L828) |
| 行 | 828 |
| 種別 | 暗黙変換（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:26:31Z |

## 検出理由

```text
implicit conversion of time_t to 'long' may truncate after 2038
```

## コード

```c
   822  
   823  /* Print a guard line. */
   824  void
   825  cmdq_guard(struct cmdq_item *item, const char *guard, int flags)
   826  {
   827  	struct client	*c = item->client;
>  828  	long		 t = item->time;
   829  	u_int		 number = item->number;
   830  
```

## 確認すべきポイント

種別（暗黙変換（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: true-positive
コメント: tの型をtime_t型とし、control_write()の%ldをPRId64に変更すると修正可能。

time_t型の変数がprintf()で出力される際、long型へキャストしたのちフォーマット指定子%ldが用いられている。
WindowsなどのLLP64データモデル（long型は32bit）では、2038年以降に桁あふれが起きる可能性がある。
64bit整数型であるint64_t型（printf("%" PRId64 "\n", num)）として出力するのが適切。
