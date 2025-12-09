# GPU メモリ不足時の CPU 自動フォールバック機能

## 概要
`setup_and_run.sh` に GPU メモリ残量チェック機能を追加しました。
起動時に VRAM の空き容量が不足している場合、自動的に CPU モード (`CUDA_VISIBLE_DEVICES=''`) で `marker-api` サーバーを起動し、OOM (Out Of Memory) エラーによるクラッシュを防止します。

## 背景
- ユーザー環境にて、別の長時間実行プロセス（学習ジョブ等）が GPU メモリの大半を使用しているケースが確認されました。
- この状態で `marker-api` を起動すると `torch.OutOfMemoryError` が発生し、アプリケーションが使用できませんでした。

## 機能詳細

1.  **VRAM チェック**
    - `nvidia-smi` コマンドが利用可能な場合、最初の GPU の空きメモリ量を取得します。
    - 取得コマンド: `nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits`

2.  **判定基準**
    - 空きメモリが **4000 MiB (4GB)** 未満の場合、"Low GPU memory detected" と判定します。
    - ※ `marker-api` (Surya モデル) の動作には数GBのVRAMが必要なため、安全マージンとして4GBを設定しました。

3.  **CPU モードへの切り替え**
    - 低メモリ状態と判定された場合、サーバー起動コマンドの前に `export CUDA_VISIBLE_DEVICES=''` を付与します。
    - これにより、PyTorch は GPU を認識せず、CPU で推論を行います。

## ユーザーへの影響
- **GPU が空いている場合**: 通常通り GPU 加速を使用して高速に動作します。
- **GPU が埋まっている場合**: 自動的に CPU モードで起動します。処理速度は低下しますが、エラーで停止することなく機能を利用できます。
- **手動での制御**: CPU モードを強制したい場合は、スクリプト内の判定しきい値を変更するか、手動で `export CUDA_VISIBLE_DEVICES=''` を設定してから `python server.py` を実行してください。

