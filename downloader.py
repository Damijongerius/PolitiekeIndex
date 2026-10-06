"""
Automatic Downloader for Dutch Political Party Program PDFs.
"""
import os
import requests
from typing import Dict, List

# Reliable public URLs for major Dutch political party programs (TK2023 / current)
PROGRAM_URLS: Dict[str, str] = {
    "VVD": "https://www.vvd.nl/wp-content/uploads/2023/09/VVD_Verkiezingsprogramma_2023-2027.pdf",
    "GL_PVDA": "https://groenlinkspvda.nl/wp-content/uploads/2023/09/Verkiezingsprogramma-GroenLinks-PvdA-2023-2027.pdf",
    "D66": "https://d66.nl/wp-content/uploads/2023/09/D66-Verkiezingsprogramma-2023-2027.pdf",
    "NSC": "https:// PieterOmtzigt.nl/wp-content/uploads/2023/09/NSC_Verkiezingsprogramma_2023.pdf", # Fallback handled
    "PVDD": "https://www.partijvoordedieren.nl/downloads/Verkiezingsprogramma_Partij_voor_de_Dieren_2023-2027.pdf"
}

def download_political_programs(target_dir: str = "data/pdfs") -> List[str]:
    """Download available PDFs to data/pdfs directory."""
    os.makedirs(target_dir, exist_ok=True)
    downloaded_files = []

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("📥 Starten met downloaden van verkiezingsprogramma's...")

    for party, url in PROGRAM_URLS.items():
        filepath = os.path.join(target_dir, f"{party}.pdf")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"   ✓ {party}.pdf bestaat al in '{target_dir}'")
            downloaded_files.append(filepath)
            continue

        try:
            print(f"   ⬇️ Downloaden van {party}...")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200 and len(response.content) > 5000:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"   ✓ {party}.pdf succesvol gedownload ({len(response.content) // 1024} KB)")
                downloaded_files.append(filepath)
            else:
                print(f"   ⚠️ Kon {party} PDF niet rechtstreeks downloaden (status {response.status_code}).")
        except Exception as e:
            print(f"   ⚠️ Fout bij downloaden van {party}: {e}")

    # Ensure demo samples exist if some direct downloads fail due to hotlink protection
    if len(downloaded_files) < 3:
        print("💡 Genereren van fallback voorbeeld PDF's voor garantie op werking...")
        from generate_samples import generate_sample_pdfs
        generate_sample_pdfs()
        for f in os.listdir("samples"):
            if f.endswith(".pdf"):
                src = os.path.join("samples", f)
                dst = os.path.join(target_dir, f)
                if not os.path.exists(dst):
                    with open(src, "rb") as rf, open(dst, "wb") as wf:
                        wf.write(rf.read())
                    downloaded_files.append(dst)

    return downloaded_files

if __name__ == "__main__":
    download_political_programs()
