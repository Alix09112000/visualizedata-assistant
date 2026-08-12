import os
import io
import pandas as pd
import streamlit as st
import plotly.express as px
from openai import OpenAI

st.set_page_config(
    page_title="VisualizeData Assistant",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 3rem;}
[data-testid="stMetricValue"] {font-size: 1.6rem;}
.hero {
    padding: 1.4rem 1.6rem;
    border: 1px solid rgba(128,128,128,.25);
    border-radius: 18px;
    margin-bottom: 1.2rem;
}
.small {opacity: .75;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>VisualizeData Assistant</h1>
  <p class="small">Transformez vos données en analyses, visualisations et décisions intelligentes.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("VisualizeData")
    st.caption("AI-powered Data Analytics")
    st.divider()
    st.write("1. Importez un fichier")
    st.write("2. Explorez les indicateurs")
    st.write("3. Visualisez les données")
    st.write("4. Interrogez vos données avec l'IA")

uploaded_file = st.file_uploader(
    "Importer un fichier CSV ou Excel",
    type=["csv", "xlsx", "xls"]
)

def load_data(file):
    name = file.name.lower()
    if name.endswith(".csv"):
        raw = file.getvalue()
        # Try common encodings/separators.
        for encoding in ("utf-8", "latin-1"):
            try:
                return pd.read_csv(io.BytesIO(raw), encoding=encoding, sep=None, engine="python")
            except Exception:
                pass
        raise ValueError("Impossible de lire ce fichier CSV.")
    return pd.read_excel(file)

def build_dataset_summary(df):
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(exclude="number")

    parts = [
        f"Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes.",
        "Colonnes: " + ", ".join(map(str, df.columns)),
        "Types:\n" + df.dtypes.astype(str).to_string(),
        "Valeurs manquantes:\n" + df.isna().sum().to_string(),
    ]

    if not numeric.empty:
        parts.append("Statistiques numériques:\n" + numeric.describe().round(3).to_string())

    if not categorical.empty:
        cat_summary = []
        for col in categorical.columns[:10]:
            vals = df[col].astype(str).value_counts(dropna=False).head(8)
            cat_summary.append(f"{col}:\n{vals.to_string()}")
        parts.append("Principales modalités:\n" + "\n\n".join(cat_summary))

    # Small sample only; avoids sending the whole dataset.
    parts.append("Échantillon:\n" + df.head(12).to_csv(index=False))
    return "\n\n".join(parts)

if uploaded_file is None:
    st.info("Commencez par importer un fichier CSV ou Excel.")
    st.markdown("### Fonctionnalités de cette version")
    st.write("• Audit rapide des données")
    st.write("• Statistiques descriptives")
    st.write("• Analyse des valeurs manquantes et doublons")
    st.write("• Visualisations interactives")
    st.write("• Questions en langage naturel avec OpenAI")
else:
    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        st.stop()

    if df.empty:
        st.warning("Le fichier ne contient aucune donnée.")
        st.stop()

    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lignes", f"{df.shape[0]:,}".replace(",", " "))
    c2.metric("Colonnes", df.shape[1])
    c3.metric("Valeurs manquantes", missing)
    c4.metric("Doublons", duplicates)

    tabs = st.tabs(["Aperçu", "Qualité", "Statistiques", "Visualisations", "Assistant IA"])

    with tabs[0]:
        st.subheader("Aperçu du jeu de données")
        st.dataframe(df.head(100), use_container_width=True)
        st.caption(f"Affichage des 100 premières lignes maximum.")

        st.subheader("Types de variables")
        types_df = pd.DataFrame({
            "Variable": df.columns.astype(str),
            "Type": df.dtypes.astype(str).values,
            "Valeurs uniques": [df[c].nunique(dropna=True) for c in df.columns]
        })
        st.dataframe(types_df, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Qualité des données")
        quality = pd.DataFrame({
            "Variable": df.columns.astype(str),
            "Valeurs manquantes": [int(df[c].isna().sum()) for c in df.columns],
            "% manquant": [round(df[c].isna().mean() * 100, 2) for c in df.columns],
            "Valeurs uniques": [int(df[c].nunique(dropna=True)) for c in df.columns]
        })
        st.dataframe(quality, use_container_width=True, hide_index=True)
        st.write(f"**Doublons détectés :** {duplicates}")

    with tabs[2]:
        st.subheader("Statistiques descriptives")
        numeric = df.select_dtypes(include="number")
        if numeric.empty:
            st.info("Aucune variable numérique détectée.")
        else:
            st.dataframe(numeric.describe().T, use_container_width=True)

    with tabs[3]:
        st.subheader("Exploration visuelle")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()

        if numeric_cols:
            chart_type = st.selectbox("Type de graphique", ["Histogramme", "Nuage de points", "Boîte à moustaches"])
            if chart_type == "Histogramme":
                x = st.selectbox("Variable", numeric_cols)
                fig = px.histogram(df, x=x)
                st.plotly_chart(fig, use_container_width=True)
            elif chart_type == "Nuage de points":
                if len(numeric_cols) < 2:
                    st.info("Il faut au moins deux variables numériques.")
                else:
                    x = st.selectbox("Axe X", numeric_cols, key="scatter_x")
                    y = st.selectbox("Axe Y", numeric_cols, index=1, key="scatter_y")
                    color_options = ["Aucune"] + all_cols
                    color = st.selectbox("Couleur", color_options)
                    fig = px.scatter(df, x=x, y=y, color=None if color == "Aucune" else color)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                y = st.selectbox("Variable numérique", numeric_cols, key="box_y")
                category_options = ["Aucune"] + [c for c in all_cols if c != y]
                x = st.selectbox("Catégorie", category_options)
                fig = px.box(df, x=None if x == "Aucune" else x, y=y)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune variable numérique détectée pour ces graphiques.")

    with tabs[4]:
        st.subheader("Interroger les données")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            st.warning("Ajoutez OPENAI_API_KEY dans les variables d'environnement de Render pour activer l'assistant IA.")
        else:
            question = st.text_area(
                "Posez une question sur vos données",
                placeholder="Ex. Quelles sont les tendances principales et les anomalies à surveiller ?"
            )
            if st.button("Analyser avec l'IA", type="primary"):
                if not question.strip():
                    st.warning("Saisissez d'abord une question.")
                else:
                    with st.spinner("Analyse en cours..."):
                        try:
                            client = OpenAI(api_key=api_key)
                            summary = build_dataset_summary(df)
                            response = client.responses.create(
                                model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                                instructions=(
                                    "Tu es VisualizeData Assistant, un analyste de données professionnel. "
                                    "Réponds en français, de manière claire et structurée. "
                                    "Base tes conclusions uniquement sur le résumé statistique et l'échantillon fournis. "
                                    "Ne prétends jamais avoir calculé une information absente. "
                                    "Signale les limites de l'analyse lorsque nécessaire."
                                ),
                                input=f"QUESTION:\n{question}\n\nDONNÉES RÉSUMÉES:\n{summary}"
                            )
                            st.markdown(response.output_text)
                        except Exception as e:
                            st.error(f"Impossible d'obtenir l'analyse IA : {e}")

    st.divider()
    st.caption("VisualizeData Assistant • MVP")
