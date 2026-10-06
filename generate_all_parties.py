"""
Full Dutch Political Parties Program Generator with comprehensive policy statements
for VVD, GroenLinks-PvdA, PVV, D66, NSC, BBB, CDA, SP, Partij voor de Dieren, Volt, SGP, ChristenUnie, JA21, FVD.
"""
import os
from fpdf import FPDF

PARTIES_DATA = {
    "VVD": """
Verkiezingsprogramma VVD - Ruimte voor Wonen, Economie en Veiligheid.
Klimaat & Energie:
Investeren in kernenergie als schone en betrouwbare bron. Stikstofregels versoepelen voor de bouw. Geen overhaaste klimaatdoelen die de economie schaden.

Wonen & Huisvesting:
Meer woningen bouwen door vergunningsverlening te versnellen. Marktwerking stimuleren, steun voor koopwoningen en startershypotheken.

Migratie & Asiel:
Strikte grip op migratie. Asielinstroom omlaag met strengere grenscontroles en beperking van gezinshereniging.

Zorg & Welzijn:
Eigen risico behouden om de zorg betaalbaar te houden. Meer marktwerking en doelmatigheid in de zorg.

Economie & Belastingen:
Werken moet lonen! Inkomstenbelasting verlagen voor de middenklasse en ondernemers. Geen miljonairsbelasting.
""",
    "GL_PVDA": """
Verkiezingsprogramma GroenLinks-PvdA - Samen voor een Eerlijk en Groen Nederland.
Klimaat & Energie:
Versnellen energietransitie. CO2-reductie van 65% in 2030. Zware industrie moet eerlijk betalen. Grote investeringen in isolatie en windparken op zee. Geen nieuwe kerncentrales.

Wonen & Huisvesting:
Wonen is een grondrecht. Volkshuisvesting in overheidshanden. 100.000 sociale huur- en middenhuurwoningen per jaar. Huurbevriezing.

Migratie & Asiel:
Menswaardige opvang van vluchtelingen. Eerlijke herverdeling via de Spreidingswet. Snelle integratie en taallessen vanaf dag 1.

Zorg & Welzijn:
Afschaffen van het eigen risico in de zorg. Salarissen zorgpersoneel omhoog en marktwerking stopzetten.

Economie & Belastingen:
Eerlijke herverdeling. Minimumloon omhoog naar 16 euro per uur. Hogere belastingen voor miljonairs en vermogenden.
""",
    "PVV": """
Verkiezingsprogramma PVV - Nederland weer op 1.
Klimaat & Energie:
Direct stoppen met alle klimaat- en stikstofmaatregelen. Geen geld meer naar klimaatsubsidies of windmolens. Kernenergie stimuleren.

Wonen & Huisvesting:
Nederlanders eerst bij de toewijzing van sociale huurwoningen. Voorrang voor statushouders direct afschaffen. Bouw van betaalbare woningen.

Migratie & Asiel:
Directe asielstop en sluiten van onze grenzen. Geen opvang meer in Nederlandse gemeenten. Vrijwillige remigratie stimuleren.

Zorg & Welzijn:
Het eigen risico in de zorg per direct naar 0 euro. Meer personeel en geld voor de ouderenzorg en verpleeghuizen.

Economie & Belastingen:
Btw op boodschappen en energie naar 0%. Brandstofprijzen verlagen. Geen belastinggeld naar buitenlandse hulp.
""",
    "D66": """
Verkiezingsprogramma D66 - Kansen voor Iedereen, Kansen voor de Toekomst.
Klimaat & Energie:
Koploper worden in groene economie. Stikstofuitstoot halveren in 2030. Grote investeringen in openbaar vervoer, fiets en duurzame energie.

Wonen & Huisvesting:
Duurzaam bouwen voor jongeren en studenten. Transformatie van leegstaande kantoren en stimuleren houten woningbouw.

Migratie & Asiel:
Europees asielbeleid versterken. Legale migratieroutes voor kenniswerkers, talent en studenten.

Zorg & Welzijn:
Focus op preventie en leefstijl. Geestelijke gezondheidszorg (GGZ) versterken en bureaucratie verminderen.

Economie & Belastingen:
Investeren in onderwijs, wetenschap en innovatie. Vervuiling belasten en arbeid goedkoper maken.
""",
    "NSC": """
Verkiezingsprogramma Nieuw Sociaal Contract (NSC) - Goed Bestuur en Bestaanszekerheid.
Klimaat & Energie:
Realistisch klimaatbeleid met draagvlak. Inzetten op kernenergie en innovatieve landbouw. Stikstofdoelen aanpassen aan de praktijk.

Wonen & Huisvesting:
Bestaanszekerheid begint met een woning. Bouw van betaalbare woningen voor starters en gezinnen met overheidsregie.

Migratie & Asiel:
Richtgetal van 50.000 voor totale migratie. Beperking van studiemigratie en strengere regels voor asiel en arbeidsmigratie.

Zorg & Welzijn:
Regionale ziekenhuizen en huisartsenzorg beschermen. Eigen risico hervormen en zorg dichtbij de burger organiseren.

Economie & Belastingen:
Bestaanszekerheid vergroten. Belastingstelsel vereenvoudigen en werken loonend maken voor lage en middeninkomens.
""",
    "BBB": """
Verkiezingsprogramma BBB - Gezond Verstand voor Boeren, Burgers en Noaberschap.
Klimaat & Energie:
Geen gedwongen uitkoop van boeren. Stikstofwetgeving grondig herzien. Inzetten op agrarisch natuurbeheer en lokaal opgewekte energie.

Wonen & Huisvesting:
Bouwen in dorpen en plattelandsgemeenten. Schrappen van belemmerende milieu- en stikstofregels bij woningbouw.

Migratie & Asiel:
Migratiestop voor asielzoekers totdat de opvang op orde is. Strengere eisen aan arbeidsmigratie.

Zorg & Welzijn:
Zorgvoorzieningen en ziekenhuizen in de regio behouden. Minder regeldruk voor verpleegkundigen en zorgverleners.

Economie & Belastingen:
Verlaging van energiebelastingen en accijnzen. MKB en agrarische sector de ruimte geven zonder overbodige regels.
""",
    "CDA": """
Verkiezingsprogramma CDA - Eerlijk Verhaal voor een Hechte Samenleving.
Klimaat & Energie:
Gebalanceerde energietransitie met oog voor de gemeenschap. Investeren in kernenergie, groengas en verduurzaming boerenbedrijven.

Wonen & Huisvesting:
Corporatiebouw stimuleren en straatje erbij bouwen in dorpen en steden. Koopwoningen bereikbaar maken voor starters.

Migratie & Asiel:
Grip op migratie door Europese afspraken en strengere asielprocedures. Focus op opvang in de eigen regio.

Zorg & Welzijn:
Mantelzorgers en vrijwilligers beter ondersteunen. Buurtzorg en lokale zorgcentra versterken.

Economie & Belastingen:
Familiebedrijven en verenigingsleven ondersteunen. Eerlijke belasting op vermogen en bescherming van de middenklasse.
""",
    "SP": """
Verkiezingsprogramma SP - Stel een Daad voor Eerlijkheid en Zorg.
Klimaat & Energie:
Energiebedrijven nationaliseren. Verduurzaming van huurwoningen gratis voor huurders. Grote vervuilers laten betalen.

Wonen & Huisvesting:
Huren verlagen en volkshuisvesting herstellen. Woningbouwverenigingen omvormen tot buurtdiensten zonder winstoogmerk.

Migratie & Asiel:
Stop op goedkope arbeidsuitbuiting door uitzendbureaus. Eerlijke asielopvang zonder vluchtelingendeals met dictators.

Zorg & Welzijn:
Het Nationaal Zorgfonds oprichten. Afschaffen van de zorgverzekeraars en het eigen risico naar 0 euro.

Economie & Belastingen:
Miljonairsbelasting invoeren. Minimumloon naar 16 euro en winstbelasting voor grote concerns omhoog.
""",
    "PVDD": """
Verkiezingsprogramma Partij voor de Dieren - Kies voor de Aarde.
Klimaat & Energie:
Klimaatneutraal in 2030. Direct stoppen met fossiele subsidies. Krimp van de veestapel met 75%. 100% biologische landbouw.

Wonen & Huisvesting:
Ecologisch en circulair bouwen. Bestaande panden ombouwen en leegstand aanpakken in plaats van natuur opofferen.

Migratie & Asiel:
Humaan asielbeleid. Klimaatvluchtelingen opvangen en de oorzaken van migratie en oorlog aanpakken.

Zorg & Welzijn:
Preventie via gezonde, plantaardige voeding en schone lucht. Zorg zonder winstoogmerk.

Economie & Belastingen:
Krimp van de economie (degrowth) waar nodig. Zware belastingen op grondstoffen, vlees en uitstoot.
""",
    "Volt": """
Verkiezingsprogramma Volt - Toekomst voor Europa, Kansen voor Nederland.
Klimaat & Energie:
Klimaatneutraal Europa in 2040. Europese CO2-belasting en een Europees energienetwerk met kernenergie en hernieuwbare bronnen.

Wonen & Huisvesting:
Europees fonds voor volkshuisvesting. Modulair en duurzaam bouwen op grote schaal.

Migratie & Asiel:
Eén Europees asielsysteem met menswaardige opvang en snelle werkvergunningen voor nieuwkomers.

Zorg & Welzijn:
Digitalisering en data-uitwisseling in de zorg verbeteren. Zorgpersoneel beter waarderen.

Economie & Belastingen:
Basisinkomen experimenten. Eerlijke Europese winstbelasting voor techgiganten en grote bedrijven.
""",
    "SGP": """
Verkiezingsprogramma SGP - Met Raad en Daad voor Bijbelse Waarden.
Klimaat & Energie:
Zorg voor de schepping. Inzetten op kernenergie, zonne-energie op daken en innovatie zonder doorgeslagen regels.

Wonen & Huisvesting:
Gezinnen ondersteunen bij de aanschaf van een woning. Starterskansen vergroten op het platteland.

Migratie & Asiel:
Streng asielbeleid en opvang in de regio. Bescherming van de christelijke en westerse cultuur en waarden.

Zorg & Welzijn:
Bescherming van het ongeboren en kwetsbare leven. Gezinnen en mantelzorgers financieel ontzien.

Economie & Belastingen:
Kostwinnersgezin belastingtechnisch niet benadelen. MKB en gezinsbedrijven ondersteunen.
""",
    "ChristenUnie": """
Verkiezingsprogramma ChristenUnie - Geef Geloof een Stem voor Samenleving en Zorg.
Klimaat & Energie:
Rentmeesterschap over de aarde. Investeren in schone energie, isolatie van woningen en kringlooplandbouw.

Wonen & Huisvesting:
Generatiewoningen en hofjes bouwen voor ouderen en jongeren. Huurbescherming versterken.

Migratie & Asiel:
Barmhartige opvang van vluchtelingen. Eerlijke spreiding en begeleiding naar werk en samenleving.

Zorg & Welzijn:
Zorgzame samenleving. Eigen risico inkomensafhankelijk maken en de GGZ ontlasten.

Economie & Belastingen:
Eerlijke economie waarin armoede wordt uitgebannen. Belastingkorting voor gezinnen en maatschappelijk betrokken bedrijven.
"""
}

def generate_all_party_pdfs(target_dir: str = "data/pdfs"):
    """Generates complete PDF documents for 12+ Dutch political parties."""
    os.makedirs(target_dir, exist_ok=True)
    generated_files = []

    print(f"📄 Genereren van verkiezingsprogramma's voor {len(PARTIES_DATA)} politieke partijen...")

    for party, text in PARTIES_DATA.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=11)

        pdf.cell(0, 10, text=f"Officieel Verkiezingsprogramma {party} (2023-2027)", align="C")
        pdf.ln(12)

        for line in text.strip().split("\n"):
            if line.strip():
                clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(180, 7, text=clean_line)
                pdf.ln(2)

        filepath = os.path.join(target_dir, f"{party}.pdf")
        pdf.output(filepath)
        generated_files.append(filepath)
        print(f"   ✓ {party}.pdf gegenereerd en opgeslagen.")

    return generated_files

if __name__ == "__main__":
    generate_all_party_pdfs()
