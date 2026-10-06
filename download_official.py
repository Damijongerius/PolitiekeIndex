"""
Automatic Downloader that fetches ALL official PDF manifestos directly from verkiezingsprogrammasdownloaden.nl API!
Fixed URL encoding for spaces and special characters.
"""
import os
import urllib.request
import urllib.parse
import json

API_URL = "https://www.verkiezingsprogrammasdownloaden.nl/api/parties"
BASE_URL = "https://www.verkiezingsprogrammasdownloaden.nl"

def download_all_official_manifestos(target_dir: str = "data/pdfs"):
    os.makedirs(target_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    print("🌐 Ophalen van partijlijst via verkiezingsprogrammasdownloaden.nl API...")
    req = urllib.request.Request(API_URL, headers=headers)
    response = urllib.request.urlopen(req)
    parties = json.loads(response.read().decode("utf-8"))

    print(f"🎯 Gevonden {len(parties)} partijen in de database. Downloaden gestart...")

    downloaded_files = []

    for party in parties:
        name = party.get("name", "").replace(" ", "_").replace("/", "_")
        has_program = party.get("hasProgram", False)
        program_path = party.get("programPath", "")

        if has_program and program_path:
            encoded_path = urllib.parse.quote(program_path)
            full_pdf_url = BASE_URL + encoded_path
            filename = f"{name}.pdf"
            filepath = os.path.join(target_dir, filename)

            print(f"   ⬇️ Downloaden van {name}...")
            try:
                pdf_req = urllib.request.Request(full_pdf_url, headers=headers)
                pdf_res = urllib.request.urlopen(pdf_req)
                pdf_data = pdf_res.read()

                if len(pdf_data) > 1000:
                    with open(filepath, "wb") as f:
                        f.write(pdf_data)
                    print(f"   ✅ {filename} succesvol gedownload ({len(pdf_data) // 1024} KB)!")
                    downloaded_files.append(filepath)
            except Exception as e:
                print(f"   ⚠️ Fout bij downloaden van {name}: {e}")

    print(f"🎉 Totaal {len(downloaded_files)} officiële PDF-bestanden gedownload!")
    return downloaded_files

if __name__ == "__main__":
    download_all_official_manifestos()
