"""
CLI script to ingest PDFs from a folder or single file into ChromaDB using pdfplumber.
"""
import os
import argparse
from pdf_parser import PDFProcessor
from database import VectorStore

def ingest_directory(input_dir: str, db_dir: str = "data/chroma_db"):
    processor = PDFProcessor()
    store = VectorStore(db_dir=db_dir)

    pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"Geen PDF bestanden gevonden in '{input_dir}'")
        return

    print(f"🔍 {len(pdf_files)} PDF bestanden verwerken...")
    total_chunks = 0

    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        print(f"📄 Inlezen van: {pdf_file} ...")
        pages_data = processor.extract_text_from_pdf(pdf_path)
        chunks = processor.create_chunks(pages_data)
        store.add_chunks(chunks)
        total_chunks += len(chunks)
        print(f"   ✓ {len(pages_data)} pagina's en {len(chunks)} tekstchunks geïndexeerd in ChromaDB.")

    print(f"🎉 Voltooid! Totaal {total_chunks} chunks toegevoegd aan de vector database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Political Program PDFs into ChromaDB.")
    parser.add_argument("--dir", type=str, default="samples", help="Map met PDF bestanden")
    parser.add_argument("--db", type=str, default="data/chroma_db", help="Pad naar ChromaDB opslag")
    args = parser.parse_args()

    ingest_directory(args.dir, args.db)
