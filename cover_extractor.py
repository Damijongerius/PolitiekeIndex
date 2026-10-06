"""
Cover Extractor: Renders page 1 of PDFs as PNG images for the Party Overview UI.
"""
import os
import pypdfium2 as pdfium

def render_pdf_cover(pdf_path: str, output_img_path: str) -> bool:
    """Renders page 1 of a PDF to a PNG image file using pypdfium2."""
    if not os.path.exists(pdf_path):
        return False

    if os.path.exists(output_img_path):
        return True

    try:
        pdf = pdfium.PdfDocument(pdf_path)
        if len(pdf) == 0:
            return False
        page = pdf[0]
        image = page.render(scale=2).to_pil()
        os.makedirs(os.path.dirname(output_img_path), exist_ok=True)
        image.save(output_img_path, format="PNG")
        return True
    except Exception as e:
        print(f"Error rendering cover for {pdf_path}: {e}")
        return False
