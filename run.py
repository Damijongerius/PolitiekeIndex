#!/usr/bin/env python3
"""
Launcher script for PolitiekKompas NL.
Starts FastAPI backend (port 8000) and optionally Vite dev server (port 5173).
"""

import sys
import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="PolitiekKompas NL Launcher")
    parser.add_argument("--dev", action="store_true", help="Start with Vite Dev Server with hot reloading")
    parser.add_argument("--port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--scrape", action="store_true", help="Scrapeer live zetels en fracties van tweedekamer.nl")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, "frontend", "dist")

    if args.scrape:
        print("🏛️ Scrapen van live Tweede Kamer data...")
        from backend.tweedekamer_scraper import scrape_all_fracties
        res = scrape_all_fracties(fetch_details=True)
        print(f"✅ {res['fractiesCount']} fracties gescrapet met in totaal {res['totalSeats']} zetels.")

    # If dist doesn't exist and not in dev mode, build it first
    if not os.path.exists(dist_dir) and not args.dev:

        print("⚡ Bouwen van de React frontend voor productie...")
        subprocess.run(["npm", "run", "build"], cwd=os.path.join(project_root, "frontend"), check=True)

    if args.dev:
        print(f"🚀 Dev Mode gestart:")
        print(f"   - Backend API: http://{args.host}:{args.port}/docs")
        print(f"   - Frontend Vite HMR: http://localhost:5173")
        
        # Start Vite in background and Uvicorn in foreground
        vite_proc = subprocess.Popen(["npm", "run", "dev"], cwd=os.path.join(project_root, "frontend"))
        try:
            import uvicorn
            uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=True)
        finally:
            vite_proc.terminate()
    else:
        print(f"🏛️ PolitiekKompas NL Productieserver draait op:")
        print(f"   👉 http://{args.host}:{args.port}")
        print(f"   👉 API Documentatie: http://{args.host}:{args.port}/docs")
        
        import uvicorn
        uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
