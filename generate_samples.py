"""
Sample Dutch Political Parties Dataset Generator for demo & testing purposes.
"""
import os
from fpdf import FPDF

SAMPLES = {
    "VVD": """
Verkiezingsprogramma VVD - Ruimte voor Wonen, Economie en Veiligheid.
Wonen & Huisvesting:
Wij willen meer woningen bouwen door snellere vergunningsverlening en stikstofregels te versoepelen. Marktwerking en bouwers moeten meer ruimte krijgen. Startershypotheken en steun voor koophuizen staan centraal.

Economie & Belastingen:
Werken moet lonen! Wij verlagen de inkomstenbelasting voor de middenklasse en ondernemers. Geen onnodige regeldruk voor het MKB. Werken moet altijd meer opleveren dan een uitkering.

Migratie & Asiel:
Strikte grip op migratie. Asielinstroom moet omlaag door strengere grenscontroles en beperking van gezinshereniging. Arbeidsmigratie alleen waar onze economie het echt nodig heeft.

Klimaat & Energie:
Investeren in kernenergie als schone en betrouwbare bron. Geen overhaaste klimaatdoelen die onze industrie kapotmaken. Realistische energietransitie.

Veiligheid & Justitie:
Zwaardere straffen voor georganiseerde misdaad. Meer agenten op straat en uitbreiding van politiebevoegdheden. Defensie-uitgaven naar minimaal 2% van het BBP.
""",
    "GL_PVDA": """
Verkiezingsprogramma GroenLinks-PvdA - Samen voor een Eerlijk en Groen Nederland.
Klimaat & Energie:
Versnellen van de energietransitie. CO2-reductie van 65% in 2030. Zware industrie moet eerlijk betalen voor uitstoot. Grote investeringen in isolatie van huizen, zonne-energie en windparken op zee. Geen nieuwe kerncentrales.

Wonen & Huisvesting:
Wonen is een grondrecht. Volkshuisvesting terug in handen van de overheid. Bouwen van 100.000 betaalbare sociale huurwoningen en middenhuur per jaar. Huurbevriezing en aanpak van huisjesmelkers.

Economie & Belastingen:
Eerlijke verdeling van welvaart. Het minimumloon omhoog naar 16 euro per uur. Hogere belastingen voor miljonairs, vermogenden en grote korporaties om de zorg en het onderwijs te versterken.

Migratie & Asiel:
Menswaardige opvang van vluchtelingen. Eerlijke verdeling over gemeenten via de Spreidingswet. Geen vreemdelingenhaat, maar snellere integratie en taallessen vanaf dag 1.

Zorg & Welzijn:
Afschaffen van het eigen risico in de zorg. Zorgpersoneel verdient betere salarissen en minder bureaucratie. Marktwerking in de zorg stopzetten.
""",
    "PVV": """
Verkiezingsprogramma PVV - Nederland weer op 1.
Migratie & Asiel:
Directe asielstop en sluiten van onze grenzen voor gelukszoekers. Geen opvang meer van asielzoekers in Nederlandse gemeenten. Vrijwillige remigratie stimuleren.

Wonen & Huisvesting:
Nederlanders eerst bij de toewijzing van sociale huurwoningen. Direct stoppen met de voorrang voor statushouders. Bouw van betaalbare woningen zonder klimaat- of stikstofrestricties.

Zorg & Welzijn:
Het eigen risico in de zorg per direct naar 0 euro. Meer personeel voor de ouderenzorg en verpleeghuizen. Ziekenhuizen in de regio moeten openblijven.

Economie & Belastingen:
Btw op boodschappen en energie naar 0%. Verlagen van de brandstofprijzen. Geen belastinggeld meer naar buitenlandse hulp of klimaatsubsidies.

Veiligheid & Justitie:
Maximale straffen voor criminelen. Minimumstraffen invoeren en geen taakstraffen meer bij geweld tegen hulpverleners. Extra geld voor defensie en politie.
""",
    "D66": """
Verkiezingsprogramma D66 - Kansen voor Iedereen, Kansen voor de Toekomst.
Klimaat & Energie:
Koploper worden in de groene economie. Stikstofuitstoot halveren in 2030 door natuurherstel en verduurzaming van de landbouw. Grote investeringen in openbaar vervoer, fietsinfrastructuur en innovatieve energienetwerken.

Wonen & Huisvesting:
Duurzaam bouwen voor jongeren en studenten. Transformatie van leegstaande kantoren naar woningen. Schrappen van belemmerende regelgeving voor houten woningbouw.

Economie & Belastingen:
Investeren in onderwijs, wetenschap en innovatie. Groene belastinghervorming: vervuiling belasten en arbeid goedkoper maken. Vrijhandel en Europese samenwerking stimuleren.

Migratie & Asiel:
Europees asielbeleid versterken. Eerlijke herverdeling binnen de EU en legale migratieroutes voor talentvolle kenniswerkers en studenten.

Veiligheid & Justitie:
Cybercrime en ondermijning keihard aanpakken. Rechtsstaat beschermen, transparantie in het bestuur en bescherming van burgerrechten online.
"""
}

def generate_sample_pdfs():
    """Generates simple PDFs for demo political parties."""
    os.makedirs("samples", exist_ok=True)
    
    for party, text in SAMPLES.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=11)
        
        pdf.cell(0, 10, text=f"Verkiezingsprogramma {party}", align="C")
        pdf.ln(12)
        
        for line in text.strip().split("\n"):
            if line.strip():
                clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(180, 7, text=clean_line)
                pdf.ln(2)
        
        filepath = os.path.join("samples", f"{party}.pdf")
        pdf.output(filepath)
        print(f"Sample PDF created: {filepath}")

if __name__ == "__main__":
    generate_sample_pdfs()
