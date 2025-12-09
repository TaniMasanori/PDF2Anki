# PDF変換高速化ガイド / PDF Conversion Speed Optimization Guide

## 概要 / Overview

このドキュメントでは、PDF2AnkiプロジェクトにおけるPDF変換処理を高速化するための最適化方法を説明します。

This document explains optimization methods to speed up PDF conversion processing in the PDF2Anki project.

## 最適化オプション / Optimization Options

### 1. GPUの使用 / GPU Usage

Marker APIはGPUを使用することで大幅に高速化できます。GPUが利用可能な場合、必ず使用することを推奨します。

Marker API can be significantly accelerated by using GPU. If GPU is available, it is highly recommended to use it.

#### GPUの確認 / Check GPU Availability

```bash
# NVIDIA GPUの場合
nvidia-smi

# PyTorchでGPUが利用可能か確認
python -c "import torch; print(torch.cuda.is_available())"
```

#### GPU設定 / GPU Configuration

Marker APIサーバー起動前に環境変数を設定：

Set environment variables before starting Marker API server:

```bash
# GPUを使用する場合
export TORCH_DEVICE=cuda

# GPU VRAMを設定（例: 16GBの場合）
export INFERENCE_RAM=16

# タスクあたりのVRAM使用量を調整（必要に応じて）
export VRAM_PER_TASK=3
```

### 2. OCRエンジンの最適化 / OCR Engine Optimization

デフォルトでは`surya`が使用されますが、CPUでは遅いです。OCRが不要な場合や、速度を優先する場合は設定を変更できます。

By default, `surya` is used, but it's slow on CPU. You can change the setting if OCR is not needed or if speed is prioritized.

#### OCRエンジンの選択 / OCR Engine Selection

```bash
# OCRを無効化（テキストベースのPDFの場合、最も高速）
export OCR_ENGINE=None

# ocrmypdfを使用（suryaより高速だが、精度はやや低い）
export OCR_ENGINE=ocrmypdf

# デフォルト（surya、最も高精度だがCPUでは遅い）
# 環境変数を設定しない
```

**注意**: `ocrmypdf`を使用する場合は、追加の依存関係が必要です。

**Note**: Using `ocrmypdf` requires additional dependencies.

### 3. バッチ処理の最適化 / Batch Processing Optimization

複数のPDFを同時に処理する場合、並列処理数を調整できます。

When processing multiple PDFs simultaneously, you can adjust the parallelism.

#### サーバー側の並列処理設定 / Server-side Parallelism

現在の実装では`max_workers=2`が設定されています。CPUコア数に応じて調整可能です。

Current implementation uses `max_workers=2`. This can be adjusted based on CPU cores.

**推奨設定 / Recommended Settings**:
- CPUのみ: CPUコア数の50-75%
- GPU使用: GPU VRAMに応じて調整（`INFERENCE_RAM / VRAM_PER_TASK`）

### 4. Marker APIサーバーの起動最適化 / Marker API Server Startup Optimization

最適化された環境変数でサーバーを起動するスクリプトを作成することを推奨します。

It is recommended to create a script to start the server with optimized environment variables.

#### 最適化された起動スクリプトの例 / Example Optimized Startup Script

```bash
#!/bin/bash
# marker-api/run_optimized.sh

# GPU設定（GPUが利用可能な場合）
if command -v nvidia-smi &> /dev/null; then
    export TORCH_DEVICE=cuda
    export INFERENCE_RAM=16  # お使いのGPU VRAMに合わせて調整
    export VRAM_PER_TASK=3
    echo "GPU mode enabled"
else
    echo "CPU mode (GPU not detected)"
fi

# OCR設定（テキストベースのPDFの場合）
# export OCR_ENGINE=None

# サーバー起動
cd marker-api
source .venv/bin/activate
python server.py --host 0.0.0.0 --port 8888
```

### 5. システムリソースの最適化 / System Resource Optimization

#### CPU使用率の最適化 / CPU Usage Optimization

- 他の重いプロセスを停止
- CPUのパフォーマンスモードを有効化（Linuxの場合）

```bash
# CPU周波数スケーリングを確認
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# パフォーマンスモードに設定（root権限が必要）
sudo cpupower frequency-set -g performance
```

#### メモリの最適化 / Memory Optimization

- 十分なRAMを確保（推奨: 8GB以上）
- スワップファイルの使用を最小化

### 6. PDFファイルの前処理 / PDF File Preprocessing

変換前にPDFを最適化することで、処理速度が向上する場合があります。

Preprocessing PDFs before conversion may improve processing speed.

- 不要なページを削除
- 画像の解像度を下げる（OCRが必要な場合を除く）
- PDFを最適化ツールで圧縮

## 実装手順 / Implementation Steps

### ステップ1: 環境変数の設定 / Step 1: Set Environment Variables

Marker APIディレクトリで`.env`ファイルを作成または編集：

Create or edit `.env` file in marker-api directory:

```bash
cd marker-api
cat >> .env << EOF
# GPU設定（GPUが利用可能な場合）
TORCH_DEVICE=cuda
INFERENCE_RAM=16
VRAM_PER_TASK=3

# OCR設定（必要に応じて変更）
# OCR_ENGINE=None
# OCR_ENGINE=ocrmypdf
EOF
```

### ステップ2: 最適化された起動スクリプトの作成 / Step 2: Create Optimized Startup Script

`marker-api/run_optimized.sh`を作成（上記の例を参照）

Create `marker-api/run_optimized.sh` (see example above)

### ステップ3: サーバーの再起動 / Step 3: Restart Server

最適化された設定でサーバーを再起動：

Restart server with optimized settings:

```bash
# 既存のサーバーを停止
# Ctrl+C で停止

# 最適化されたスクリプトで起動
cd marker-api
./run_optimized.sh
```

## パフォーマンス比較 / Performance Comparison

### 典型的な改善例 / Typical Improvements

| 設定 / Setting | CPUのみ / CPU Only | GPU使用 / GPU Enabled |
|----------------|-------------------|---------------------|
| 10ページのPDF / 10-page PDF | 60-120秒 / 60-120s | 10-20秒 / 10-20s |
| 50ページのPDF / 50-page PDF | 5-10分 / 5-10min | 1-2分 / 1-2min |
| OCRなし / No OCR | 30-50%高速化 / 30-50% faster | 10-20%高速化 / 10-20% faster |

**注意**: 実際のパフォーマンスは、PDFの内容、システム構成、GPU性能によって異なります。

**Note**: Actual performance varies depending on PDF content, system configuration, and GPU performance.

## トラブルシューティング / Troubleshooting

### GPUが認識されない場合 / GPU Not Detected

1. NVIDIAドライバーがインストールされているか確認
2. PyTorchのCUDA対応版がインストールされているか確認

```bash
python -c "import torch; print(torch.version.cuda)"
```

### メモリ不足エラー / Out of Memory Error

- `INFERENCE_RAM`を減らす
- `VRAM_PER_TASK`を増やす（並列処理数を減らす）
- バッチサイズを減らす

### 速度が改善しない場合 / No Speed Improvement

1. GPUが実際に使用されているか確認（`nvidia-smi`で確認）
2. OCRエンジンの設定を確認
3. システムリソースの使用状況を確認

## 参考資料 / References

- [Marker PDF Documentation](https://github.com/VikParuchuri/marker)
- [Marker API README](../marker-api/README.md)
- [PyTorch GPU Setup](https://pytorch.org/get-started/locally/)

## 更新履歴 / Changelog

- 2025-11-13: 初版作成 / Initial version created

