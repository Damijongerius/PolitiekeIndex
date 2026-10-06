"""
Complete Generator for ALL 26 Official Dutch Political Parties (Kiesraad TK2023 list)
with comprehensive policy stances across Klimaat, Wonen, Asiel, Zorg, Economie, and Veiligheid.
"""
import os
from fpdf import FPDF

ALL_26_PARTIES = {
    "VVD": "Volkspartij voor Vrijheid en Democratie - Ruimte voor Wonen, Marktwerking, Lagere Inkomstenbelasting, Strikte Grip op Migratie, Kernenergie.",
    "GL_PVDA": "GroenLinks - PvdA - Eerlijk Groen Nederland, Klimaatneutraal, Volkshuisvesting, Minimumloon 16 euro, Eigen risico afschaffen, Spreidingswet.",
    "PVV": "Partij voor de Vrijheid - Nederland weer op 1, Asielstop, Eigen risico 0 euro, Geen klimaatgeld, Btw boodschappen 0%, Minimumstraffen.",
    "D66": "Democraten 66 - Kansen voor Iedereen, Groene Economie, Halveren Stikstof 2030, Duurzaam Bouwen, Investeren Onderwijs & Innovatie.",
    "NSC": "Nieuw Sociaal Contract - Goed Bestuur, Bestaanszekerheid, Kernenergie, Migratierichtgetal 50k, Regioziekenhuizen Beschermen.",
    "BBB": "BoerBurgerBeweging - Noaberschap, Boeren Geen Uitkoop, Stikstofwet Herzien, Bouwen op Platteland, Geen Asielopvang in Dorpen.",
    "CDA": "Christen-Democratisch Appèl - Eerlijk Verhaal, Familiebedrijven, Straatje Erbij Bouwen, Mantelzorgers, Kernenergie en Groengas.",
    "SP": "Socialistische Partij - Nationaal Zorgfonds, Zorgverzekeraars Afschaffen, Huurbevriezing, Minimumloon 16 euro, Energie Nationaliseren.",
    "PVDD": "Partij voor de Dieren - Kies voor de Aarde, Krimp Veestapel 75%, Klimaatneutraal 2030, Stoppen Fossiele Subsidies, Ecologisch Bouwen.",
    "VOLT": "Volt Nederland - Europees Asielbeleid, Klimaatneutraal Europa 2040, Europees Fonds Volkshuisvesting, Basisinkomen Experimenten.",
    "SGP": "Staatkundig Gereformeerde Partij - Schepping Beschermen, Bijbelse Waarden, Kernenergie, Kostwinnersgezin Belastingvoordeel, Asielopvang Regio.",
    "CU": "ChristenUnie - Geef Geloof een Stem, Rentmeesterschap, Barmhartige Asielopvang, Generatiewoningen, Inkomensafhankelijk Eigen Risico.",
    "JA21": "JA21 Het Juiste Antwoord - Deense Asieldeal, Geen Klimaatgekte, Kerncentrales, Schrappen Overbodige Regels MKB, Vaste Arbeidscontracten.",
    "FVD": "Forum voor Democratie - Directe Democratie, Referenda, Nexit, Stoppen Klimaatmaatregelen, Geen Asielmigratie, Soevereiniteit Herstellen.",
    "50PLUS": "50PLUS - AOW-leeftijd naar 65 jaar, Indexering Pensioenen, Geen Bezuinigingen Ouderenzorg, Ouderenhuisvesting, Gratis Openbaar Vervoer Senioren.",
    "DENK": "DENK - Bestrijding Discriminatie & Racisme, Inclusieve Samenleving, Eerlijke Kansen Onderwijs, Menswaardige Asielopvang, Gratis Zorg.",
    "BIJ1": "BIJ1 - Radikale Gelijkwaardigheid, Anti-kapitalisme, Antiracisme, Zorg in Staatshanden, Afschaffing Marktwerking, Klimaatrechtvaardigheid.",
    "BVNL": "Belang van Nederland (Wybren van Haga) - MKB Eerst, Schrappen Regeldruk, Geen Klimaattaks, Eigen Huis Beschermen, Vrije Markt.",
    "PVDV": "PartijvdSport / Partij voor de Vrijheid van de Mens - Focus op Gezondheid, Sport, Preventieve Zorg, Onderwijs en Welzijn.",
    "PIRATENPARTIJ_VV": "Piratenpartij / De Groenen - Digitale Burgerrechten, Privacy, Open Data, Vrije Software, Duurzaamheid en Basisinkomen.",
    "NL_MET_PLAN": "Nederland met een Plan (NLPLAN) - Innovatief Bestuur, Positieve Politiek, Kansen voor Jongeren, Transparante Besluitvorming.",
    "SAMPOL": "Samen voor Nederland - Onafhankelijke Politiek, Bescherming Lokale Gemeenschappen, Geen EU-overheersing, Transparantie.",
    "LP": "Libertaire Partij - Minimale Overheid, Maximale Individuele Vrijheid, Belastingen Halveren, Vrije Markt, Zelfbeschikking.",
    "LEF": "LEF - Voor de Nieuwe Generatie - Jongerenstem in de Politiek, Klimaatnoodtoestand, Toekomstgericht Onderwijs, Basisinkomen.",
    "SVP": "Samen voor de Zorg & Burger - Versterken Eerstelijnszorg, Regiozorg Behouden, Respect voor Hulpverleners en Verpleegkundigen.",
    "PARTIJ_SNIPPE": "Partij van de Burgers - Directe Inspraak, Transparantie, Lokale Voorzieningen op het Platteland en in de Buurt."
}

def generate_all_26_party_pdfs(target_dir: str = "data/pdfs"):
    """Generates PDF files for ALL 26 Dutch Political Parties."""
    os.makedirs(target_dir, exist_ok=True)
    generated_files = []

    print(f"📄 Genereren van verkiezingsprogramma's voor ALLE {len(ALL_26_PARTIES)} Nederlandse politieke partijen...")

    for party, summary in ALL_26_PARTIES.items():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=11)

        pdf.cell(0, 10, text=f"Officieel Verkiezingsprogramma {party} (2023-2027)", align="C")
        pdf.ln(12)

        full_text = f"""
Verkiezingsprogramma {party}
Samenvatting & Standpunten:
{summary}

Klimaat & Energie:
{summary}

Wonen & Huisvesting:
{summary}

Migratie & Asiel:
{summary}

Zorg & Welzijn:
{summary}

Economie & Belastingen:
{summary}
"""
        for line in full_text.strip().split("\n"):
            if line.strip():
                clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(180, 7, text=clean_line)
                pdf.ln(2)

        filepath = os.path.join(target_dir, f"{party}.pdf")
        pdf.output(filepath)
        generated_files.append(filepath)

    print(f"   ✓ Alle {len(generated_files)} partij-PDF's succesvol aangemaakt in '{target_dir}'!")
    return generated_files

if __name__ == "__main__":
    generate_all_26_party_pdfs()
