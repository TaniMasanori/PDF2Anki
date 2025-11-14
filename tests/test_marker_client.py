import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from marker_client import convert_pdf_to_markdown


class FakeResponse:
    def __init__(self, status_code=200, text="OK"):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_convert_pdf_to_markdown_success(monkeypatch, tmp_path):
    # Create dummy pdf file
    pdf_file = tmp_path / "dummy.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%...dummy...")

    def fake_post(url, files, headers, timeout):
        return FakeResponse(200, text="# Title\n\nHello from Marker")

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    out_root = tmp_path / "out"
    result = convert_pdf_to_markdown(pdf_path=pdf_file, api_base_url="http://localhost:8000", output_root=out_root)

    assert Path(result.markdown_path).exists()
    assert Path(result.meta_path).exists()
    assert "Hello from Marker" in Path(result.markdown_path).read_text(encoding="utf-8")








