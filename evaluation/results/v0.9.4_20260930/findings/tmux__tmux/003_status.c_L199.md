# tmux/tmux — status.c:199

| 項目 | 値 |
|------|----|
| リポジトリ | [tmux/tmux](https://github.com/tmux/tmux) |
| ファイル | [`status.c`](https://github.com/tmux/tmux/blob/e778f7f805a3d159be00c9048e1a692c5727edbc/status.c#L199) |
| 行 | 199 |
| 種別 | 明示キャスト（narrowing） |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T14:26:31Z |

## 検出理由

```text
explicit conversion of time_t to 'int' may truncate after 2038
```

## コード

```c
   193  
   194  	timerclear(&tv);
   195  	tv.tv_sec = options_get_number(s->options, "status-interval");
   196  
   197  	if (tv.tv_sec != 0)
   198  		evtimer_add(&c->status.timer, &tv);
>  199  	log_debug("client %p, status interval %d", c, (int)tv.tv_sec);
   200  }
   201  
```

## 確認すべきポイント

種別（明示キャスト（narrowing））から自動生成した確認事項です。断定的な修正方法ではありません。

- 代入元の `time_t` 値は、この時点で範囲限定されていませんか？（剰余演算 `%`、または除算と累積値の減算を繰り返すことで、すでに小さい値に縮退している場合は安全な可能性があります。周辺のコードを確認してください）
- 代入先の型は自由に変更できますか？（POSIX 標準の構造体（`struct tm` 等）のフィールドや、外部 API・ネットワークプロトコルで固定されたサイズの場合、型を広げる選択肢自体がないことがあります）
- 上記のいずれにも該当しない場合は、代入先の型を `time_t` または 64-bit 整数型（`int64_t` 等）に広げることを検討してください

## 確認結果

判定: false-positive
コメント: この変数は通知に関する変数であって、時刻を考慮していない。
