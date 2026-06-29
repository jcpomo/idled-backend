import io
import pytest
from openpyxl import Workbook
from pypdf import PdfWriter
from app.documentos.extract import extract_text

def _pdf_bytes(text_lines):
    # pypdf can't easily write text; use a minimal real PDF via reportlab-free approach:
    # build a PDF with a blank page is not enough for text. Instead test the Excel + text paths
    # for content, and the PDF path for "does not crash + returns str".
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def _xlsx_bytes(rows):
    wb = Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

def test_extract_excel():
    data = _xlsx_bytes([["Cliente", "Total"], ["ACME", 100], ["Globex", 200]])
    out = extract_text(data, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    assert "ACME" in out and "Globex" in out and "Total" in out

def test_extract_plain_text():
    out = extract_text("hola mundo".encode(), "text/plain")
    assert out == "hola mundo"

def test_extract_pdf_returns_str():
    out = extract_text(_pdf_bytes([]), "application/pdf")
    assert isinstance(out, str)

def test_unsupported_type_raises():
    with pytest.raises(ValueError):
        extract_text(b"\x00", "image/png")
