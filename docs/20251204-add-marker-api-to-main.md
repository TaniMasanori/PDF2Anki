# Git 作業記録: marker-api を main に取り込み（サブモジュール化）

## 目的
- 既存の `marker-api` ディレクトリを削除せず、そのまま main ブランチに取り込む。
- 将来の更新も追従しやすいよう、外部リポジトリをサブモジュールとして管理する。

## 実施方針
- 既存の `marker-api` は独立した Git リポジトリ（`.git/` を保持）だったため、サブモジュールとして登録。
- `.gitignore` の `marker-api/` 除外を外し、`.gitmodules` を作成して `marker-api` をサブモジュール化。

## 実施コマンド概要
```bash
# main を最新化
git checkout main
git pull --ff-only origin main

# .gitignore の除外を外す（marker-api/ 行を削除）
git add .gitignore
git commit -m "chore(git): allow tracking marker-api by removing ignore rule"

# サブモジュール登録（既存ディレクトリを活かす）
git config -f .gitmodules submodule.marker-api.path marker-api
git config -f .gitmodules submodule.marker-api.url https://github.com/adithya-s-k/marker-api.git

# サブモジュールの gitlink を作成（marker-api の HEAD を使う）
sha=$(git -C marker-api rev-parse HEAD)
git update-index --add --cacheinfo 160000,$sha,marker-api
git add .gitmodules
git commit -m "chore(submodule): add marker-api as git submodule"
git push origin main
```

## 備考
- これにより、リポジトリのルートに `.gitmodules` が追加され、`marker-api` はサブモジュール（gitlink, mode 160000）として管理されます。
- 今後、`marker-api` 側の最新版を取り込む場合は以下を実行してください。
  ```bash
  git submodule update --init --recursive
  (cd marker-api && git fetch && git checkout <必要なタグやブランチ> && git pull)
  git add marker-api
  git commit -m "chore(submodule): bump marker-api to <new-sha>"
  git push origin main
  ```
- 既存の `marker-api/.git` は、必要に応じて `git submodule absorbgitdirs marker-api` を実行することで、親リポジトリの `.git/modules/marker-api` に吸収できます（現状でも動作上は問題ありません）。

## コミット
- chore(git): allow tracking marker-api by removing ignore rule
- chore(submodule): add marker-api as git submodule


