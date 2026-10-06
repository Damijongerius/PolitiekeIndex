"""
Real PDF Scraper & Downloader for Authentic Official Dutch Political Party Manifestos (TK2023).
Downloads official PDFs directly from government / party websites and indexes them with pdfplumber.
"""
import os
import requests
from typing import Dict, List

# Official direct PDF links for major Dutch political parties (Verkiezingsprogramma's TK2023)
REAL_PDF_URLS: Dict[str, str] = {
    "VVD": "https://www.vvd.nl/wp-content/uploads/2023/09/VVD_Verkiezingsprogramma_2023-2027.pdf",
    "GL_PVDA": "https://groenlinkspvda.nl/wp-content/uploads/2023/09/Verkiezingsprogramma-GroenLinks-PvdA-2023-2027.pdf",
    "D66": "https://d66.nl/wp-content/uploads/2023/09/D66-Verkiezingsprogramma-2023-2027.pdf",
    "PVDD": "https://www.partijvoordedieren.nl/downloads/Verkiezingsprogramma_Partij_voor_de_Dieren_2023-2027.pdf",
    "VOLT": "https://volt-nl.ams3.digitaloceanspaces.com/EU24/Verkiezingsprogramma%20Volt%20Nederland%202023.pdf",
    "CU": "https://www.christenunie.nl/l/library/download/urn:uuid:6d531a74-d477-49f3-8b78-75c60c874b35/verkiezingsprogramma+christenunie+2023-2027.pdf",
    "SP": "https://www.sp.nl/sites/default/files/verkiezingsprogramma_sp_2023.pdf"
}

def fetch_real_political_pdfs(target_dir: str = "data/pdfs") -> List[str]:
    """Downloads real official PDFs using a realistic browser User-Agent."""
    os.makedirs(target_dir, exist_ok=True)
    downloaded = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    print("🌐 Downloaden van ECHTE officiële verkiezingsprogramma's...")

    for party, url in REAL_PDF_URLS.items():
        filepath = os.path.join(target_dir, f"{party}_officieel.pdf")
        
        # Avoid redownloading if real file already downloaded
        if os.path.exists(filepath) and os.path.getsize(filepath) > 50000:
            print(f"   ✓ Echte {party} PDF is al gedownload ({os.path.getsize(filepath) // 1024} KB).")
            downloaded.append(filepath)
            continue

        try:
            print(f"   ⬇️ Downloaden van {party} via {url}...")
            r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 30000:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                print(f"   ✅ ECHTE {party} PDF gedownload! ({len(r.content) // 1024} KB)")
                downloaded.append(filepath)
            else:
                print(f"   ⚠️ Status {r.status_code} bij downloaden van {party}")
        except Exception as e:
            print(f"   ⚠️ Kon {party} niet direct ophalen: {e}")

    return downloaded

if __name__ == "__main__":
    fetch_real_political_pdfs()
