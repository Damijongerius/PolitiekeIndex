"""
PDF Parser module using pdfplumber to extract text and structure from political program PDFs.
"""
import os
import re
from typing import List, Dict, Any
import pdfplumber

class PDFProcessor:
    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text page by page with metadata using pdfplumber.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        pages_data = []
        filename = os.path.basename(pdf_path)
        party_name = os.path.splitext(filename)[0].replace("_", " ").upper()

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    # Clean text
                    cleaned_text = self._clean_text(text)
                    if cleaned_text:
                        pages_data.append({
                            "party": party_name,
                            "filename": filename,
                            "page": page_num,
                            "text": cleaned_text
                        })

        return pages_data

    def _clean_text(self, text: str) -> str:
        """Clean extra spaces and linebreaks while retaining structure."""
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Splits extracted page text into overlapping chunks for indexing into ChromaDB.
        """
        chunks = []
        chunk_id = 0

        for item in pages_data:
            party = item["party"]
            page = item["page"]
            text = item["text"]
            filename = item["filename"]

            words = text.split(" ")
            if len(words) <= self.chunk_size:
                chunks.append({
                    "id": f"{party}_{page}_{chunk_id}",
                    "text": text,
                    "metadata": {
                        "party": party,
                        "page": page,
                        "filename": filename,
                        "chunk_id": chunk_id
                    }
                })
                chunk_id += 1
            else:
                start = 0
                while start < len(words):
                    end = start + self.chunk_size
                    chunk_text = " ".join(words[start:end])
                    chunks.append({
                        "id": f"{party}_{page}_{chunk_id}",
                        "text": chunk_text,
                        "metadata": {
                            "party": party,
                            "page": page,
                            "filename": filename,
                            "chunk_id": chunk_id
                        }
                    })
                    chunk_id += 1
                    start += (self.chunk_size - self.overlap)

        return chunks
