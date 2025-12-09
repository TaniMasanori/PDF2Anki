---
title: marker-pdf Setup Guide
date: 2025-10-02
updated: 2025-10-04
---

This document provides setup instructions for marker-pdf Python library on Windows/WSL/Linux. Code comments are written in English.

## 1. Prerequisites
- Python 3.10+ (Python 3.13 recommended for latest features)
- pip package manager
- Sufficient disk space (~5GB for models cache)
- CUDA-capable GPU (optional, but recommended for faster processing)

## 2. Installation Methods

### Method A: Direct pip Installation (Recommended)
```bash
# Create and activate virtual environment
python3 -m venv ~/.venvs/pdf2anki
source ~/.venvs/pdf2anki/bin/activate  # On Windows: .venvs\pdf2anki\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install marker-pdf
pip install marker-pdf

# Verify installation
python -c "from marker.converters.pdf import PdfConverter; print('marker-pdf installed successfully')"
```

### Method B: WSL (Windows Subsystem for Linux)
If you prefer WSL environment:
```bash
# Inside WSL Ubuntu terminal
sudo apt update && sudo apt install -y python3 python3-venv python3-pip

# Create virtual environment
python3 -m venv ~/.venvs/pdf2anki
source ~/.venvs/pdf2anki/bin/activate

# Install marker-pdf
pip install marker-pdf
```

## 3. Basic Usage

### Python API Usage
```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

# Create converter instance (models will be downloaded on first use)
converter = PdfConverter(artifact_dict=create_model_dict())

# Convert PDF to Markdown
rendered = converter("path/to/input.pdf")

# Access results
markdown_text = rendered.markdown
images_dict = rendered.images  # dict[str, PIL.Image.Image]

# Save markdown
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_text)

# Save images
for img_name, img_pil in images_dict.items():
    img_pil.save(f"output_images/{img_name}")
```

### CLI Usage
marker-pdf provides a command-line tool `marker_single`:
```bash
# Basic conversion
marker_single input.pdf --output_dir outputs/

# With options
marker_single input.pdf \
  --output_dir outputs/ \
  --MarkdownRenderer_extract_images true \
  --max_pages 10
```

## 4. Model Cache Location
On first run, marker-pdf downloads deep learning models (~2-4GB):
- Linux/WSL: `~/.cache/datalab/models/`
- Windows: `C:\Users\<username>\.cache\datalab\models\`

These models are reused for subsequent conversions. Ensure adequate disk space.

## 5. Performance Optimization

### GPU Acceleration
If you have CUDA-capable GPU:
```bash
# Install PyTorch with CUDA support first
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Then install marker-pdf
pip install marker-pdf
```

### CPU-only Mode
marker-pdf works on CPU but will be slower. No special configuration needed.

## 6. Common Issues & Solutions

### Issue: CUDA out of memory
```bash
# Solution: Use CPU or process fewer pages at once
export CUDA_VISIBLE_DEVICES=""  # Force CPU mode
```

### Issue: ModuleNotFoundError
```bash
# Solution: Ensure virtual environment is activated
source ~/.venvs/pdf2anki/bin/activate  # Linux/WSL
# or
.\.venvs\pdf2anki\Scripts\activate  # Windows
```

### Issue: Slow conversion
- Use GPU if available
- Process smaller page ranges for testing
- Ensure models are cached (first run is slower)

### Issue: PDF parsing fails
- Ensure PDF is not encrypted
- For scanned PDFs, marker-pdf uses OCR automatically
- Check PDF file is not corrupted

## 7. Integration with PDF2Anki Project

Our project uses marker-pdf through `src/convert_pdf_marker.py`:
```bash
# Example usage
python src/convert_pdf_marker.py --input lec1.pdf --outdir outputs
```

Output structure:
```
outputs/
  conversions/<pdf_sha256>/
    marker.md             # Converted Markdown
    meta.json             # Metadata (pages, elapsed time, etc.)
    conversion_result.json# Result paths
    _page_0_Picture_0.jpeg# Extracted images (same directory as markdown)
    _page_1_Figure_1.jpeg
    ...
```

## 8. Differences from Marker API (adithya-s-k/marker-api)

| Aspect | marker-api (Old) | marker-pdf (Current) |
|--------|------------------|----------------------|
| Type | REST API Server | Python Library |
| Installation | Clone repo + dependencies | Simple: `pip install marker-pdf` |
| Usage | HTTP POST requests | Direct Python function calls |
| Server | Requires running server | No server needed |
| Images | Returns via HTTP response | Returns as PIL Image objects |
| Complexity | Higher (server management) | Lower (library import) |

## 9. Next Steps
- Test conversion with sample PDFs
- Implement cleaning and chunking logic
- Integrate with LLM for card generation

## References
- marker-pdf GitHub: https://github.com/VikParuchuri/marker
- Documentation: https://pypi.org/project/marker-pdf/
- PyTorch: https://pytorch.org/get-started/locally/





