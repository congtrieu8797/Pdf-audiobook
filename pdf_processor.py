import io
import re
from typing import Tuple, Optional
import unicodedata
from vietnamese_font_fixer import fix_vietnamese_font

# Thử import PyMuPDF - thư viện số 1 xử lý font tiếng Việt trong PDF
try:
    import pymupdf as fitz
    HAS_PYMUPDF = True
except ImportError:
    try:
        import fitz
        HAS_PYMUPDF = True
    except ImportError:
        HAS_PYMUPDF = False

from pypdf import PdfReader

def extract_text_from_pdf(
    pdf_source: io.BytesIO | str | bytes, 
    start_page: int = 1, 
    end_page: Optional[int] = None
) -> Tuple[str, dict]:
    """
    Trích xuất nội dung văn bản từ file PDF với thuật toán xử lý font tiếng Việt tối ưu.
    Sử dụng PyMuPDF (fitz) làm bộ phân tích chính, tự động khôi phục bảng mã Unicode tiếng Việt.
    """
    if isinstance(pdf_source, (bytes, bytearray)):
        pdf_bytes = pdf_source
    elif isinstance(pdf_source, io.BytesIO):
        pdf_bytes = pdf_source.getvalue()
    elif isinstance(pdf_source, str):
        with open(pdf_source, "rb") as f:
            pdf_bytes = f.read()
    else:
        pdf_bytes = pdf_source.read()

    extracted_pages = []
    total_pages = 0

    if HAS_PYMUPDF:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            start_idx = max(0, start_page - 1)
            end_idx = total_pages if end_page is None else min(total_pages, end_page)

            for i in range(start_idx, end_idx):
                page = doc[i]
                # flags=fitz.TEXT_DEHYPHENATE tự động nối các từ bị ngắt dòng do dấu gạch ngang
                page_text = page.get_text("text", flags=fitz.TEXT_DEHYPHENATE) or ""
                
                # Áp dụng bộ lọc sửa font tiếng Việt
                page_text = fix_vietnamese_font(page_text)
                page_text = clean_text(page_text)
                
                if page_text:
                    extracted_pages.append(page_text)
            doc.close()
        except Exception:
            # Nếu PyMuPDF gặp sự cố với file đặc biệt, fallback sang pypdf
            extracted_pages = []

    # Fallback sang pypdf nếu PyMuPDF chưa cài đặt hoặc không lấy được text
    if not extracted_pages:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        start_idx = max(0, start_page - 1)
        end_idx = total_pages if end_page is None else min(total_pages, end_page)

        for i in range(start_idx, end_idx):
            page = reader.pages[i]
            page_text = page.extract_text() or ""
            page_text = fix_vietnamese_font(page_text)
            page_text = clean_text(page_text)
            if page_text:
                extracted_pages.append(page_text)

    full_text = "\n\n".join(extracted_pages)
    # Chuẩn hóa Unicode lần cuối
    full_text = unicodedata.normalize('NFC', full_text)
    
    words = full_text.split()
    word_count = len(words)
    estimated_minutes = round(word_count / 150, 1)

    metadata = {
        "total_pdf_pages": total_pages,
        "processed_pages": len(extracted_pages),
        "start_page": start_page,
        "end_page": end_idx if 'end_idx' in locals() else total_pages,
        "word_count": word_count,
        "estimated_reading_minutes": estimated_minutes,
        "engine": "PyMuPDF (Chống lỗi font)" if HAS_PYMUPDF else "pypdf"
    }

    return full_text, metadata

def clean_text(text: str) -> str:
    """Làm sạch văn bản, chuẩn hóa khoảng trắng và dòng"""
    if not text:
        return ""
    # Chuẩn hóa ngắt dòng: nối các dòng bị đứt quãng giữa câu
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'[ \t]+', ' ', text)
    # Loại bỏ nhiều dòng trống liên tiếp
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()
