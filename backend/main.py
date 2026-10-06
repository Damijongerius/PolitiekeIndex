"""
FastAPI Server for PolitiekKompas NL / Nederlandse Politiek Analytics
Provides high-performance REST APIs for party manifestos, statement evaluations,
side-by-side comparisons, political compass coordinates, and PDF document exploration.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.models import (
    PartySummary, PartyDetail, StatementRequest, StatementEvaluationResponse,
    CompareRequest, CompareResponse, CompassResponse, TweedeKamerResponse
)
from backend.services import PoliticalAnalysisService
from backend.party_data import THEMES_CATALOG, PARTIES_CATALOG
from backend.tweedekamer_scraper import get_live_fracties, scrape_all_fracties


app = FastAPI(
    title="PolitiekKompas NL API",
    description="Professionele REST API voor analyse van Nederlandse verkiezingsprogramma's via ChromaDB en AI",
    version="2.0.0"
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = PoliticalAnalysisService()

# Curated Preset Statements
PRESET_STATEMENTS = [
    {
        "id": "kernenergie",
        "category": "Klimaat & Energie",
        "statement": "Er moeten per direct meer kerncentrales gebouwd worden in Nederland.",
        "icon": "Atom"
    },
    {
        "id": "eigen_risico",
        "category": "Zorg & Welzijn",
        "statement": "Het eigen risico in de basisverzekering moet volledig worden afgeschaft.",
        "icon": "HeartPulse"
    },
    {
        "id": "asielinstroom",
        "category": "Migratie & Asiel",
        "statement": "De asielinstroom moet sterk worden beperkt met een tijdelijke asielstop en strengere grenscontroles.",
        "icon": "ShieldAlert"
    },
    {
        "id": "minimumloon",
        "category": "Economie & Koopkracht",
        "statement": "Het minimumloon en de gekoppelde uitkeringen moeten substantieel verhoogd worden naar minimaal 16 euro per uur.",
        "icon": "Coins"
    },
    {
        "id": "stikstof",
        "category": "Landbouw & Natuur",
        "statement": "De stikstofregels voor agrariërs en woningbouwprojecten moeten versoepeld worden.",
        "icon": "Tractor"
    },
    {
        "id": "vermogen",
        "category": "Economie & Belastingen",
        "statement": "Er moet een substantiële vermogens- en miljonairsbelasting komen voor de hoogste inkomens.",
        "icon": "TrendingUp"
    },
    {
        "id": "ov_gratis",
        "category": "Infrastructuur & Verkeer",
        "statement": "Het openbaar vervoer moet gratis of sterk gesubsidieerd worden voor studenten en ouderen.",
        "icon": "Train"
    },
    {
        "id": "defensie",
        "category": "Veiligheid & Defensie",
        "statement": "Nederland moet structureel voldoen aan de NAVO-norm van minimaal 2% van het bbp voor defensie.",
        "icon": "ShieldCheck"
    }
]

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "parties_indexed": len(PARTIES_CATALOG),
        "themes_count": len(THEMES_CATALOG),
        "db_chunks_count": service.store.collection.count()
    }

@app.get("/api/presets")
def get_presets():
    return PRESET_STATEMENTS

@app.get("/api/themes")
def get_themes():
    return list(THEMES_CATALOG.values())

@app.get("/api/tweedekamer/fracties", response_model=TweedeKamerResponse)
def get_tweedekamer_fracties(refresh: bool = Query(False, description="Force fresh scrape from tweedekamer.nl")):
    """Returns official Tweede Kamer factions, seats, chairs, and parliament members."""
    data = get_live_fracties(force_refresh=refresh)
    return data

@app.post("/api/tweedekamer/scrape", response_model=TweedeKamerResponse)
def trigger_tweedekamer_scrape():
    """Triggers complete fresh scrape of Tweede Kamer fracties and Kamerleden."""
    data = scrape_all_fracties(fetch_details=True)
    return data

@app.get("/api/parties", response_model=List[PartySummary])
def get_parties():

    """Returns list of all political parties with metadata."""
    return service.get_party_summaries()

@app.get("/api/parties/{party_id}", response_model=PartyDetail)
def get_party(party_id: str):
    """Returns full details and theme breakdown of a party."""
    party = service.get_party_detail(party_id)
    if not party:
        raise HTTPException(status_code=404, detail=f"Party '{party_id}' not found")
    return party

@app.get("/api/parties/{party_id}/cover")
def get_party_cover(party_id: str):
    """Serves party PDF cover image."""
    p = PARTIES_CATALOG.get(party_id)
    if not p:
        raise HTTPException(status_code=404, detail="Party not found")
    
    cover_path = os.path.join(service.covers_dir, p["coverFilename"])
    if os.path.exists(cover_path):
        return FileResponse(cover_path, media_type="image/png")
    
    # Fallback to general cover if available
    alt_cover = os.path.join(service.covers_dir, f"{p['name']}_cover.png")
    if os.path.exists(alt_cover):
        return FileResponse(alt_cover, media_type="image/png")

    raise HTTPException(status_code=404, detail="Cover image not found")

@app.get("/api/parties/{party_id}/pdf")
def download_party_pdf(party_id: str):
    """Download party PDF manifesto."""
    p = PARTIES_CATALOG.get(party_id)
    if not p:
        raise HTTPException(status_code=404, detail="Party not found")

    pdf_path = os.path.join(service.pdf_dir, p["pdfFilename"])
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF manifesto not found on server")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=p["pdfFilename"]
    )

@app.get("/api/parties/{party_id}/pages/{page_num}")
def get_party_page(party_id: str, page_num: int):
    """Extracts raw text of a specific page from the party's PDF."""
    res = service.extract_page_text(party_id, page_num)
    if "error" in res and res["error"].startswith("Party not found"):
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@app.post("/api/evaluate", response_model=StatementEvaluationResponse)
def evaluate_statement(req: StatementRequest):
    """Evaluates a statement across all parties and maps to political dimensions."""
    if not req.statement or not req.statement.strip():
        raise HTTPException(status_code=400, detail="Statement cannot be empty")
    return service.evaluate_statement_for_all_parties(req.statement.strip())

@app.get("/api/compass", response_model=CompassResponse)
def get_compass():
    """Returns political compass coordinates for all parties."""
    return service.get_compass_data()

@app.post("/api/compare", response_model=CompareResponse)
def compare_parties(req: CompareRequest):
    """Compares multiple parties across chosen themes."""
    if not req.party_ids:
        raise HTTPException(status_code=400, detail="Provide at least one party ID to compare")
    return service.compare_parties(req.party_ids, req.theme_keys)

# Mount frontend/dist for production serving
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Do not intercept api routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not Found")
        target = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(target) and os.path.isfile(target):
            return FileResponse(target)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

