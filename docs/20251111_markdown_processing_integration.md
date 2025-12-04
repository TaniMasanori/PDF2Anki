ou Markdown Processing Integration into Streamlit App

## 日付
2025年11月11日

## 概要
新しく取り込まれたマークダウン処理スクリプト（`markdown_chunker.py`, `markdown_cleaner.py`, `process_markdown.py`, `semantic_detector.py`）をStreamlitアプリケーションに統合し、LLM（ChatGPT）API機能を使用してAnkiカードを生成できるようにしました。

## 実装内容

### 1. ラッパーモジュールの作成
`src/markdown_processor_wrapper.py`を作成し、以下の機能を提供しました：

- **型変換機能**: `domain_types`と`pdf2anki_types`の間の型変換を行う関数
- **統合処理関数**: マークダウンのクリーンアップとチャンキングを一括で実行する`process_markdown_for_streamlit()`
- **セマンティック情報取得**: チャンクからセマンティック構造情報を取得する`get_semantic_info_for_chunk()`
- **メタデータ読み込み**: PDF SHA256をメタデータファイルから読み込む`load_pdf_sha256_from_meta()`

### 2. Streamlitアプリの更新
`src/streamlit_app.py`を更新し、以下の機能を追加しました：

#### チャンクベースのカード生成
- `generate_cards_from_chunk()`: 個別のチャンクからAnkiカードを生成する関数
- `generate_anki_cards()`: チャンキング機能を統合したカード生成関数
  - チャンキングモードと非チャンキングモードの両方をサポート
  - チャンクごとにLLM APIを呼び出し、セマンティック情報を活用

#### UIの改善
- サイドバーに「Processing Options」セクションを追加
  - 「Use intelligent chunking」チェックボックス（デフォルト: 有効）
  - 「Max tokens per chunk」設定（デフォルト: 2000）
- PDF変換時にSHA256ハッシュを取得し、セッション状態に保存
- チャンク処理の進行状況をプログレスバーで表示

#### セマンティック情報の活用
- 各チャンクからキーワードと定義を抽出
- LLMプロンプトにセマンティック情報を追加して、より質の高いカード生成を実現

### 3. 変更されていないファイル
以下の新しく取り込まれたスクリプトは変更していません（ユーザーの要求通り）：
- `src/markdown_chunker.py`
- `src/markdown_cleaner.py`
- `src/process_markdown.py`
- `src/semantic_detector.py`

## 使用方法

1. **PDFをアップロード**: StreamlitアプリでPDFファイルをアップロード
2. **マークダウンに変換**: 「Convert to Markdown」ボタンをクリック
3. **設定を調整**: サイドバーで以下を設定
   - 生成するカード数
   - コンテンツフォーカス（mixed, definitions, concepts, facts）
   - Ankiノートタイプ（basic, cloze）
   - チャンキングの有効/無効
   - チャンクあたりの最大トークン数
4. **カード生成**: 「Generate Anki Cards」ボタンをクリック
   - チャンキングが有効な場合、マークダウンがクリーンアップされ、チャンクに分割されます
   - 各チャンクからセマンティック情報が抽出され、LLMプロンプトに追加されます
   - チャンクごとにLLM APIが呼び出され、Ankiカードが生成されます
5. **ダウンロード**: 生成されたTSVファイルをダウンロードしてAnkiにインポート

## 技術的な詳細

### 型システムの統合
- `domain_types`（新しく取り込まれたスクリプトが使用）と`pdf2anki_types`（既存のStreamlitアプリが使用）の間で型変換を行うラッパー関数を実装
- データの整合性を保ちながら、両方の型システムを共存させる

### チャンキング戦略
1. マークダウンをセクション見出しで分割
2. 各セクションが最大トークン数を超える場合、段落や文でさらに分割
3. 各チャンクに一意のIDとソース参照を割り当て

### セマンティック検出
- 定義パターンの検出（"X is Y", "X: Y"など）
- キーワードの抽出（太字、斜体、引用符内のテキスト）
- 概念境界の識別（見出し、リストなど）

## 今後の改善点

- チャンク処理の並列化による高速化
- セマンティック情報をより効果的に活用したプロンプト生成
- チャンク品質の評価とフィルタリング機能
- エラーハンドリングの強化

## コミット情報
- コミットハッシュ: 5592884
- コミットメッセージ: "Integrate markdown processing scripts into Streamlit app with chunking support"

