# セットアップスクリプトの修正: sh 実行時の互換性対応

## 概要
ユーザーが `sh setup_and_run.sh` (または `run_streamlit.sh`) のように `sh` コマンドを使用してスクリプトを実行した場合に、Bash 固有の構文（`&>` や `[[`）が解釈されずエラーが発生する問題を修正しました。

## 発生していた問題
- `sh` (Ubuntu 等では `dash`) は `&>` (標準出力・標準エラー出力の同時リダイレクト) をサポートしていないため、Python バージョンチェックなどで構文エラーや意図しない挙動が発生していた。
- スクリプトのシェバンは `#!/bin/bash` となっているが、`sh script.sh` として実行されるとシェバンが無視され、非互換のシェルで実行されてしまう。

## 修正内容

### 1. Bash での再実行ロジックの追加
`setup_and_run.sh` および `run_streamlit.sh` の冒頭に、現在のシェルが Bash でない場合に自動的に Bash で再実行するロジックを追加しました。

```bash
# Ensure running in bash
if [ -z "$BASH_VERSION" ]; then
    exec bash "$0" "$@"
fi
```

これにより、ユーザーが `sh setup_and_run.sh` と入力しても、内部的に Bash プロセスに切り替わり、スクリプトが正しく実行されます。

### 2. リダイレクト構文の修正
互換性向上のため、Bash 固有の `&> /dev/null` を POSIX 準拠の `> /dev/null 2>&1` に変更しました。

- 修正前: `command -v python3 &> /dev/null`
- 修正後: `command -v python3 > /dev/null 2>&1`

対象箇所:
- Python チェック
- `gnome-terminal` / `xterm` チェック

## 対象ファイル
- `setup_and_run.sh`
- `run_streamlit.sh`

## 確認事項
- `sh setup_and_run.sh` で実行してもエラーなく動作すること。

