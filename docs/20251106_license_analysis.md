# ライセンス分析レポート

作成日: 2025-11-06

## 概要

本プロジェクト（PDF2Anki）のライセンス適合性について分析しました。特に、Streamlitとmarker-apiを使用する場合のMITライセンスの適切性を検討しています。

## 現在のライセンス状況

### プロジェクト本体
- **ライセンス**: MIT License
- **著作権者**: Masanori Tani (2025)

### 依存関係のライセンス

#### 1. Streamlit
- **ライセンス**: Apache License 2.0
- **互換性**: ✅ MITと互換性あり
- **説明**: Apache 2.0はMITと同様に寛容なライセンスで、商用利用も可能です。

#### 2. marker-apiディレクトリ
- **ライセンス**: GNU General Public License v3 (GPL v3)
- **場所**: `/home/masan/PDF2Anki/marker-api/`
- **互換性**: ⚠️ **問題あり**
- **説明**: GPL v3はコピーレフトライセンスで、このコードを含むプロジェクト全体もGPL v3で公開する必要があります。

#### 3. marker-pdfパッケージ
- **ライセンス**: GPL-3.0-or-later
- **使用箇所**: `src/convert_pdf_marker.py`で直接インポート
- **互換性**: ⚠️ **問題あり**
- **説明**: GPL-3.0-or-laterはGPL v3と同様のコピーレフトライセンスです。このパッケージを直接インポートするコードはGPLの影響を受けます。

## 使用状況の分析

### marker-apiの使用方法

1. **HTTP API経由での使用**（推奨）
   - `src/marker_client.py`がHTTPリクエストでmarker-apiサーバーにアクセス
   - この方法では、marker-apiが別プロセスとして実行されるため、GPLの影響を受けにくい

2. **直接インポート**（問題あり）
   - `marker-api/`ディレクトリがリポジトリに含まれている
   - リポジトリにGPL v3のコードが含まれる場合、プロジェクト全体がGPL v3の影響を受ける可能性がある

### marker-pdfの使用

- `src/convert_pdf_marker.py`が`marker`モジュールを直接インポート
- このファイルはCLIスクリプトで、Streamlitアプリからは使用されていない
- **marker-pdfはGPL-3.0-or-laterライセンス**のため、このファイルはGPLの影響を受ける
- ただし、Streamlitアプリ（`src/streamlit_app.py`）は`marker_client.py`を使用しており、HTTP API経由なので直接的な依存関係はない

## 問題点とリスク

### 1. GPL v3のコピーレフト条項

marker-apiディレクトリがリポジトリに含まれている場合：
- プロジェクト全体をGPL v3で公開する必要がある可能性
- MITライセンスとの互換性がない
- 商用利用やプロプライエタリな配布が制限される可能性

### 2. ライセンスの混在

- プロジェクト本体: MIT
- marker-api: GPL v3
- この混在は法的な複雑さを生む可能性がある

## 推奨される解決策

### オプション1: marker-apiを別リポジトリに分離（推奨）

**メリット**:
- プロジェクト本体をMITライセンスのまま維持可能
- marker-apiは独立したGPL v3プロジェクトとして管理
- HTTP API経由での使用により、GPLの影響を回避

**実装方法**:
1. marker-apiディレクトリを別リポジトリに移動
2. このリポジトリからmarker-apiを削除
3. READMEにmarker-apiのセットアップ手順を記載（別リポジトリへのリンク）

### オプション2: プロジェクト全体をGPL v3に変更

**メリット**:
- ライセンスの一貫性が保たれる
- オープンソースコミュニティとの整合性

**デメリット**:
- 商用利用が制限される
- プロプライエタリな配布ができない

### オプション3: marker-apiを.gitignoreに追加

**メリット**:
- リポジトリからGPL v3コードを除外
- プロジェクト本体をMITのまま維持

**デメリット**:
- ユーザーが手動でmarker-apiをセットアップする必要がある
- セットアップが複雑になる

## 結論

**現在のMITライセンスは、marker-apiディレクトリがリポジトリに含まれている限り、適切ではありません。**

### 推奨アクション

1. **即座の対応**: marker-apiディレクトリを別リポジトリに分離するか、.gitignoreに追加
2. **長期的対応**: marker-apiをGitサブモジュールとして管理するか、完全に別リポジトリに分離
3. **ドキュメント更新**: READMEにmarker-apiのセットアップ手順を明確に記載

### 現在の使用状況での評価

- **Streamlit**: ✅ MITと互換
- **marker-api（HTTP API経由）**: ✅ 使用可能（別プロセスとして実行）
- **marker-api（リポジトリに含まれる）**: ❌ GPL v3の影響を受ける可能性
- **marker-pdf（直接インポート）**: ❌ GPL-3.0-or-laterの影響を受ける（`src/convert_pdf_marker.py`）
- **Streamlitアプリ本体**: ✅ HTTP API経由のため、直接的なGPL依存なし

## 次のステップ

1. ✅ marker-pdfのライセンスを確認済み（GPL-3.0-or-later）
2. marker-apiディレクトリの扱いを決定（分離 or .gitignore）
3. `src/convert_pdf_marker.py`の扱いを決定（削除 or GPLとして分離）
4. 必要に応じてLICENSEファイルを更新
5. READMEにライセンス情報を追加

## 追加の推奨事項

### `src/convert_pdf_marker.py`について

このファイルはmarker-pdfを直接インポートしているため、GPL-3.0-or-laterの影響を受けます。

**選択肢**:
1. **削除**: Streamlitアプリで使用されていないため、削除可能
2. **分離**: 別のGPLライセンスのプロジェクトとして分離
3. **保持**: このファイルのみGPLとして扱い、プロジェクト本体はMITのまま（ただし、リポジトリに含まれる限り問題が残る可能性）

