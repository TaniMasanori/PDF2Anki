# 2025-12-04 marker-api サブモジュール対応に伴う README 更新

本リポジトリに含まれる `marker-api` を **Git サブモジュール**として管理するように変更しました。これに伴い、README のクローン手順・セットアップ手順を更新しました。アプリケーションコードの変更はありません（ドキュメントのみ）。

## 変更点（概要）
- `marker-api` をサブモジュール化（参照先は `.gitmodules` に記載）
- 初回クローン時の推奨手順を `--recurse-submodules` に変更
- 既存クローン向けのサブモジュール初期化手順を追記
- プロジェクト構成のコメントを「git submodule」である旨に更新

## 利用手順（抜粋）

### 初回クローン（推奨）
```bash
git clone --recurse-submodules <repository-url>
cd PDF2Anki
```

### すでにクローン済みの場合（サブモジュール初期化）
```bash
git submodule update --init --recursive
```

### サブモジュールを新しいコミット／タグへ更新する
```bash
cd marker-api
git fetch origin
git checkout <tag-or-commit>
cd ..
git add marker-api
git commit -m "chore: bump marker-api submodule"
```

## 影響範囲
- アプリケーションの挙動には変更なし
- ドキュメント（README）のみ更新
- サブモジュール参照先： [adithya-s-k/marker-api](https://github.com/adithya-s-k/marker-api)（固定は `.gitmodules` にて管理）

## 補足
- 最小変更方針により、既存の Marker API 起動コマンドやポート番号の説明は本変更では触れていません。利用環境に応じて `MARKER_API_BASE` の値（例：`http://localhost:8000` や `http://localhost:8888`）を合わせてください。


