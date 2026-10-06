# PolitiekKompas NL 🇳🇱

> **Professionele Full-Stack Web Applicatie voor AI Analyse van Nederlandse Verkiezingsprogramma's & Politieke Standpunten.**

Gebouwd met een moderne, ontkoppelde tech-stack:
- **Frontend**: [Vite](https://vite.dev/) + [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/) + [Tailwind CSS](https://tailwindcss.com/) + [Lucide Icons](https://lucide.dev/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12) REST API met interactieve Swagger UI
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) Persistent Store (1.778 geïndexeerde chunks)
- **Document Extractie**: [pdfplumber](https://github.com/jsvine/pdfplumber) & [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)

---

## ✨ Functionaliteiten

1. **🎯 Standpunten & Stelling Checker (Live AI Semantic Search)**:
   - Voer een eigen stelling in of klik op samengestelde maatschappelijke vraagstukken.
   - Automatische bepaling van politieke dimensies (*Links/Rechts* en *Progressief/Conservatief*).
   - Directe standpuntsscores per partij van **-2 tot +2** (*Sterk Voor* tot *Sterk Tegen*).
   - Uitklapbare, geverifieerde bronpassages met exacte PDF paginanummers en citaten.

2. **🧭 Interactief Politiek Kieskompas (2D Ideologische Matrix)**:
   - Dynamische 2D matrix (Economisch Links-Rechts vs Maatschappelijk Progressief-Conservatief).
   - 4 duidelijke kwadranten (*Progressief-Links*, *Progressief-Rechts*, *Conservatief-Links*, *Conservatief-Rechts*).
   - Partij-bollen geschaald naar het aantal zetels in de Tweede Kamer in officiële huisstijlkleuren.
   - Mogelijkheid om geanalyseerde stellingen direct als doelpin te projecteren op het kompas.

3. **🏛️ Partij Dossiers & PDF Verkenner**:
   - Uitgebreide catalogus van 24 Nederlandse politieke partijen (zowel Tweede Kamer als buitenparlementair).
   - Gerenderde voorpagina's uit de officiële verkiezingsmanifesten.
   - Uiteengezette standpunten over de 6 kernthema's: *Klimaat & Energie*, *Wonen*, *Zorg*, *Migratie*, *Economie*, *Veiligheid*.
   - Ingebouwde interactieve PDF-tekst browser met paginaschuifbalk.

4. **⚖️ Zij-aan-Zij Thema Vergelijker**:
   - Vergelijk 2 tot 5 partijen gelijktijdig.
   - Direct overzicht van overeenkomsten, verschillen en beleidsvoorstellen per thema.

---

## 🚀 Snelle Start

### 1. Virtuele Omgeving & Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend Dependencies Installeren
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Server Starten

#### Productiemodus (één commando):
Start de FastAPI server die zowel de API als de React SPA host op poort 8000:
```bash
python3 run.py
```
Open **[http://localhost:8000](http://localhost:8000)** in je browser.  
Open **[http://localhost:8000/docs](http://localhost:8000/docs)** voor de interactieve OpenAPI / Swagger documentatie.

#### Ontwikkelmodus (Vite Hot Module Replacement + FastAPI Reload):
```bash
python3 run.py --dev
```
- Frontend (Vite HMR): **[http://localhost:5173](http://localhost:5173)**
- Backend (FastAPI): **[http://localhost:8000](http://localhost:8000)**

---

## 🐳 Uitvoeren met Docker

Het gehele project (React frontend + FastAPI backend + ChromaDB vector database) is volledig gecontaineriseerd in een multi-stage build.

### Optie 1: Met Docker Compose (Aanbevolen)
```bash
docker compose up --build
```
Of op de achtergrond:
```bash
docker compose up -d
```

### Optie 2: Met de Docker CLI
Bouw het image:
```bash
docker build -t politiekkompas .
```
Start de container (met data volume mount voor persistentie van ChromaDB en PDF's):
```bash
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data --name politiekkompas politiekkompas
```

Open **[http://localhost:8000](http://localhost:8000)** in je browser.

---

## 📂 Project Structuur

```
├── backend/
│   ├── main.py              # FastAPI server, endpoints, static serving
│   ├── models.py            # Pydantic data schema's (Stelling, Partij, Thema, Kompas)
│   ├── party_data.py        # Partijen catalogus (kleuren, zetels, kompas coördinaten, aliassen)
│   └── services.py          # Business logic: ChromaDB semantische zoekopdrachten, scoring & citaten
├── frontend/
│   ├── src/
│   │   ├── api/client.ts    # Type-safe API client
│   │   ├── components/      # React componenten (StellingChecker, PoliticalCompass, etc.)
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx          # Hoofdlayout & tab router
│   │   └── main.tsx         # React root
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── data/
│   ├── chroma_db/           # Persistent ChromaDB vector database (1.778 chunks)
│   ├── pdfs/                # 24 Officiële PDF verkiezingsprogramma's
│   └── covers/              # Gerenderde voorpagina's van alle PDF manifestos
├── run.py                   # Universele launcher voor productie en dev
├── requirements.txt         # Python dependencies
└── README.md
```
