#!/usr/bin/env python3
"""
Tweede Kamer Scraper CLI
Gebruik dit script om zetels, fracties en Kamerleden te scrapen van tweedekamer.nl.

Gebruik:
    python scraper.py              # Haalt alle 17 fracties en Kamerleden op
    python scraper.py --quick      # Haalt alleen zetels en fractievoorzitters op (supersnel)
    python scraper.py --view       # Toont de huidige gecachete fracties en zetelverdeling
"""

import argparse
import sys
import os
from backend.tweedekamer_scraper import (
    scrape_all_fracties,
    get_cached_fracties,
    get_live_fracties,
    FRACTIES_URL
)

def print_table(fracties):
    print("\n" + "=" * 78)
    print(f"{'FRACTIE':<38} {'ZETELS':<8} {'FRACTIEVOORZITTER':<22} {'LEDEN':<6}")
    print("=" * 78)
    total_seats = 0
    total_members = 0
    for f in sorted(fracties, key=lambda x: x["seats"], reverse=True):
        total_seats += f["seats"]
        members_count = len(f.get("members", []))
        total_members += members_count
        name = f["name"][:36]
        leader = (f.get("leader") or "-")[:20]
        print(f"{name:<38} {f['seats']:<8} {leader:<22} {members_count:<6}")
    print("=" * 78)
    print(f"{'TOTAAL':<38} {total_seats:<8} {'':<22} {total_members:<6}")
    print("=" * 78 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Tweede Kamer Fracties & Zetels Scraper")
    parser.add_argument("--quick", action="store_true", help="Alleen overzicht scrapen (sneller, zonder Kamerleden details)")
    parser.add_argument("--view", action="store_true", help="Bekijk bestaande gecachete data zonder opnieuw te scrapen")
    parser.add_argument("--force", action="store_true", help="Forceer live herladen van tweedekamer.nl")

    args = parser.parse_args()

    if args.view:
        cached = get_cached_fracties()
        if not cached:
            print("Geen gecachete data gevonden. Draai 'python scraper.py' om data op te halen.")
            sys.exit(1)
        print(f"Gecachete data van: {cached.get('lastUpdated')}")
        print_table(cached["fracties"])
        return

    fetch_details = not args.quick
    print(f"Scrapen van {FRACTIES_URL}...")
    if args.quick:
        print("(Snelle modus: detailpagina's van Kamerleden worden overgeslagen)")

    data = scrape_all_fracties(fetch_details=fetch_details)
    print(f"\nSuccesvol {data['fractiesCount']} fracties opgehaald! (Totaal: {data['totalSeats']} zetels)")
    print_table(data["fracties"])
    print(f"Data opgeslagen in data/tweedekamer_fracties.json")

if __name__ == "__main__":
    main()
