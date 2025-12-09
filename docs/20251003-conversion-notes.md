---
title: lec6.pdf 変換メモ
created: 2025-10-03
---

## 概要
- `lec6.pdf` を Markdown に変換しました。
- 一時対応として `pymupdf4llm` で `docs/20251003-lec6.md` を作成済み。
- ご要望に合わせ、`marker-pdf` による高精度変換を現在実行中です（CLI: `marker_single`）。

## 実施内容
1. 依存導入: `marker-pdf` を導入（CLI `marker_single` 利用可能）。
2. 変換実行: `marker_single --output_dir outputs/marker lec6.pdf` を起動。
3. 進行状況: レイアウト・OCRモデルのダウンロードと推論を実行中。完了後にMarkdownを `docs/20251003-lec6.md` に差し替え予定。

## 注意点
- `marker-pdf` 実行時は数GB規模のモデルをダウンロードします（`~/.cache/datalab/models`）。リポジトリには含めません。
- 画像抽出を有効にすると出力が大きくなる場合があります。必要に応じて画像を無効化して再実行可能です。

## 今後の対応（完了後）
- `outputs/marker` に生成された Markdown/画像を確認し、必要に応じて `docs/` に整理します。
- 大きな生成物は `.gitignore` または Git LFS の対象にします。


