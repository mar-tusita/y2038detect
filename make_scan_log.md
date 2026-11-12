# make_scan_log.py

複数プロジェクトへのスキャン結果を、再現可能なマークダウン形式で記録するツールです。

## 使い方

```bash
python make_scan_log.py PROJECT VERSION -- [y2038detect のオプション] SOURCE_PATH
```

出力先: `evaluation/logs/{PROJECT}-{VERSION}.md`（`--output` で変更可）。既存ファイルを上書きするには `--force` を指定します。

**例（nginx 1.31.1 をスキャンして記録する場合）:**

```bash
python make_scan_log.py nginx 1.31.1 -- \
    --no-system-includes \
    -I /path/to/nginx_stubs \
    -I nginx-1.31.1/src/core \
    -I nginx-1.31.1/src/os/unix \
    nginx-1.31.1/src/
```

## 生成ファイルの内容

- スキャン日・y2038detect バージョン・使用オプションなどのメタデータ表
- 実行コマンド（再現用）
- クリーン / 問題あり / fatal error のファイル数サマリー
- fatal error の原因一覧（ユニーク）
- 各検出箇所のコード引用（`>` マーカー付き前後文脈）とツール出力

各検出箇所には `**解説**: <!-- TODO: 解説を記入 -->` というプレースホルダーが残るので、後から手動で問題の意味や影響を補足できます。
