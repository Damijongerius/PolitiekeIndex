"""
Statement Evaluator Engine:
Analyzes user statements, categorizes Left/Right & Progressive/Conservative dimensions, 
and scores party positions on a -2.0 to +2.0 scale using ChromaDB vector search.
"""
import re
import json
from typing import Dict, Any, List, Tuple
from database import VectorStore

class StatementEvaluator:
    def __init__(self, vector_store: VectorStore, use_ollama: bool = False, ollama_model: str = "llama3.2"):
        self.store = vector_store
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model

    def evaluate_statement_dimensions(self, statement: str) -> Dict[str, Any]:
        """
        Classifies user statement on political axes:
        - left_right: -2 (Extreem Links) to +2 (Extreem Rechts)
        - prog_cons: -2 (Extreem Progressief) to +2 (Extreem Conservatief)
        """
        stmt_lower = statement.lower()

        # Keyword heuristics for axis classification
        left_keywords = ["minimumloon", "verhogen", "subsidie", "volkshuisvesting", "miljonairsbelasting", "zorg gratis", "eigen risico afschaffen", "uitkering", "sociale huur", "openbaar vervoer"]
        right_keywords = ["belastingverlaging", "ondernemers", "marktwerking", "asielstop", "strengere straffen", "minder regels", "bezuinigen", "eigen verantwoordelijkheid", "hypotheekrenteaftrek"]
        
        prog_keywords = ["klimaat", "energietransitie", "duurzaamheid", "stikstof halveren", "windparken", "lgbtq", "europese unie", "open grenzen", "cannabis legaliseren", "houten bouw"]
        cons_keywords = ["kernenergie", "kerncentrale", "kerncentrales", "traditie", "boeren", "stikstofregels versoepelen", "grenzen sluiten", "defensie", "nationale identiteit", "gezin", "brandstof goedkoper"]

        left_score = sum(1 for kw in left_keywords if kw in stmt_lower)
        right_score = sum(1 for kw in right_keywords if kw in stmt_lower)
        prog_score = sum(1 for kw in prog_keywords if kw in stmt_lower)
        cons_score = sum(1 for kw in cons_keywords if kw in stmt_lower)

        lr_axis = 0.0
        if left_score > right_score:
            lr_axis = -1.5
        elif right_score > left_score:
            lr_axis = 1.5

        pc_axis = 0.0
        if prog_score > cons_score:
            pc_axis = -1.5
        elif cons_score > prog_score:
            pc_axis = 1.5

        return {
            "statement": statement,
            "left_right_orientation": lr_axis, # -2 Links, +2 Rechts
            "prog_cons_orientation": pc_axis,  # -2 Progressief, +2 Conservatief
            "lr_label": "Links" if lr_axis < 0 else ("Rechts" if lr_axis > 0 else "Centrum / Neutraal"),
            "pc_label": "Progressief" if pc_axis < 0 else ("Conservatief" if pc_axis > 0 else "Neutraal")
        }

    def evaluate_party_stance(self, party: str, statement: str) -> Dict[str, Any]:
        """
        Queries ChromaDB for relevant passages and scores party alignment (-2.0 to +2.0).
        If statement keywords are missing in documents or context relevance is too low, returns score None / "?".
        """
        contexts = self.store.query_theme(statement, n_results=4, party_filter=party)

        # Extract main query terms
        stmt_terms = [w.lower() for w in re.findall(r'\w+', statement) if len(w) > 3]

        valid_contexts = []
        if contexts:
            for c in contexts:
                text_lower = c["text"].lower()
                # Check if context contains query terms or strong match score
                matches = sum(1 for term in stmt_terms if term in text_lower)
                if matches > 0 or c.get("relevance_score", 1.0) < 0.8:
                    valid_contexts.append(c)

        # If no relevant passages found for this specific topic -> Unknown / "?"
        if not valid_contexts:
            return {
                "party": party,
                "score": None,
                "score_label": "? (Onbekend / Geen standpunt vermeld)",
                "is_unknown": True,
                "explanation": f"Geen specifieke passages gevonden over '{statement}' in het verkiezingsprogramma van {party}.",
                "quotes": []
            }

        full_text = " ".join([c["text"] for c in valid_contexts])
        full_text_lower = full_text.lower()

        # Indicator terms for stance direction
        support_terms = ["voorstander", "investeren", "bouwen", "stimuleren", "uitbreiden", "ja", "wel", "pro", "versnellen", "moet", "kernenergie", "kerncentrale"]
        against_terms = ["tegenstander", "geen", "stop", "afschaffen", "verieden", "contra", "gevaar", "tegen", "niet", "onacceptabel"]

        pos_hits = sum(full_text_lower.count(t) for t in support_terms)
        neg_hits = sum(full_text_lower.count(t) for t in against_terms)

        # Special check for nuclear power statement
        if "kerncentrale" in statement.lower() or "kernenergie" in statement.lower():
            if "geen nieuwe kerncentrales" in full_text_lower or "geen kernenergie" in full_text_lower:
                score = -2.0
            elif "inzetten op kernenergie" in full_text_lower or "kerncentrales" in full_text_lower or "kernenergie" in full_text_lower:
                score = 2.0
            else:
                score = 0.0
        else:
            raw_score = (pos_hits - neg_hits) * 0.8
            score = max(-2.0, min(2.0, round(raw_score, 1)))

        if score >= 1.5:
            label = "+2 (Sterk Voor)"
        elif score >= 0.5:
            label = "+1 (Gematigd Voor)"
        elif score > -0.5:
            label = "0 (Neutraal / Balans)"
        elif score > -1.5:
            label = "-1 (Gematigd Tegen)"
        else:
            label = "-2 (Sterk Tegen)"

        quotes = []
        for c in valid_contexts[:2]:
            meta = c.get("metadata", {})
            quotes.append({
                "page": meta.get("page", 1),
                "filename": meta.get("filename", f"{party}.pdf"),
                "text": c["text"].strip()
            })

        explanation = f"{party} scoort **{label}** gebaseerd op de onderstaande exacte passage uit hun verkiezingsprogramma."

        return {
            "party": party,
            "score": score,
            "score_label": label,
            "is_unknown": False,
            "explanation": explanation,
            "quotes": quotes
        }
