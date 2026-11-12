# ventoy/Ventoy — SQUASHFS/squashfs-tools-4.4/squashfs-tools/unsquashfs.c:921

| 項目 | 値 |
|------|----|
| リポジトリ | [ventoy/Ventoy](https://github.com/ventoy/Ventoy) |
| ファイル | [`SQUASHFS/squashfs-tools-4.4/squashfs-tools/unsquashfs.c`](https://github.com/ventoy/Ventoy/blob/25369d58843a3ca001c57703bab0365fdc9242ce/SQUASHFS/squashfs-tools-4.4/squashfs-tools/unsquashfs.c#L921) |
| 行 | 921 |
| 種別 | ファイルシステムタイムスタンプ設定 API 呼び出し |
| 検出モード | 通常 |
| y2038detect バージョン | 0.9.4 |
| スキャン日 | 2026-09-30T13:59:52Z |

## 検出理由

```text
call to utime() uses time_t timestamps; limited to 32-bit range — use utimensat() instead
```

## コード

```c
   915  
   916  int set_attributes(char *pathname, int mode, uid_t uid, gid_t guid, time_t time,
   917  	unsigned int xattr, unsigned int set_mode)
   918  {
   919  	struct utimbuf times = { time, time };
   920  
>  921  	if(utime(pathname, &times) == -1) {
   922  		EXIT_UNSQUASH_STRICT("set_attributes: failed to set time on %s, because %s\n",
   923  			pathname, strerror(errno));
```

## 確認すべきポイント

種別（ファイルシステムタイムスタンプ設定 API 呼び出し）から自動生成した確認事項です。断定的な修正方法ではありません。

- メッセージ内で示された代替 API（`utimensat()` / `futimens()`）への置き換えを検討してください
- 代替 API は引数の構成が異なります（`struct timeval[2]` ではなく`struct timespec[2]` を使う等）。呼び出し側の変更が必要です

## 確認結果

判定: wontfix
コメント: SquashFSの仕様上2106年2月7日06:28:15(UTC)までは問題が発覚しない。それ以降のタイムスタンプを扱う場合は注意が必要である。
y2038detectはutimensat()について言及していますが、この問題はSquashFSの仕様に依存しているため、utimensat()に置き換えても修正はできない。
