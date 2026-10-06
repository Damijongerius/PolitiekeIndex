"""
Clean & Simple Streamlit Web App with Button Navigation and A-Z Vertical Party Layout.
No filters, no messy bar charts. Clean vertical list ordered A-Z with score badges and exact quotes.
"""
import os
import streamlit as st
import pandas as pd

from pdf_parser import PDFProcessor
from database import VectorStore
from statement_evaluator import StatementEvaluator
from cover_extractor import render_pdf_cover
from analyzer import DEFAULT_THEMES

# Page Configuration
st.set_page_config(
    page_title="Nederlandse Politiek Analytics",
    page_icon="🇳🇱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Clean Buttons and Vertical Cards
st.markdown("""
<style>
    /* Custom Sidebar Button Styling */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 15px;
        margin-bottom: 5px;
    }
    .party-row-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .badge-score {
        font-size: 0.95rem;
        font-weight: 700;
        padding: 6px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-plus2 { background-color: #d1e7dd; color: #0f5132; }
    .badge-plus1 { background-color: #e2f0d9; color: #2b580c; }
    .badge-zero { background-color: #fff3cd; color: #664d03; }
    .badge-min1 { background-color: #f8d7da; color: #842029; }
    .badge-min2 { background-color: #f5c2c7; color: #842029; }
    .badge-unknown { background-color: #e2e8f0; color: #475569; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_store():
    return VectorStore(db_dir="data/chroma_db")

store = get_store()
evaluator = StatementEvaluator(vector_store=store)
pdf_folder = "data/pdfs"
covers_folder = "data/covers"

# Initialize Navigation Session State
if "page" not in st.session_state:
    st.session_state["page"] = "Standpunten"

# --- SIDEBAR BUTTON NAVIGATION ---
st.sidebar.image("https://img.icons8.com/color/96/000000/netherlands.png", width=56)
st.sidebar.markdown("### **Menu**")

if st.sidebar.button("🎯  Standpunten Evaluator", key="btn_standpunten"):
    st.session_state["page"] = "Standpunten"
    st.rerun()

if st.sidebar.button("🏛️  Alle Partijen (A-Z)", key="btn_partijen"):
    st.session_state["page"] = "Partijen"
    st.rerun()

all_parties = sorted(store.get_all_parties())

# ==========================================
# PAGE 1: STANDPUNTEN (A-Z VERTICAL LIST)
# ==========================================
if st.session_state["page"] == "Standpunten":
    st.markdown('<h2>🎯 Standpunten Evaluator (A - Z)</h2>', unsafe_allow_html=True)
    st.write("Typ hieronder een stelling in. De AI doorzoekt alle verkiezingsprogramma's van **A tot Z** en toont per partij onder elkaar het standpunt, de score (-2 tot +2) en de exacte tekst uit de PDF.")

    PRESET_STATEMENTS = [
        "--- Kies eventueel een voorbeeld stelling ---",
        "Er moeten per direct meer kerncentrales gebouwd worden in Nederland.",
        "Het eigen risico in de zorg moet volledig afgeschaft worden.",
        "De asielinstroom moet sterk beperkt worden met strengere grenscontroles.",
        "Het minimumloon en de uitkeringen moeten substantieel verhoogd worden.",
        "De stikstofregels voor boeren en de bouw moeten versoepeld worden.",
        "De belastingen voor de hoogste inkomens en vermogens moeten omhoog."
    ]

    selected_preset = st.selectbox("💡 Voorbeeld stellingen:", PRESET_STATEMENTS)
    default_input = "" if selected_preset.startswith("---") else selected_preset

    user_statement = st.text_input(
        "✏️ Typ je stelling of statement:",
        value=default_input,
        placeholder="Bijv: 'Openbaar vervoer moet gratis worden voor studenten en ouderen.'"
    )

    if user_statement:
        st.markdown("---")
        dims = evaluator.evaluate_statement_dimensions(user_statement)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Economisch:** {dims['lr_label']}")
        with col2:
            st.info(f"**Maatschappelijk:** {dims['pc_label']}")

        st.subheader(f"📋 Alle {len(all_parties)} Partijen op een rij (A - Z)")

        # Evaluate ALL parties ordered A-Z
        for party in all_parties:
            res = evaluator.evaluate_party_stance(party, user_statement)
            
            # Badge style determination
            score = res['score']
            if res['is_unknown'] or score is None:
                badge_class = "badge-unknown"
                badge_text = "? (Onbekend / Niet vermeld)"
            elif score >= 1.5:
                badge_class = "badge-plus2"
                badge_text = "+2 (Sterk Voor)"
            elif score >= 0.5:
                badge_class = "badge-plus1"
                badge_text = "+1 (Gematigd Voor)"
            elif score > -0.5:
                badge_class = "badge-zero"
                badge_text = "0 (Neutraal / Balans)"
            elif score > -1.5:
                badge_class = "badge-min1"
                badge_text = "-1 (Gematigd Tegen)"
            else:
                badge_class = "badge-min2"
                badge_text = "-2 (Sterk Tegen)"

            st.markdown(f"""
            <div class="party-row-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h3 style="margin: 0; color: #1e3c72;">🏛️ {party}</h3>
                    <span class="badge-score {badge_class}">{badge_text}</span>
                </div>
                <p style="color: #444; margin-bottom: 10px;">{res['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)

            if res['quotes']:
                with st.expander(f"📖 Bekijk exacte tekst en paginabron uit de {party} PDF"):
                    for q in res['quotes']:
                        st.caption(f"Pagina {q['page']} (`{q['filename']}`):")
                        st.info(f"\"{q['text']}\"")

# ==========================================
# PAGE 2: PARTIJEN (A-Z LIST WITH COVERS)
# ==========================================
else:
    st.markdown('<h2>🏛️ Alle Partijen (A - Z)</h2>', unsafe_allow_html=True)
    st.write("Bekijk alle politieke partijen op alfabetische volgorde met hun **PDF voorpagina**, **algemeen standpunt**, **thema-uitwerkingen** en het **volledige PDF document**.")

    col_nav, col_content = st.columns([1, 3])

    with col_nav:
        st.subheader("Selecteer Partij (A-Z)")
        selected_party = st.radio("Partij:", options=all_parties, label_visibility="collapsed")

    with col_content:
        if selected_party:
            st.markdown(f"<h1>🏛️ {selected_party}</h1>", unsafe_allow_html=True)

            # Find PDF file
            party_pdf = None
            if os.path.exists(pdf_folder):
                for f in os.listdir(pdf_folder):
                    if f.endswith(".pdf") and (selected_party.lower() in f.lower() or f.lower().startswith(selected_party.lower())):
                        party_pdf = f
                        break

            if party_pdf:
                pdf_path = os.path.join(pdf_folder, party_pdf)
                cover_img_path = os.path.join(covers_folder, f"{selected_party}_cover.png")
                has_cover = render_pdf_cover(pdf_path, cover_img_path)

                col_img, col_info = st.columns([1, 2])
                with col_img:
                    st.markdown("**Voorpagina van de PDF:**")
                    if has_cover and os.path.exists(cover_img_path):
                        st.image(cover_img_path, width=220)
                    else:
                        st.info("📄 PDF Voorpagina Preview")

                with col_info:
                    st.markdown(f"**Document:** `{party_pdf}`")
                    st.caption(f"Grootte: {os.path.getsize(pdf_path) // 1024} KB")
                    with open(pdf_path, "rb") as f_pdf:
                        st.download_button(
                            label=f"⬇️ Download {selected_party} PDF",
                            data=f_pdf.read(),
                            file_name=party_pdf,
                            mime="application/pdf"
                        )

            st.markdown("---")

            # Tabs for Party Details
            p_tab1, p_tab2, p_tab3 = st.tabs([
                "🌟 Algemeen Standpunt & Profiel", 
                "📌 Uitelkaargetrokken Thema Standpunten", 
                "📖 Volledig PDF Document"
            ])

            # TAB 1: Algemeen Standpunt
            with p_tab1:
                st.subheader(f"Algemeen Politiek Profiel van {selected_party}")
                gen_contexts = store.query_theme(f"{selected_party} visie toekomst verkiezingsprogramma speerpunten", n_results=3, party_filter=selected_party)
                if gen_contexts:
                    st.info(f"**Kernvisie uit de PDF van {selected_party}:**")
                    for gc in gen_contexts[:2]:
                        st.write(f"> *\"{gc['text'][:400]}...\"*")
                else:
                    st.write(f"Informatie over het algemene standpunt van {selected_party}.")

            # TAB 2: Uitelkaargetrokken Thema Standpunten
            with p_tab2:
                st.subheader("Specifieke Standpunten per Thema")
                for theme_name, theme_info in DEFAULT_THEMES.items():
                    with st.expander(f"🔹 **{theme_name}**"):
                        t_contexts = store.query_theme(theme_name, n_results=2, party_filter=selected_party)
                        if t_contexts:
                            for tc in t_contexts:
                                meta = tc.get("metadata", {})
                                st.caption(f"Pagina {meta.get('page', 1)} uit `{meta.get('filename', '')}`:")
                                st.write(tc['text'])
                        else:
                            st.caption("Geen specifieke thema-passage gevonden in de PDF.")

            # TAB 3: Volledig PDF Document Reader
            with p_tab3:
                st.subheader("Volledig PDF Document Inzien")
                if party_pdf and os.path.exists(os.path.join(pdf_folder, party_pdf)):
                    processor = PDFProcessor()
                    pages = processor.extract_text_from_pdf(os.path.join(pdf_folder, party_pdf))
                    st.caption(f"Totaal {len(pages)} pagina's geëxtraheerd met `pdfplumber`:")

                    selected_page = st.slider("Selecteer pagina:", 1, max(1, len(pages)), 1)
                    if pages:
                        p_data = pages[selected_page - 1]
                        st.markdown(f"### Pagina {p_data['page']}")
                        st.text_area(f"Inhoud Pagina {p_data['page']}", value=p_data['text'], height=350)
