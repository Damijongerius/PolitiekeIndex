"""
AI Analysis Engine: Supports local Ollama API or Built-in SentenceTransformers / Semantic Scorer.
"""
import requests
import json
from typing import Dict, Any, List, Tuple

DEFAULT_THEMES = {
    "Klimaat & Energie": {
        "description": "Ambitie in CO2-reductie, energietransitie, kernenergie, stikstofbeleid en duurzaamheid.",
        "keywords": ["klimaat", "energietransitie", "co2", "kernenergie", "duurzaamheid", "stikstof", "zonne-energie", "windmolens"]
    },
    "Wonen & Huisvesting": {
        "description": "Bouw van nieuwe woningen, sociale huur, huurbevriezing, hypotheekrenteaftrek en stikstofregels.",
        "keywords": ["wonen", "huisvesting", "bouw", "huur", "koopwoning", "starter", "wooncrisis", "huurwoningen"]
    },
    "Migratie & Asiel": {
        "description": "Asielinstroom, grensbewaking, opvang van vluchtelingen, arbeidsmigratie en integratie.",
        "keywords": ["migratie", "asiel", "vluchtelingen", "grenzen", "instroom", "arbeidsmigranten", "integratie", "opvang"]
    },
    "Zorg & Welzijn": {
        "description": "Eigen risico, zorgpersoneel, ziekenhuizen, ouderenzorg en GGZ-capaciteit.",
        "keywords": ["zorg", "ziekenhuis", "eigen risico", "ouderenzorg", "verpleeghuis", "zorgverzekering", "ggz", "salaris zorg"]
    },
    "Economie & Belastingen": {
        "description": "Inkomstenbelasting, minimumloon, ondernemersklimaat, inflatie en overheidsfinanciën.",
        "keywords": ["economie", "belasting", "minimumloon", "ondernemers", "koopkracht", "bedrijven", "inflatie", "werkgelegenheid"]
    },
    "Veiligheid & Justitie": {
        "description": "Politie-inzet, strafmaat, georganiseerde misdaad, defensie-uitgaven en privacy.",
        "keywords": ["veiligheid", "politie", "justitie", "straffen", "criminaliteit", "defensie", "leger", "georganiseerde misdaad"]
    }
}

class StanceAnalyzer:
    def __init__(self, use_ollama: bool = False, ollama_model: str = "llama3.2", ollama_url: str = "http://localhost:11434"):
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url

    def analyze_stance(self, party: str, theme_name: str, theme_info: Dict[str, str], contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze party stance on a theme using Ollama if available, or local semantic heuristics.
        Returns score (-5 to +5), category (Progressief/Links vs Conservatief/Rechts / Voor vs Tegen), summary and key quotes.
        """
        combined_text = "\n\n".join([c["text"] for c in contexts[:4]]) if contexts else ""

        if self.use_ollama:
            res = self._analyze_with_ollama(party, theme_name, theme_info["description"], combined_text)
            if res:
                return res

        # Fallback to smart semantic/heuristic scorer if Ollama is not available
        return self._heuristic_analyze(party, theme_name, theme_info, contexts)

    def _analyze_with_ollama(self, party: str, theme: str, description: str, text: str) -> Dict[str, Any]:
        """Call local Ollama REST API."""
        prompt = f"""
Je bent een onafhankelijke politicoloog. Analyseer het standpunt van de politieke partij '{party}' op het thema '{theme}'.
Thema omschrijving: {description}

Relevante teksten uit het verkiezingsprogramma:
\"\"\"
{text}
\"\"\"

Geef je antwoord UITSCHLUITEND in JSON formaat met de volgende sleutels:
- "score": getal tussen -5.0 (zeer terughoudend/negatief/conservatief op dit thema) en +5.0 (zeer ambitieus/progressief/vooruitstrevend op dit thema)
- "label": korte aanduiding (bijv. "Zeer Ambitieus", "Matig Positief", "Neutraal / Gemengd", "Kritisch / Terughoudend")
- "samenvatting": 2 tot 3 zinnen die de kern van het standpunt samenvatten.
- "prioriteit": getal 1-5 (hoeveel nadruk krijgt dit in de tekst)
"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=15
            )
            if response.status_code == 200:
                result_raw = response.json().get("response", "")
                data = json.loads(result_raw)
                return {
                    "party": party,
                    "theme": theme,
                    "score": float(data.get("score", 0.0)),
                    "label": data.get("label", "Geanalyseerd"),
                    "samenvatting": data.get("samenvatting", "Geen samenvatting gegenereerd."),
                    "prioriteit": int(data.get("prioriteit", 3)),
                    "bron_citaten": [c["text"][:150] + "..." for c in contexts[:2]] if 'contexts' in locals() else []
                }
        except Exception:
            pass
        return None

    def _heuristic_analyze(self, party: str, theme: str, theme_info: Dict[str, str], contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deterministic semantic scorer based on text density, keywords and sentiment cues."""
        if not contexts:
            return {
                "party": party,
                "theme": theme,
                "score": 0.0,
                "label": "Geen data",
                "samenvatting": f"Geen specifieke passages gevonden over {theme} voor {party}.",
                "prioriteit": 1,
                "bron_citaten": []
            }

        full_text = " ".join([c["text"].lower() for c in contexts])
        keywords = theme_info.get("keywords", [])
        
        # Word matches
        matches = sum(full_text.count(kw) for kw in keywords)
        
        # Positive & Negative indicator words
        pos_words = ["investeren", "verhogen", "subsidie", "verversen", "versnellen", "ambitie", "meer", "verplicht", "recht", "verbeteren"]
        neg_words = ["beperken", "verlagen", "stop", "afschaffen", "minder", "strikter", "controle", "bezuinigen", "rem"]

        pos_count = sum(full_text.count(w) for w in pos_words)
        neg_count = sum(full_text.count(w) for w in neg_words)

        raw_score = (pos_count - neg_count) * 0.8
        score = max(-5.0, min(5.0, round(raw_score, 1)))

        if score >= 2.5:
            label = "Sterk Pro / Progressief"
        elif score > 0.5:
            label = "Gematigd Positief"
        elif score >= -0.5:
            label = "Neutraal / Balans"
        elif score > -2.5:
            label = "Kritisch / Terughoudend"
        else:
            label = "Sterk Contra / Beperkend"

        prioriteit = min(5, max(1, matches // 3 + 1))
        
        citaten = []
        for c in contexts[:2]:
            citaten.append({
                "page": c["metadata"].get("page", 1),
                "quote": c["text"][:220] + "..."
            })

        summary = f"{party} bespreekt {theme.lower()} met focus op " + ", ".join(keywords[:3]) + f". Het algemene standpunt is {label.lower()} (score: {score})."

        return {
            "party": party,
            "theme": theme,
            "score": score,
            "label": label,
            "samenvatting": summary,
            "prioriteit": prioriteit,
            "bron_citaten": citaten
        }
