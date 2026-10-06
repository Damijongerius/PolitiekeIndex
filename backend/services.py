"""
Business logic and analytics services for political stance evaluation,
theme breakdowns, vector retrieval, and compass computations.
"""
import os
import re
from typing import List, Dict, Any, Optional
from database import VectorStore
from backend.party_data import PARTIES_CATALOG, THEMES_CATALOG
from backend.models import (
    Quote, PartyStance, Dimensions, StatementEvaluationResponse,
    CompassParty, CompassResponse, PartySummary, PartyDetail,
    ThemeDetail, ThemeComparisonItem, CompareResponse, FractieInfo
)


class PoliticalAnalysisService:
    def __init__(self, db_dir: str = "data/chroma_db", pdf_dir: str = "data/pdfs", covers_dir: str = "data/covers"):
        self.store = VectorStore(db_dir=db_dir)
        self.pdf_dir = pdf_dir
        self.covers_dir = covers_dir
        self._theme_cache: Dict[str, Dict[str, ThemeDetail]] = {}
        self._page_count_cache: Dict[str, int] = {}

    def _get_tk_fractie(self, party_id: str) -> Optional[FractieInfo]:
        from backend.tweedekamer_scraper import get_cached_fracties
        cached = get_cached_fracties()
        if not cached:
            return None
        fracties = cached.get("fracties", [])
        for f in fracties:
            if f.get("id") == party_id:
                try:
                    return FractieInfo(**f)
                except Exception:
                    pass
        p_info = PARTIES_CATALOG.get(party_id)
        if p_info:
            target_name = p_info["name"].lower()
            target_full = p_info["fullName"].lower()
            for f in fracties:
                fn = f.get("name", "").lower()
                if fn in target_name or fn in target_full or target_name in fn:
                    try:
                        return FractieInfo(**f)
                    except Exception:
                        pass
        return None

    def get_party_summaries(self) -> List[PartySummary]:
        """Returns clean list of all parties with metadata and status."""
        results = []
        for pid, p in PARTIES_CATALOG.items():
            pdf_path = os.path.join(self.pdf_dir, p["pdfFilename"])
            pdf_available = os.path.exists(pdf_path)
            cover_url = f"/api/parties/{pid}/cover"
            pdf_url = f"/api/parties/{pid}/pdf"

            page_count = self._get_page_count(pid, pdf_path) if pdf_available else None
            tk_data = self._get_tk_fractie(pid)

            results.append(PartySummary(
                id=pid,
                name=p["name"],
                fullName=p["fullName"],
                leader=p["leader"],
                seats=p["seats"],
                inParliament=p["inParliament"],
                orientation=p["orientation"],
                color=p["color"],
                textColor=p["textColor"],
                pdfAvailable=pdf_available,
                coverUrl=cover_url,
                pdfUrl=pdf_url,
                pageCount=page_count,
                compass=p["compass"],
                shortDescription=p["shortDescription"],
                tkData=tk_data
            ))
        return results


    def _get_page_count(self, party_id: str, pdf_path: str) -> int:
        if party_id in self._page_count_cache:
            return self._page_count_cache[party_id]
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(pdf_path)
            count = len(pdf)
            self._page_count_cache[party_id] = count
            return count
        except Exception:
            return 0

    def query_party_chunks(self, party_id: str, query: str, n_results: int = 4) -> List[Dict[str, Any]]:
        """Query ChromaDB across all aliases of the given party."""
        party_info = PARTIES_CATALOG.get(party_id)
        if not party_info:
            return []

        aliases = party_info.get("dbAliases", [party_info["name"]])
        where_clause = None
        if len(aliases) == 1:
            where_clause = {"party": aliases[0]}
        elif len(aliases) > 1:
            where_clause = {"$or": [{"party": a} for a in aliases]}

        try:
            results = self.store.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            formatted = []
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                for doc, meta, dist in zip(docs, metas, dists):
                    formatted.append({
                        "text": doc,
                        "metadata": meta,
                        "relevance_score": float(dist)
                    })
            return formatted
        except Exception as e:
            print(f"Error querying ChromaDB for {party_id}: {e}")
            return []

    def evaluate_statement_dimensions(self, statement: str) -> Dimensions:
        """Classifies statement on Left/Right and Progressive/Conservative axes."""
        stmt_lower = statement.lower()

        left_keywords = [
            "minimumloon", "verhogen", "subsidie", "volkshuisvesting", "miljonairsbelasting",
            "zorg gratis", "eigen risico afschaffen", "uitkering", "sociale huur", "openbaar vervoer",
            "nationaal zorgfonds", "rijkste", "basisbeurs", "eerlijker delen", "werknemers", "staatsbedrijf"
        ]
        right_keywords = [
            "belastingverlaging", "ondernemers", "marktwerking", "asielstop", "strengere straffen",
            "minder regels", "bezuinigen", "eigen verantwoordelijkheid", "hypotheekrenteaftrek",
            "vrije markt", "kleinere overheid", "lastenverlichting", "concurrentiepositie", "veiligheid"
        ]
        prog_keywords = [
            "klimaat", "energietransitie", "duurzaamheid", "stikstof halveren", "windparken",
            "lgbtq", "lhbti", "europese unie", "open grenzen", "cannabis legaliseren", "houten bouw",
            "biodiversiteit", "circulair", "trein", "inclusiviteit", "dierenrechten"
        ]
        cons_keywords = [
            "kernenergie", "kerncentrale", "kerncentrales", "traditie", "boeren", "stikstofregels versoepelen",
            "grenzen sluiten", "defensie", "nationale identiteit", "gezin", "brandstof goedkoper",
            "soevereiniteit", "patriottisme", "zwarte piet", "nexit"
        ]

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
            pc_axis = 1.5
        elif cons_score > prog_score:
            pc_axis = -1.5

        lr_label = "Links (Sociaal-Economisch)" if lr_axis < 0 else ("Rechts (Marktgericht)" if lr_axis > 0 else "Centrum / Neutraal")
        pc_label = "Progressief" if pc_axis > 0 else ("Conservatief" if pc_axis < 0 else "Neutraal / Midden")

        return Dimensions(
            statement=statement,
            left_right_orientation=lr_axis,
            prog_cons_orientation=pc_axis,
            lr_label=lr_label,
            pc_label=pc_label,
            economic_explanation=f"Bevat economische indicatoren richting {lr_label}." if lr_axis != 0 else "Neutraal op economisch vlak.",
            cultural_explanation=f"Bevat sociaal-culturele waarden richting {pc_label}." if pc_axis != 0 else "Neutraal op maatschappelijk vlak."
        )

    def evaluate_statement_for_all_parties(self, statement: str) -> StatementEvaluationResponse:
        """Evaluates statement across all registered parties ordered alphabetically."""
        dimensions = self.evaluate_statement_dimensions(statement)
        party_stances: List[PartyStance] = []

        stmt_terms = [w.lower() for w in re.findall(r'\w+', statement) if len(w) > 3]

        # Specific stance indicators
        support_terms = ["voorstander", "investeren", "bouwen", "stimuleren", "uitbreiden", "ja", "wel", "pro", "versnellen", "moet", "noodzakelijk", "verhogen", "invoeren", "prioriteit"]
        against_terms = ["tegenstander", "geen", "stop", "afschaffen", "verbieden", "contra", "gevaar", "tegen", "niet", "onacceptabel", "verlagen", "afwijzen", "beperken"]

        is_nuclear = "kerncentrale" in statement.lower() or "kernenergie" in statement.lower()
        is_eigen_risico = "eigen risico" in statement.lower()
        is_asiel = "asiel" in statement.lower() or "grenzen" in statement.lower() or "instroom" in statement.lower()
        is_stikstof = "stikstof" in statement.lower() or "boeren" in statement.lower()

        # Sort parties: Parliamentary first (by seats desc), then alphabetical
        sorted_parties = sorted(
            PARTIES_CATALOG.values(),
            key=lambda p: (-p["seats"], p["name"].lower())
        )

        for p in sorted_parties:
            pid = p["id"]
            p_name = p["name"]
            p_color = p["color"]

            contexts = self.query_party_chunks(pid, statement, n_results=4)

            # Filter valid contexts
            valid = []
            for c in contexts:
                t_lower = c["text"].lower()
                matches = sum(1 for term in stmt_terms if term in t_lower)
                if matches > 0 or c.get("relevance_score", 1.0) < 0.75:
                    valid.append(c)

            if not valid:
                party_stances.append(PartyStance(
                    party_id=pid,
                    party_name=p_name,
                    party_color=p_color,
                    score=None,
                    score_label="? (Geen standpunt vermeld)",
                    is_unknown=True,
                    explanation=f"Geen directe passages gevonden over deze stelling in het programma van {p_name}.",
                    quotes=[]
                ))
                continue

            full_text = " ".join([c["text"] for c in valid]).lower()
            pos_hits = sum(full_text.count(t) for t in support_terms)
            neg_hits = sum(full_text.count(t) for t in against_terms)

            # High precision rules for signature Dutch political debate topics
            if is_nuclear:
                if any(w in full_text for w in ["inzetten op kernenergie", "nieuwe kerncentrales", "kerncentrales bouwen", "schone kernenergie"]):
                    score = 2.0
                elif any(w in full_text for w in ["geen kerncentrales", "geen nieuwe kernenergie", "kernafval onveilig", "te duur en te laat"]):
                    score = -2.0
                elif pos_hits > neg_hits:
                    score = 1.0
                elif neg_hits > pos_hits:
                    score = -1.0
                else:
                    score = 0.0
            elif is_eigen_risico:
                if any(w in full_text for w in ["eigen risico afschaffen", "eigen risico naar 0", "geen eigen risico"]):
                    score = 2.0
                elif any(w in full_text for w in ["eigen risico verlagen", "stapsgewijs verlagen"]):
                    score = 1.0
                elif any(w in full_text for w in ["eigen risico handhaven", "kost miljarden", "rem op zorguitgaven"]):
                    score = -2.0
                else:
                    score = 0.0
            elif is_asiel:
                if any(w in full_text for w in ["asielstop", "grenzen sluiten", "strengste asielbeleid ooit", "instroom beperken", "beperking asiel"]):
                    score = 2.0 if "beperkt" in statement.lower() or "streng" in statement.lower() else -2.0
                elif any(w in full_text for w in ["vluchtelingen humaan opvangen", "recht op asiel verdedigen", "spreidingswet"]):
                    score = -2.0 if "beperkt" in statement.lower() or "streng" in statement.lower() else 2.0
                else:
                    raw = (pos_hits - neg_hits) * 0.8
                    score = max(-2.0, min(2.0, round(raw, 1)))
            elif is_stikstof:
                if any(w in full_text for w in ["stikstofregels versoepelen", "geen gedwongen krimp", "boeren perspectief"]):
                    score = 2.0 if "versoepeld" in statement.lower() else -2.0
                elif any(w in full_text for w in ["stikstof halveren", "natuurherstel", "halvering van de veestapel"]):
                    score = -2.0 if "versoepeld" in statement.lower() else 2.0
                else:
                    raw = (pos_hits - neg_hits) * 0.8
                    score = max(-2.0, min(2.0, round(raw, 1)))
            else:
                raw = (pos_hits - neg_hits) * 0.8
                score = max(-2.0, min(2.0, round(raw, 1)))

            # Score label
            if score >= 1.5:
                label = "+2 (Sterk Voor)"
            elif score >= 0.5:
                label = "+1 (Gematigd Voor)"
            elif score > -0.5:
                label = "0 (Neutraal / Genuanceerd)"
            elif score > -1.5:
                label = "-1 (Gematigd Tegen)"
            else:
                label = "-2 (Sterk Tegen)"

            quotes_list = []
            for c in valid[:2]:
                meta = c.get("metadata", {})
                quotes_list.append(Quote(
                    page=int(meta.get("page", 1)),
                    filename=meta.get("filename", p["pdfFilename"]),
                    text=c["text"].strip()
                ))

            explanation = f"{p_name} is gekwalificeerd als **{label}** op basis van de geregistreerde standpunten in het verkiezingsprogramma."

            party_stances.append(PartyStance(
                party_id=pid,
                party_name=p_name,
                party_color=p_color,
                score=score,
                score_label=label,
                is_unknown=False,
                explanation=explanation,
                quotes=quotes_list
            ))

        return StatementEvaluationResponse(
            statement=statement,
            dimensions=dimensions,
            party_stances=party_stances
        )

    def get_party_detail(self, party_id: str) -> Optional[PartyDetail]:
        """Returns full party detail with vision and all theme breakdowns."""
        p = PARTIES_CATALOG.get(party_id)
        if not p:
            return None

        pdf_path = os.path.join(self.pdf_dir, p["pdfFilename"])
        pdf_available = os.path.exists(pdf_path)
        page_count = self._get_page_count(party_id, pdf_path) if pdf_available else None

        # Vision query
        vision_chunks = self.query_party_chunks(party_id, f"{p['name']} visie toekomst verkiezingsprogramma speerpunten", n_results=2)
        if vision_chunks:
            vision_summary = " ".join([c["text"][:300].strip() for c in vision_chunks]) + "..."
        else:
            vision_summary = p["shortDescription"]

        # Themes breakdown
        themes_dict: Dict[str, ThemeDetail] = {}
        for t_key, t_info in THEMES_CATALOG.items():
            t_detail = self._get_party_theme_stance(party_id, p["name"], t_key, t_info)
            themes_dict[t_key] = t_detail

        return PartyDetail(
            id=party_id,
            name=p["name"],
            fullName=p["fullName"],
            leader=p["leader"],
            seats=p["seats"],
            inParliament=p["inParliament"],
            orientation=p["orientation"],
            color=p["color"],
            textColor=p["textColor"],
            pdfAvailable=pdf_available,
            coverUrl=f"/api/parties/{party_id}/cover",
            pdfUrl=f"/api/parties/{party_id}/pdf",
            pageCount=page_count,
            compass=p["compass"],
            shortDescription=p["shortDescription"],
            visionSummary=vision_summary,
            themes=themes_dict,
            tkData=self._get_tk_fractie(party_id)
        )


    def _get_party_theme_stance(self, party_id: str, party_name: str, theme_key: str, theme_info: Dict[str, Any]) -> ThemeDetail:
        cache_key = f"{party_id}_{theme_key}"
        if party_id in self._theme_cache and theme_key in self._theme_cache[party_id]:
            return self._theme_cache[party_id][theme_key]

        query = f"{theme_info['title']} " + " ".join(theme_info.get("keywords", []))
        contexts = self.query_party_chunks(party_id, query, n_results=3)

        if not contexts:
            res = ThemeDetail(
                title=theme_info["title"],
                score=0.0,
                label="Geen specifieke gegevens",
                summary=f"Geen passages aangetroffen over {theme_info['title']} in het programma van {party_name}.",
                quotes=[]
            )
        else:
            quotes = []
            for c in contexts[:2]:
                meta = c.get("metadata", {})
                quotes.append(Quote(
                    page=int(meta.get("page", 1)),
                    filename=meta.get("filename", f"{party_name}.pdf"),
                    text=c["text"][:320].strip() + ("..." if len(c["text"]) > 320 else "")
                ))
            summary_snippet = contexts[0]["text"][:280].strip() + "..."
            res = ThemeDetail(
                title=theme_info["title"],
                score=2.0,
                label="Belangrijk speerpunt",
                summary=summary_snippet,
                quotes=quotes
            )

        if party_id not in self._theme_cache:
            self._theme_cache[party_id] = {}
        self._theme_cache[party_id][theme_key] = res
        return res

    def compare_parties(self, party_ids: List[str], theme_keys: Optional[List[str]] = None) -> CompareResponse:
        """Returns side-by-side theme comparison for chosen party IDs."""
        valid_parties = [self.get_party_summary(pid) for pid in party_ids if pid in PARTIES_CATALOG]
        
        target_themes = theme_keys if theme_keys else list(THEMES_CATALOG.keys())
        theme_items: List[ThemeComparisonItem] = []

        for tk in target_themes:
            if tk not in THEMES_CATALOG:
                continue
            t_info = THEMES_CATALOG[tk]
            stances_map: Dict[str, ThemeDetail] = {}

            for p_sum in valid_parties:
                detail = self._get_party_theme_stance(p_sum.id, p_sum.name, tk, t_info)
                stances_map[p_sum.id] = detail

            theme_items.append(ThemeComparisonItem(
                theme_key=tk,
                theme_name=t_info["title"],
                stances=stances_map
            ))

        return CompareResponse(
            parties=valid_parties,
            themes=theme_items
        )

    def get_party_summary(self, party_id: str) -> PartySummary:
        p = PARTIES_CATALOG[party_id]
        pdf_path = os.path.join(self.pdf_dir, p["pdfFilename"])
        pdf_available = os.path.exists(pdf_path)
        return PartySummary(
            id=party_id,
            name=p["name"],
            fullName=p["fullName"],
            leader=p["leader"],
            seats=p["seats"],
            inParliament=p["inParliament"],
            orientation=p["orientation"],
            color=p["color"],
            textColor=p["textColor"],
            pdfAvailable=pdf_available,
            coverUrl=f"/api/parties/{party_id}/cover",
            pdfUrl=f"/api/parties/{party_id}/pdf",
            pageCount=self._get_page_count(party_id, pdf_path) if pdf_available else None,
            compass=p["compass"],
            shortDescription=p["shortDescription"]
        )

    def get_compass_data(self) -> CompassResponse:
        """Returns compass coordinates for all parties."""
        parties_list = []
        for pid, p in PARTIES_CATALOG.items():
            parties_list.append(CompassParty(
                id=pid,
                name=p["name"],
                fullName=p["fullName"],
                color=p["color"],
                textColor=p["textColor"],
                x=float(p["compass"]["x"]),
                y=float(p["compass"]["y"]),
                seats=p["seats"],
                inParliament=p["inParliament"],
                summary=p["shortDescription"]
            ))
        return CompassResponse(parties=parties_list)

    def extract_page_text(self, party_id: str, page_num: int) -> Dict[str, Any]:
        """Extracts text of a single page from the party's PDF."""
        p = PARTIES_CATALOG.get(party_id)
        if not p:
            return {"error": "Party not found", "page": page_num, "text": ""}

        pdf_path = os.path.join(self.pdf_dir, p["pdfFilename"])
        if not os.path.exists(pdf_path):
            return {"error": "PDF not found", "page": page_num, "text": ""}

        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                if page_num < 1 or page_num > total_pages:
                    return {"error": f"Page {page_num} out of range (1-{total_pages})", "totalPages": total_pages, "text": ""}
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
                return {
                    "party_id": party_id,
                    "party_name": p["name"],
                    "page": page_num,
                    "totalPages": total_pages,
                    "text": text
                }
        except Exception as e:
            return {"error": str(e), "page": page_num, "text": ""}
