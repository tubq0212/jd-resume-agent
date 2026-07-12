from __future__ import annotations

from io import BytesIO

from docx import Document


def read_txt_file(file_bytes: bytes) -> str:
    """Read a TXT resume file with common encodings."""
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return file_bytes.decode("utf-8", errors="ignore")


def read_docx_file(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    return "\n".join(paragraph for paragraph in paragraphs if paragraph)


def read_pdf_file(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("请先安装 pypdf：pip install -r requirements.txt") from exc

    reader = PdfReader(BytesIO(file_bytes))
    page_texts = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            page_texts.append(text.strip())

    extracted_text = "\n".join(page_texts)

    if not extracted_text.strip():
        raise RuntimeError("PDF 未提取到文字，可能是扫描版或图片型 PDF。请先使用 DOCX/TXT，后续再接入 OCR。")

    return extracted_text
