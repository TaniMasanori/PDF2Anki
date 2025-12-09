タイトル: PDF2Anki フローチャート（Mermaid）

このドキュメントは、PDF2Anki のエンドツーエンド処理フローを示します。Web UI は Streamlit、PDF→Markdown 変換は Marker API、カード生成は OpenAI 互換の LLM（または OpenAI）を利用します。

```mermaid
flowchart TD
    %% User/UI
    U[ユーザ\n(ブラウザ/Streamlit UI)] -->|PDFアップロード| A[streamlit_app.py\nアップロード処理]
    A --> B[SHA256計算・セッション出力ディレクトリ作成\noutputs/<timestamp>_<pdf_name>/]
    A -->|Convert to Markdown クリック| C[marker_client.convert_pdf_to_markdown]
    
    %% Marker API
    subgraph Marker API サービス
        MAPI[/POST /convert/]
    end
    C -->|PDF送信| MAPI
    MAPI -->|markdown, meta 受信| D[marker.md, meta.json 保存\n(temp conv_dir)]
    D --> E[converted.md, meta.json を\nセッション出力へコピー]
    E --> F[Markdownプレビュー表示]
    
    %% カード生成トリガ
    F -->|Generate Anki Cards| G[LLM設定の決定\n(LLM_API_BASE or OPENAI)]
    G --> H{Use intelligent chunking?}
    
    %% Chunking パス
    subgraph チャンク処理パス
        direction TB
        I[markdown_processor_wrapper\n.clean_markdown] --> J[.chunk_markdown\n(max_tokens)]
        J --> K[各チャンクごとに\nsemantic_detector で\n定義/用語/概念境界抽出]
        K --> L[anki_core.build_prompt\n(チャンク＋セマンティクス)]
        L --> LL[LLM 呼び出し\nopenai.chat.completions.create]
        LL --> LM[anki_core.parse_cards_from_output\n→ Cards]
    end
    
    %% Non-chunking パス
    subgraph 非チャンク処理パス
        direction TB
        N[anki_core.build_prompt\n(全文ベース)] --> NL[LLM 呼び出し]
        NL --> NM[parse_cards_from_output\n→ Cards]
    end
    
    H -- はい --> I
    H -- いいえ --> N
    
    %% 結果統合
    I & J & K & L & LL & LM --> O[全チャンクの Cards を集約]
    N & NL & NM --> O
    O --> P[TSV 生成 (Card.to_tsv_row)\noutputs/<session>/anki_cards.tsv]
    P --> Q[ダウンロードボタン\n( Markdown / TSV )]
    Q --> R[Anki へインポート]
```

補足:
- Marker API 側の最終保存は一時ディレクトリ（ハッシュごとの `conversions/<sha>/`）ですが、UI で扱う最終成果物は `outputs/<timestamp>_<pdf_name>/` にコピーされます。
- チャンク処理が有効な場合、各チャンクでセマンティック情報（定義・用語・概念境界）を取り入れてプロンプトを強化し、カード品質の向上を図ります。
- LLM は OpenAI 互換エンドポイント（LLM_API_BASE）か、OpenAI API（OPENAI_API_KEY/OPENAI_MODEL）を自動選択します。


