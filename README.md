# y2038detect

C 言語で書かれたソースコードの **2038年問題**（Unix タイムスタンプの 32 ビット整数オーバーフロー）を静的解析で検出するツールです。

libclang による AST（抽象構文木）解析を使用するため、単純な文字列検索よりも正確に問題箇所を特定できます。

<!-- download-box -->

---

## 検出できる問題

| 種別 | 例 |
|------|----|
| `time_t` の暗黙的な narrowing 変換 | `int t = time(NULL);` |
| `time_t` の明示的なキャスト | `int t = (int)now;` |
| 関数引数への narrowing 渡し | `save(int t)` に `time(NULL)` を渡す |
| 構造体メンバへの narrowing 代入 | `s.ts = time(NULL);`（`ts` が `int` 型） |
| 関数戻り値での narrowing | `int get_ts(void) { return time(NULL); }` |
| `tm_year` の 2038 年以前への上限設定 | `t->tm_year < 138` |
| `#define` マクロ定数による上限設定 | `#define LIM 138` … `t->tm_year < LIM` |
| `time_t` と `0x7FFFFFFF` の比較 | `if (t < 0x7FFFFFFF)` （32 ビット `time_t` を前提） |
| `typedef` チェーン経由の narrowing | `typedef time_t ts_t;` … `int x = ts_t_var;` |
| 複合代入演算子での narrowing | `int v; v += time(NULL);` |
| `printf` 系関数への `time_t` 引数のフォーマット指定子不一致 | `printf("%d", time(NULL))` |
| 廃止済みタイムスタンプ設定 API の呼び出し | `utime()`・`utimes()`・`lutimes()`・`futimes()` |

---

## 動作要件

- **Python 3.10 以上**（3.12 推奨）
- **libclang Python バインディング**（`pip install libclang` で取得）
- C コンパイラは**不要**です（後述）

---

## インストール

### 1. Python のインストール

Python 3.10 以上が必要です（3.12 推奨）。[python.org](https://www.python.org/downloads/) または各 OS のパッケージマネージャでインストールしてください。

### 2. libclang のインストール

```bash
pip install libclang
```

このパッケージには Clang のライブラリが同梱されており、**別途 LLVM / Clang をインストールする必要はありません**。

### 3. ツールの取得

配布サイトから zip をダウンロードして展開します。

```text
https://mar-tusita.github.io/y2038detect/
```

展開したディレクトリに移動します。

```bash
cd y2038detect-<バージョン>
```

---

## 使い方

### 基本的な実行

```bash
python y2038detect.py <ファイル.c> [ファイル.c ...]
```

例：

```bash
python y2038detect.py src/timer.c
```

### ディレクトリ内の C ファイルをまとめてスキャン

ディレクトリを指定すると、そのディレクトリ以下のすべての `.c` ファイルを再帰的に解析します。

```bash
python y2038detect.py src/
```

### コマンドライン引数

| 引数 | 説明 |
|------|------|
| `PATH` | 解析対象の C ファイル、またはディレクトリ（複数指定可） |
| `-I DIR` | インクルードパスの追加（複数指定可） |
| `-D MACRO` | プリプロセッサマクロの定義（例: `-DFOO` `-DFOO=1`）（複数指定可） |
| `-U MACRO` | プリプロセッサマクロの未定義化（例: `-U_WIN32`）（複数指定可） |
| `--target TRIPLE` | libclang に渡すターゲットトリプル（例: `x86_64-pc-linux-gnu`） |
| `-X FLAG` | 任意の clang フラグを libclang に直接渡す（複数指定可）。`-` で始まる値は `=` で繋ぐ（例: `-X=-ferror-limit=0`） |
| `--compile-commands FILE` | `compile_commands.json` のパスを指定（後述） |
| `--exclude PATTERN` | ディレクトリスキャン時に除外するパターン（複数指定可、後述） |
| `--absolute` | ファイルパスを絶対パスで表示（デフォルトは CWD 相対） |
| `--color` | カラー出力を強制 ON（デフォルトは端末検出で自動切り替え：端末なら ON、リダイレクト・パイプ時は OFF） |
| `--no-color` | カラー出力を強制 OFF（`NO_COLOR` 環境変数をセットしても同様） |
| `--format FORMAT` | 出力形式：`default`（GCC スタイル）または `github`（GitHub Actions アノテーション）。省略時は `GITHUB_ACTIONS` 環境変数で自動判定 |
| `--json` | 結果を JSON 形式で出力 |
| `--no-system-includes` | コンパイラ自動検出によるシステムヘッダを使わず、同梱スタブのみで解析する |
| `--show-parse-errors` | libclang のパースエラー（`#include` が見つからない等を含む）を stderr に出力する（デフォルト: 非表示）。出力するだけで、解析結果は変わらない |
| `--strict` | すべてのヒューリスティック抑制を無効化する（後述） |
| `--version` | バージョンを表示して終了 |

---

## compile_commands.json を使う

CMake や [Bear](https://github.com/rizsotto/Bear) などが生成する `compile_commands.json` を渡すと、ファイルごとのインクルードパスやマクロ定義を自動で取得できます。実プロジェクトへの適用で最も効果的な方法です。

### CMake プロジェクトの場合

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build
python y2038detect.py --compile-commands build/compile_commands.json src/
```

### Bear を使う場合（CMake 以外）

```bash
bear -- make
python y2038detect.py --compile-commands compile_commands.json src/
```

各エントリから `-I`・`-D`・`-std=`・`-isystem` フラグをファイルごとに取得します（`command` 文字列と `arguments` 配列の両形式に対応）。`-I` の指定が常に優先されます。

---

## ヘッダファイルの扱い

ツールは以下の優先順位でインクルードパスを解決します：

1. **ユーザー指定の `-I`**（最優先）
2. **システムヘッダ**（Linux / macOS で gcc / clang が見つかれば自動取得）
3. **同梱スタブ**（`_stubs/` ディレクトリ）— 最終手段

### FreeBSD 向けプログラムをスキャンする場合

`_stubs_freebsd/` ディレクトリに FreeBSD 固有のスタブを用意しています。`-I` で追加するか、`pyproject.toml` に設定してください。

```bash
python y2038detect.py -I_stubs_freebsd/ src/
```

```toml
# pyproject.toml
[tool.y2038detect]
includes = ["_stubs_freebsd/"]
```

収録しているヘッダ: `sys/event.h`（kqueue）・`sys/queue.h`（LIST/TAILQ マクロ）・`sys/tree.h`・`sys/sysctl.h`・`sys/proc.h`・`sys/user.h`（kinfo_proc）・`sys/endian.h`・`sys/capsicum.h`・`sys/jail.h`・`sys/cpuset.h`・`sys/mac.h`（MAC フレームワーク）・`ifaddrs.h`・`paths.h`・`pthread_np.h`・`net/if.h`・`net/if_dl.h`

### Linux 向けプログラムをスキャンする場合

`_stubs_linux/` ディレクトリに Linux 固有ヘッダのスタブを用意しています。Linux 以外の環境（Windows・macOS）でスキャンする場合や、`_stubs/` だけでは不足する場合に追加してください。

```bash
python y2038detect.py -I_stubs_linux/ src/
```

```toml
# pyproject.toml
[tool.y2038detect]
includes = ["_stubs_linux/"]
```

収録しているヘッダ: `sys/epoll.h`・`sys/eventfd.h`・`sys/inotify.h`・`sys/prctl.h`・`sys/sendfile.h`・`sys/signalfd.h`・`sys/sysinfo.h`・`sys/timerfd.h`

---

### Windows 環境

Windows では MinGW の gcc が存在する場合でも、MinGW ヘッダとの互換性問題を避けるため**コンパイラ自動取得は行いません**。同梱スタブのみを使用します。追加の設定は不要です。

```powershell
# スタブのみで動作する
python y2038detect.py src\timer.c
```

#### MinGW のヘッダを使いたい場合

プロジェクトが MinGW 固有のヘッダを必要とする場合は、`-I` でインクルードパスを明示的に指定します。

```powershell
# MinGW のインクルードパスを確認する
gcc -x c -v -E NUL 2>&1 | Select-String "^ "

# 確認したパスを -I で指定して実行（MSYS2 の例）
python y2038detect.py -IC:\msys64\mingw64\include src\timer.c
```

複数のパスが必要な場合は `-I` を繰り返します：

```powershell
python y2038detect.py -IC:\msys64\mingw64\include -IC:\msys64\mingw64\x86_64-w64-mingw32\include src\timer.c
```

### Linux / macOS 環境

`gcc` または `clang` がインストールされている場合、ツール起動時にシステムインクルードパスを**自動取得**します。追加の設定は不要です。

```bash
# gcc / clang があれば自動でシステムヘッダを使う
python y2038detect.py src/timer.c
```

### プロジェクト固有のヘッダがある場合

独自ライブラリのヘッダなど、システムヘッダにないファイルが必要な場合は `-I` で追加します。

```bash
python y2038detect.py -I./include -I/opt/mylib/include src/timer.c
```

---

## 出力の見方

### 通常出力（デフォルト）

問題が検出された場合、GCC / Clang に近いフォーマットで出力されます。

```shell
src/timer.c:42:12: warning: implicit conversion of time_t to 'int' may truncate after 2038
    int saved = time(NULL);
               ^
src/timer.c:87:3: warning: tm_year compared with 138 (year 2038): upper bound excludes dates beyond 2038
    if (t->tm_year < 138)
    ^
```

ファイルパスはカレントディレクトリからの相対パスで表示されます。`--absolute` を指定すると絶対パスになります。

### スキャンサマリー

複数ファイルをスキャンした場合、最後にサマリー行が表示されます。

```shell
# 問題が見つかった場合
python y2038detect.py src/
src/timer.c:42:12: warning: implicit conversion of time_t to 'int' may truncate after 2038
    int saved = time(NULL);
               ^
3 issues in 2 files (45 clean)

# 問題がなかった場合
python y2038detect.py src/
All 47 files clean.
```

単一ファイルを指定した場合・`--json` モードではサマリーは表示されません。

### JSON 出力（`--json`）

CI や他のツールと連携する場合に便利です。

```bash
python y2038detect.py --json src/timer.c
```

```json
[
  {
    "file": "src/timer.c",
    "line": 42,
    "col": 12,
    "message": "implicit conversion of time_t to 'int' may truncate after 2038",
    "context": [
      { "line": 40, "text": "void update(void) {" },
      { "line": 41, "text": "    time_t now = time(NULL);" },
      { "line": 42, "text": "    int t = now;" },
      { "line": 43, "text": "}" }
    ]
  }
]
```

`context` はスキャン時点のソースの前後数行（既定でその行の前6行・後2行、ファイルの先頭・末尾では
収まる範囲に短縮）です。ファイルが読めなかった場合（例: スキャン後に削除された）は `null` に
なります。

### 終了コード

| コード | 意味 |
|--------|------|
| `0` | 問題なし |
| `1` | 問題が検出された、または libclang が致命的エラー（fatal）を報告し検出が 0 件だった |
| `2` | 内部エラーで解析できなかったファイルがある（stderr に `internal error: PATH: ...` を出力し、残りのファイルは走査を続ける。問題が検出されていても `2` が優先される） |

### GitHub Actions アノテーション出力

GitHub Actions 上では `GITHUB_ACTIONS=true` 環境変数が自動的にセットされます。y2038detect はこれを検出し、PR の差分画面に問題を inline 表示できるアノテーション形式に切り替えます。

```text
::warning file=src/timer.c,line=42,col=12::implicit conversion of time_t to 'int' may truncate after 2038
```

追加設定は不要です。ただし、`--format=default` を明示すると端末向けの通常出力に戻せます。`--json` を指定した場合は JSON が優先されます。

### 実際の検出例（評価結果）

実際のプロジェクトに適用した検出例は、[評価結果のページ](https://mar-tusita.github.io/y2038detect/evaluation/findings/)で見られます。

---

## スキャン対象の除外（`--exclude`）

`--exclude PATTERN` を使うと、ディレクトリスキャン時に特定のファイルを除外できます。`vendor/` や `third_party/` のような外部コードを丸ごとスキップするときに便利です。

```bash
# vendor/ 以下をすべて除外
python y2038detect.py --exclude 'vendor/*' src/

# 複数パターンを指定
python y2038detect.py --exclude 'vendor/*' --exclude 'third_party/*' src/

# 特定の拡張子を除外
python y2038detect.py --exclude '*.pb.c' src/
```

**パターンの仕様:**

- `fnmatch` 形式のグロブパターンを使用（`*` がワイルドカード）
- `vendor/*` のようにスラッシュなしで書いても、`src/vendor/foo.c` にマッチします（パスの末尾部分にも照合するため）
- 複数の `--exclude` を繰り返して指定できます
- コマンドラインで直接指定したファイルは除外されません（ディレクトリ展開時のみ適用）

---

## 設定ファイル（`pyproject.toml`）

`--exclude` や `--compile-commands` などのオプションをプロジェクトごとのデフォルト値として `pyproject.toml` に書いておけます。毎回コマンドラインに書く手間が省けます。

```toml
[tool.y2038detect]
compile_commands = "build/compile_commands.json"
exclude = ["vendor/*", "third_party/*"]
includes = ["include/"]
strict = true
extra_clang_args = ["-ferror-limit=0"]
```

| キー | 説明 | 対応する CLI オプション |
|------|------|----------------------|
| `compile_commands` | `compile_commands.json` のパス | `--compile-commands` |
| `exclude` | 除外パターンのリスト | `--exclude` |
| `includes` | インクルードパスのリスト | `-I` |
| `strict` | `true` でヒューリスティック抑制を無効化 | `--strict` |
| `extra_clang_args` | libclang に渡すフラグのリスト | `-X` |

`pyproject.toml` はカレントディレクトリから上位ディレクトリに向かって順に検索し、最初に見つかったものを使用します。

**優先順位**: CLI 引数 > `pyproject.toml` の設定

`exclude` と `includes` はマージされます（CLI で追加指定した値が設定ファイルの値に加算されます）。`compile_commands` は CLI 指定が優先されます。

設定ファイルが読み込まれると `note: using config from ...` を stderr に表示します。

> **Python 3.10 について**: `pyproject.toml` の読み込みには Python 3.11 以上が必要です（`tomllib` 標準ライブラリ）。Python 3.10 では設定ファイルは無視され、CLI 引数のみ有効です。

---

## `--strict` モード

通常、y2038detect はいくつかのヒューリスティックによって誤検知を抑制しています。また、デフォルトでは OFF になっている追加検出カテゴリもあります。`--strict` を指定するとこれらをすべて変更し、より厳格にスキャンします。

| 動作変更の内容 | 通常の動作 | `--strict` 時の動作 |
|--------------|------------|---------------------|
| `long` / `unsigned long` の LP64 例外 | LP64 環境（Linux 64-bit 等）では `long` が 8 バイトのため警告しない | サイズによらず常に警告 |
| Y2K 時代の `tm_year` ハック | `tm_year < 100` 未満の比較値（例: `tm_year < 69`）は Y2K 処理とみなして無視 | 0〜138 の全範囲を警告対象 |
| bounded variable tracking | `val %= 86400` の後の narrowing は時刻単位の演算とみなして無視 | bounded 判定を行わず常に警告 |
| `srand()` 等への直接引数 | `srand(time(NULL))` 等、シード消費関数への narrowing は無視 | 抑制せず常に警告 |
| `struct stat` タイムスタンプフィールドアクセス | 警告しない（ノイズが多いためデフォルト OFF） | `st_mtime`・`st_atime`・`st_ctime` 等へのアクセスを警告（ファイルシステムが 32-bit タイムスタンプしか保存しない可能性があるため） |
| `utimensat()` / `futimens()` 呼び出し | 警告しない（推奨される代替 API のため） | 警告する — 32-bit 環境では `time_t` が 32-bit に制限されるため |

```bash
python y2038detect.py --strict src/
```

`pyproject.toml` でも指定できます：

```toml
[tool.y2038detect]
strict = true
```

> **注意**: `--strict` は誤検知が増えます。`// y2038: ignore` による個別抑制は `--strict` でも有効です。

---

## 警告の抑制

### 行単位の抑制

誤検知や意図的な例外箇所は、該当行に `y2038: ignore` アノテーションを付けることで警告を抑制できます。

```c
// C++ スタイル
int t = time(NULL);  // y2038: ignore

// C スタイル
int t = time(NULL);  /* y2038: ignore */
```

大文字・小文字は区別しません（`Y2038: IGNORE` も有効です）。

### 範囲指定による一括抑制

複数行にわたる誤検知は `y2038: ignore-begin` / `y2038: ignore-end` で範囲ごと抑制できます。

```c
/* y2038: ignore-begin */
days  = (int)(val / 86400);
hours = (int)(val / 3600);
mins  = (int)(val / 60);
secs  = (int)(val % 60);
/* y2038: ignore-end */
```

`ignore-end` を省略した場合はファイル末尾まで抑制されます。

### 時間単位演算後の自動抑制

`time_t` 変数に時間単位定数（60・3600・86400・604800、および曜日計算用の7）で剰余演算を行った後の narrowing 変換は、自動的に警告が抑制されます。

```c
time_t val = time(NULL);
val %= 86400;                    /* val は 0〜86399 に bounded */
int hours = (int)(val / 3600);  /* 警告なし（int に収まると判断） */
int mins  = (int)(val / 60);    /* 警告なし */
```

宣言時の初期化でも同様に機能します：

```c
time_t seconds = t % 86400;        /* seconds が bounded と認識される */
int h = (int)(seconds / 3600);     /* 警告なし */
```

除数は整数リテラル・`#define` マクロに加え、`const time_t` 型のローカル変数（別の定数を
参照する算術式による初期化も含む）でも認識されます：

```c
const time_t secs_hour = 3600;
const time_t secs_day  = 3600 * 24;   /* 算術式も解決される */
time_t seconds = t % secs_day;        /* seconds が bounded と認識される */
int h = (int)(seconds / secs_hour);   /* 警告なし */
```

剰余演算そのものは、左辺の変数が bounded かどうかに関わらず、右辺の除数が上記の時間単位
定数であれば無条件に警告が抑制されます（曜日計算 `(days+4) % 7` 等）。

**既知の限界**: ループ（`for`/`while`）を跨いだ累積減算による bounding（配列要素や
関数呼び出しの戻り値を使った縮退）は認識されません。意図的に抑制したい場合は
`y2038: ignore` を使用してください。

---

## pre-commit フレームワークと連携する

[pre-commit](https://pre-commit.com/) を使っているプロジェクトなら、コミット時に自動で検査を実行できます。

### セットアップ

プロジェクトルートの `.pre-commit-config.yaml` に以下を追加してください。

```yaml
repos:
  - repo: https://github.com/mar-tusita/y2038detect
    rev: v0.9.4
    hooks:
      - id: y2038detect
```

初回セットアップ：

```bash
pip install pre-commit
pre-commit install
```

### 動作

`git commit` を実行すると、ステージされた `.c` ファイルだけが自動的に解析されます。2038年問題が検出された場合はコミットが中止され、警告が表示されます。

### オプションを追加する場合

`--compile-commands` や `-I` を渡したい場合は `args:` で指定します。

```yaml
repos:
  - repo: https://github.com/mar-tusita/y2038detect
    rev: v0.9.4
    hooks:
      - id: y2038detect
        args: [--compile-commands, build/compile_commands.json]
```

---

## フィードバックと貢献

不具合の報告、誤検出・見逃しの例、改善の提案は [GitHub の Issues](https://github.com/mar-tusita/y2038detect/issues) へお寄せください。誤検出や見逃しの報告には、再現できる最小の C コードを添えていただけると助かります。

Pull request も歓迎します。取り込むときは 1 件を 1 コミットにまとめます（squash merge）。送っていただいた変更は、本ツールと同じ [BSD 2-Clause License](LICENSE) で公開されます。

このリポジトリはリリースなどの節目ごとに更新しているため、コミット履歴はその単位になっています。

---

## 謝辞

- **[LLVM / libclang](https://llvm.org/)** — 本ツールのコアである AST 解析エンジン。
  libclang の Python バインディングにより、単純な文字列検索では届かない型情報・マクロ展開を扱った
  精度の高い検出が実現できています。
- **[y2k38-checker](https://github.com/cysec-lab/y2k38-checker)** — Clang Static Analyzer
  プラグインとして実装された同種のツール。検出カテゴリの設計において参考にしました。
- **[Claude Code](https://claude.ai/code)（Anthropic）** — 本ツールの開発全般にわたって利用しました。
  ツール作成にあたり、「どこまで機械がプログラムを書けるのか、人間が機械をどのように活用できるのか」を模索する実験的な試みとして、コード生成からドキュメント作成まで幅広く活用しています。
