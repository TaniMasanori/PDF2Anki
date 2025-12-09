タイトル: PDF2Anki 最終発表アウトライン（デモ台本付き）
日付: 2025-11-13
リポジトリ: https://github.com/TaniMasanori/PDF2Anki

目的
- 完成システムのエンドツーエンドをわかりやすく実演。
- 設計判断、デバッグ課題、vibe coding で得た知見を簡潔に共有。

想定時間配分（合計 ~10–12 分）
1) 導入（1 分）
   - 問題設定：PDF から学習カード作成は時間がかかる。
   - 解決策：PDF2Anki は PDF→Markdown→Anki カードを一気通貫で自動生成。
2) システム概要（2 分）
   - UI: Streamlit、変換: Marker API、生成: OpenAI/互換 LLM。
   - 主要機能：数式対応、チャンク分割＋セマンティクス、TSV エクスポート、タグ付け。
3) ライブデモ（5–6 分）
   - A. Marker API 起動確認（別ターミナル）
     - コマンド例: cd marker-api && source .venv/bin/activate && python server.py --host 0.0.0.0 --port 8000
     - ブラウザで http://localhost:8000/health を確認。
   - B. Streamlit 起動
     - コマンド例: source venv/bin/activate && streamlit run src/streamlit_app.py
     - ブラウザで http://localhost:8501 を表示。
   - C. 操作手順
     1. PDF をアップロード（講義スライドや短めの論文）。
     2. 「Convert to Markdown」を実行、成功メッセージとプレビューを確認。
     3. サイドバー設定
        - Number of cards: 12（例）
        - Content focus: definitions（例）
        - Note type: basic もしくは cloze
        - Use intelligent chunking: 有効（推奨）
     4. 「Generate Anki Cards」を実行、進捗表示。
     5. 生成されたカードの一部を展開して、
        - 数式維持（MathJax）
        - タグ付け
        - ソース由来の粒度（チャンク分割）
        を確認。
     6. TSV をダウンロード→Anki の Import 画面でマッピングを口頭説明。
4) 設計トレードオフ（1–2 分）
   - OpenAI vs ローカル LLM（コスト/速度/プライバシー）。
   - チャンク分割＋セマンティクス（品質/遅延/複雑度）。
   - セッションディレクトリ出力（再現性/リポジトリ肥大防止）。
5) デバッグ課題と対策（1 分）
   - max_tokens vs max_completion_tokens の違いによる API エラー。
   - 429（クォータ/レート制限）時の案内とローカル LLM フォールバック。
   - 起動順序（Marker→Streamlit）の徹底とヘルスチェック導線。
6) 学び（1 分）
   - vibe coding の有効性と限界（仕様の思い込み/幻覚対策）。
   - 小さな差分での改良・検証サイクルが安定度を上げる。
7) まとめ（30 秒）
   - ゴール達成、デモ成功、今後の改善点（画像活用、品質評価 UI など）。

参考資料（スライド候補）
- システム全体図（README の Mermaid 図要約）。
- UI スクリーンショット（アップロード、プレビュー、生成結果、ダウンロード）。
- 失敗例と復旧例（404/429/モデル不一致）。

ハンドオフ要点（発表者向けメモ）
- 事前に PDF を1～2本ピックアップし、同じマシンで Marker と Streamlit の起動確認を済ませる。
- 生成カードの中から品質の良いものを2～3枚ピックアップして紹介。
- Anki への取り込みは設定画面のスクショで代替可能（時間短縮）。
