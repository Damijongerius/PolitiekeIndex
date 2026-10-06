"""
Tweede Kamer Fracties Scraper
Scrapes official parliamentary factions, seats (zetels), fraction leaders (fractievoorzitters),
member lists (Kamerleden) with photos and profile links, and contact information from:
https://www.tweedekamer.nl/kamerleden_en_commissies/fracties
"""

import os
import json
import time
import socket
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

# Ensure network calls don't hang indefinitely
socket.setdefaulttimeout(12)

BASE_URL = "https://www.tweedekamer.nl"
FRACTIES_URL = "https://www.tweedekamer.nl/kamerleden_en_commissies/fracties"
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "tweedekamer_fracties.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "nl,en;q=0.9",
    "Connection": "close"
}

def fetch_html(url: str, retries: int = 3, timeout: int = 12) -> str:
    """Fetch HTML content with retries and a clean connection."""
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            last_err = e
            time.sleep(0.8 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {last_err}")

def slugify_party_name(name: str) -> str:
    """Normalize a party/faction name to a standard ID."""
    clean = name.lower().strip()
    mapping = {
        "democraten 66": "d66",
        "d66": "d66",
        "volkspartij voor vrijheid en democratie": "vvd",
        "vvd": "vvd",
        "progressief nederland": "gl-pvda",
        "pro": "gl-pvda",
        "partij voor de vrijheid": "pvv",
        "pvv": "pvv",
        "christen-democratisch appèl": "cda",
        "cda": "cda",
        "ja21": "ja21",
        "forum voor democratie": "fvd",
        "fvd": "fvd",
        "boerburgerbeweging": "bbb",
        "bbb": "bbb",
        "denk": "denk",
        "staatkundig gereformeerde partij": "sgp",
        "sgp": "sgp",
        "partij voor de dieren": "pvdd",
        "pvdd": "pvdd",
        "christenunie": "christenunie",
        "socialistische partij": "sp",
        "sp": "sp",
        "50plus": "50plus",
        "volt": "volt",
        "groep markuszower": "groep-markuszower",
        "groep-markuszower": "groep-markuszower",
        "lid keijzer": "lid-keijzer",
        "lid-keijzer": "lid-keijzer",
    }
    for k, v in mapping.items():
        if k in clean:
            return v
    slug = "".join(c if c.isalnum() else "-" for c in clean)
    return "-".join(filter(None, slug.split("-")))

def scrape_fracties_overview() -> List[Dict[str, Any]]:
    """Scrapes the main fracties overview page."""
    html = fetch_html(FRACTIES_URL)
    soup = BeautifulSoup(html, "html.parser")
    
    parties = []
    cards = soup.find_all("div", class_=lambda c: c and "u-bg-white" in c and "u-rounded-md" in c)
    
    for card in cards:
        h2 = card.find("h2")
        if not h2:
            continue
        a = h2.find("a", href=True)
        if not a:
            continue
        
        party_name = a.get_text(strip=True)
        detail_url = urllib.parse.urljoin(BASE_URL, a["href"])
        
        # Logo
        logo_img = card.find("img", alt=lambda alt: alt and "logo" in str(alt).lower())
        if not logo_img:
            imgs = card.find_all("img")
            logo_img = imgs[0] if imgs else None
        logo_url = urllib.parse.urljoin(BASE_URL, logo_img["src"]) if logo_img else None
        
        # Seats
        seat_span = card.find("span", class_=lambda c: c and "u-rounded-full" in c)
        seats = int(seat_span.get_text(strip=True)) if (seat_span and seat_span.get_text(strip=True).isdigit()) else 0
        
        # Leader (Fractievoorzitter)
        leader_avatar = card.find("figure", class_=lambda c: c and "m-avatar" in c)
        leader_name = None
        leader_photo = None
        leader_role = None
        if leader_avatar:
            img = leader_avatar.find("img")
            if img and img.get("src"):
                leader_photo = urllib.parse.urljoin(BASE_URL, img["src"])
            info_div = leader_avatar.find_next_sibling("div")
            if info_div:
                spans = info_div.find_all("span")
                if len(spans) >= 2:
                    leader_role = spans[0].get_text(strip=True)
                    leader_name = spans[1].get_text(strip=True)
                elif len(spans) == 1:
                    leader_name = spans[0].get_text(strip=True)
                else:
                    leader_name = info_div.get_text(strip=True)
                    
        parties.append({
            "id": slugify_party_name(party_name),
            "name": party_name,
            "seats": seats,
            "leader": leader_name,
            "leaderRole": leader_role or "Fractievoorzitter",
            "leaderPhoto": leader_photo,
            "logo": logo_url,
            "detailUrl": detail_url,
            "fullTitle": party_name,
            "website": None,
            "email": None,
            "phone": None,
            "members": [],
            "totalMembers": 0
        })
        
    return parties

def scrape_fractie_detail(party: Dict[str, Any]) -> Dict[str, Any]:
    """Scrapes detail page for a single party/fractie."""
    url = party.get("detailUrl")
    if not url:
        return party
        
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        
        h1 = soup.find("h1")
        party["fullTitle"] = h1.get_text(strip=True) if h1 else party["name"]
        
        website = None
        email = None
        phone = None
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("mailto:"):
                email = href.replace("mailto:", "").split("?")[0].strip()
            elif href.startswith("tel:"):
                phone = href.replace("tel:", "").strip()
            elif ("http" in href) and ("tweedekamer.nl" not in href) and ("houseofrepresentatives" not in href) and ("lijstvangevallenen" not in href):
                if not website:
                    website = href
                    
        party["website"] = website
        party["email"] = email
        party["phone"] = phone
        
        members = []
        for h3 in soup.find_all("h3"):
            card = h3.find_parent(class_=lambda c: c and "m-card" in str(c))
            if card:
                m_link = card.find("a", href=True)
                m_img = card.find("img")
                role_span = card.find(class_=lambda c: c and "u-text-sm" in str(c))
                members.append({
                    "name": h3.get_text(strip=True),
                    "link": urllib.parse.urljoin(BASE_URL, m_link["href"]) if m_link else None,
                    "photo": urllib.parse.urljoin(BASE_URL, m_img["src"]) if (m_img and m_img.get("src")) else None,
                    "role": role_span.get_text(strip=True) if role_span else "Tweede Kamerlid"
                })
                
        party["members"] = members
        party["totalMembers"] = len(members)
    except Exception as e:
        print(f"Let op: kon details voor {party.get('name')} niet laden: {e}")
        
    return party

def scrape_all_fracties(fetch_details: bool = True, polite_delay: float = 0.2) -> Dict[str, Any]:
    """Scrapes all fracties and optionally their detail pages."""
    print("Scrapen van overzichtspagina...")
    parties = scrape_fracties_overview()
    print(f"Gevonden: {len(parties)} fracties.")
    
    if fetch_details:
        for idx, p in enumerate(parties):
            print(f"[{idx+1}/{len(parties)}] Ophalen details: {p['name']} ({p['seats']} zetels)...")
            scrape_fractie_detail(p)
            if idx < len(parties) - 1 and polite_delay > 0:
                time.sleep(polite_delay)
                
    total_seats = sum(p["seats"] for p in parties)
    payload = {
        "lastUpdated": datetime.now().isoformat(),
        "sourceUrl": FRACTIES_URL,
        "totalSeats": total_seats,
        "fractiesCount": len(parties),
        "fracties": parties
    }
    
    # Save to disk cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    return payload

def normalize_cached_data(data: Any) -> Dict[str, Any]:
    """Normalizes raw cached json into canonical dictionary structure."""
    if isinstance(data, list):
        items = []
        for p in data:
            item = {
                "id": slugify_party_name(p.get("name", "")),
                "name": p.get("name", ""),
                "seats": p.get("seats", 0),
                "leader": p.get("leader"),
                "leaderRole": p.get("leader_role") or p.get("leaderRole") or "Fractievoorzitter",
                "leaderPhoto": p.get("leader_photo") or p.get("leaderPhoto"),
                "logo": p.get("logo"),
                "detailUrl": p.get("detail_url") or p.get("detailUrl") or "",
                "fullTitle": p.get("full_title") or p.get("fullTitle") or p.get("name", ""),
                "website": p.get("website"),
                "email": p.get("email"),
                "phone": p.get("phone"),
                "members": p.get("members", []),
                "totalMembers": len(p.get("members", []))
            }
            items.append(item)
        return {
            "lastUpdated": datetime.now().isoformat(),
            "sourceUrl": FRACTIES_URL,
            "totalSeats": sum(i["seats"] for i in items),
            "fractiesCount": len(items),
            "fracties": items
        }
    elif isinstance(data, dict):
        if "fracties" in data:
            for p in data["fracties"]:
                if "id" not in p:
                    p["id"] = slugify_party_name(p.get("name", ""))
                if "leaderRole" not in p and "leader_role" in p:
                    p["leaderRole"] = p["leader_role"]
                if "leaderPhoto" not in p and "leader_photo" in p:
                    p["leaderPhoto"] = p["leader_photo"]
                if "detailUrl" not in p and "detail_url" in p:
                    p["detailUrl"] = p["detail_url"]
                if "fullTitle" not in p and "full_title" in p:
                    p["fullTitle"] = p["full_title"]
                if "totalMembers" not in p:
                    p["totalMembers"] = len(p.get("members", []))
            return data
    return {
        "lastUpdated": datetime.now().isoformat(),
        "sourceUrl": FRACTIES_URL,
        "totalSeats": 0,
        "fractiesCount": 0,
        "fracties": []
    }

def get_cached_fracties() -> Optional[Dict[str, Any]]:
    """Loads cached data if available."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return normalize_cached_data(data)
        except Exception as e:
            print(f"Fout bij inladen cache: {e}")
            return None
    return None

def get_live_fracties(force_refresh: bool = False, fetch_details: bool = True) -> Dict[str, Any]:
    """Returns fracties data, either from cache or live scrape."""
    if not force_refresh:
        cached = get_cached_fracties()
        if cached and cached.get("fracties"):
            return cached
            
    return scrape_all_fracties(fetch_details=fetch_details)

if __name__ == "__main__":
    result = scrape_all_fracties(fetch_details=True)
    print(f"\nScraping voltooid: {result['fractiesCount']} fracties, {result['totalSeats']} zetels.")
