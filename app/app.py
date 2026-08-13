import io
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from openai import OpenAI

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens — design system Modernist
# ─────────────────────────────────────────────────────────────────────────────
NAVY = "#201e1d"
INDIGO = "#ec3013"
INDIGO_DARK = "#dd2b0f"
ORANGE = "#ae1800"
PALE = "#eae9e9"
WHITE = "#f3f2f2"
INK = "#201e1d"
MUTED = "#7d7979"
LINE = "#bab6b6"
RADIUS = "0px"

MARK = (
    '<svg width="26" height="26" viewBox="0 0 52 52" aria-hidden="true" style="flex:none">'
    f'<path d="M2 6 L20 46 L36 14" stroke="{INK}" stroke-width="7" fill="none"></path>'
    f'<path d="M36 14 L50 2" stroke="{INDIGO}" stroke-width="7" fill="none"></path></svg>'
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_PREVIEW_ROWS = 200

st.set_page_config(
    page_title="VisualizeData Assistant",
    page_icon="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 52 52'%3E%3Crect width='52' height='52' fill='%23201e1d'/%3E%3Cpath d='M8 12 L22 42 L34 18' stroke='%23f3f2f2' stroke-width='6' fill='none'/%3E%3Cpath d='M34 18 L44 10' stroke='%23ec3013' stroke-width='6' fill='none'/%3E%3C/svg%3E",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Thème Plotly — indigo en série principale, orange réservé à l'insight
# ─────────────────────────────────────────────────────────────────────────────
pio.templates["visualizedata"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Archivo, system-ui, sans-serif", size=13, color=INK),
        title=dict(font=dict(family="Archivo, system-ui, sans-serif", size=17, color=NAVY)),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        colorway=[INDIGO, NAVY, "#7d7979", "#bab6b6", "#dd2b0f", "#9e3526"],
        margin=dict(l=48, r=24, t=36, b=48),
        xaxis=dict(showgrid=False, linecolor=LINE, linewidth=1, ticks="outside",
                   tickcolor=LINE, zeroline=False),
        yaxis=dict(gridcolor=LINE, linecolor=LINE, linewidth=1, zeroline=False),
        bargap=0.08,
        hoverlabel=dict(bgcolor=NAVY, bordercolor=NAVY,
                        font=dict(color="#FFFFFF", family="Manrope")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)"),
    )
)
pio.templates.default = "visualizedata"

# ─────────────────────────────────────────────────────────────────────────────
# CSS — applique l'identité VisualizeData à l'interface Streamlit
# ─────────────────────────────────────────────────────────────────────────────
st.html(
    f"""<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap" rel="stylesheet"> <style> :root {{ --vd-navy:{NAVY}; --vd-indigo:{INDIGO}; --vd-orange:{ORANGE}; --vd-pale:{PALE}; --vd-ink:{INK}; --vd-muted:{MUTED}; --vd-line:{LINE}; --vd-r:{RADIUS}; }} html, body, .stApp, [class*="css"] {{ font-family:'Archivo', system-ui, sans-serif; background:{WHITE}; color:var(--vd-ink); }} h1,h2,h3,h4,h5,h6 {{ font-family:'Archivo', system-ui, sans-serif !important; font-weight:800 !important; letter-spacing:-.02em; line-height:1.16; color:var(--vd-navy); }} #MainMenu, footer, header [data-testid="stStatusWidget"] {{visibility:hidden}} .block-container {{padding-top:2rem; padding-bottom:4rem; max-width:1500px}} section[data-testid="stSidebar"] {{ background:var(--vd-pale); border-right:1px solid var(--vd-line); }} section[data-testid="stSidebar"] .block-container {{padding-top:1.5rem}} div[data-testid="stMetric"] {{ background:{WHITE}; padding:16px 18px; border:1px solid var(--vd-line); border-radius:var(--vd-r); }} div[data-testid="stMetricLabel"] p {{ font-size:12px !important; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--vd-muted) !important; }} div[data-testid="stMetricValue"] {{ font-family:'Archivo', sans-serif; font-size:32px !important; font-weight:600; color:var(--vd-navy); }} .stTabs [data-baseweb="tab-list"] {{gap:6px; border-bottom:1px solid var(--vd-line)}} .stTabs [data-baseweb="tab"] {{ background:transparent; padding:11px 16px; font-weight:600; color:var(--vd-muted); }} .stTabs [aria-selected="true"] {{ color:var(--vd-indigo) !important; box-shadow:inset 0 -2px 0 0 var(--vd-indigo); }} .stTabs [data-baseweb="tab-highlight"] {{background:transparent}} .stButton button, .stDownloadButton button, .stFormSubmitButton button {{ font-family:'Archivo', sans-serif; font-weight:700; font-size:15px; border-radius:var(--vd-r); border:1px solid var(--vd-line); background:{WHITE}; color:var(--vd-navy); padding:10px 18px; }} .stButton button:hover {{border-color:var(--vd-indigo); color:var(--vd-indigo)}} .stButton button[kind="primary"], .stDownloadButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{ background:var(--vd-indigo); border-color:var(--vd-indigo); color:{WHITE}; }} .stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {{ background:{INDIGO_DARK}; border-color:{INDIGO_DARK}; color:{WHITE}; }} .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div, .stChatInput textarea {{ background:{WHITE} !important; border:1px solid var(--vd-line) !important; border-radius:var(--vd-r) !important; color:var(--vd-ink) !important; font-family:'Archivo', sans-serif; }} .stTextInput input:focus, .stTextArea textarea:focus {{border-color:var(--vd-indigo) !important}} *:focus-visible {{outline:2px solid var(--vd-indigo) !important; outline-offset:2px}} ::selection {{background:rgba(79,70,229,.18)}} .stSlider [data-baseweb="slider"] div[role="slider"] {{background:var(--vd-indigo)}} section[data-testid="stFileUploaderDropzone"] {{ background:{WHITE}; border:1.5px dashed #C3D3F5; border-radius:var(--vd-r); padding:22px; }} div[data-testid="stDataFrame"] {{ border:1px solid var(--vd-line); border-radius:var(--vd-r); overflow:hidden; }} .vd-rule {{height:1px; background:var(--vd-line); border:0; margin:24px 0}} .vd-kicker {{ font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--vd-indigo); margin-bottom:10px; }} .vd-hero {{ background:linear-gradient(180deg,var(--vd-pale) 0%,{WHITE} 100%); border:1px solid var(--vd-line); border-radius:0; padding:30px 32px; margin-bottom:22px; }} .vd-hero h1 {{font-size:34px; margin:0 0 8px}} .vd-hero p {{color:var(--vd-muted); max-width:70ch; margin:0}} .vd-answer {{ background:var(--vd-pale); border:1px solid var(--vd-line); border-left:3px solid var(--vd-indigo); border-radius:var(--vd-r); padding:16px 18px; margin:6px 0 14px; }} .vd-poster {{ background:var(--vd-navy); color:{WHITE}; border-radius:0; padding:30px; }} .vd-poster .q {{ font-family:'Archivo', sans-serif; font-weight:600; font-size:24px; line-height:1.2; margin:0; }} .vd-poster .q em {{font-style:normal; color:var(--vd-orange)}} .vd-poster .row {{ display:flex; justify-content:space-between; padding:12px 0; border-top:1px solid rgba(255,255,255,.16); font-size:14px; }} .vd-feature {{ border:1px solid var(--vd-line); border-radius:var(--vd-r); padding:16px 18px; height:100%; }} .vd-feature b {{font-family:'Archivo', sans-serif; font-weight:600; display:block; margin-bottom:4px; color:var(--vd-navy)}} .vd-feature span {{color:var(--vd-muted); font-size:14px}} .vd-bar-label {{display:flex; justify-content:space-between; font-size:14px; margin-bottom:5px}} .vd-bar {{height:7px; background:var(--vd-pale); border-radius:0; overflow:hidden}} .vd-bar > div {{height:100%; background:var(--vd-indigo)}} .vd-bar.alert > div {{background:var(--vd-orange)}} .vd-tag {{ display:inline-block; font-size:12px; font-weight:700; padding:4px 12px; border-radius:0; background:rgba(79,70,229,.12); color:var(--vd-indigo); }} </style>"""
)


# ─────────────────────────────────────────────────────────────────────────────
# Chargement des données
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(raw: bytes, name: str, sheet: str | None = None) -> pd.DataFrame:
    lower = name.lower()
    if lower.endswith(".csv"):
        last_error: Exception | None = None
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return pd.read_csv(io.BytesIO(raw), encoding=encoding, sep=None, engine="python")
            except Exception as exc:  # séparateur ou encodage incompatible
                last_error = exc
        raise ValueError(f"Impossible de lire ce fichier CSV : {last_error}")
    return pd.read_excel(io.BytesIO(raw), sheet_name=sheet or 0)


@st.cache_data(show_spinner=False)
def excel_sheets(raw: bytes) -> list[str]:
    return pd.ExcelFile(io.BytesIO(raw)).sheet_names


def coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit en datetime les colonnes texte qui ressemblent à des dates."""
    out = df.copy()
    for col in out.select_dtypes(include="object").columns:
        sample = out[col].dropna().astype(str).head(50)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed", dayfirst=False)
        if parsed.notna().mean() > 0.85:
            out[col] = pd.to_datetime(out[col], errors="coerce", format="mixed")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Analyse automatique
# ─────────────────────────────────────────────────────────────────────────────
def quality_table(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Variable": df.columns.astype(str),
            "Type": df.dtypes.astype(str).values,
            "Manquants": [int(df[c].isna().sum()) for c in df.columns],
            "% manquant": [round(df[c].isna().mean() * 100, 2) for c in df.columns],
            "Complétude %": [round(df[c].notna().mean() * 100, 1) for c in df.columns],
            "Uniques": [int(df[c].nunique(dropna=True)) for c in df.columns],
        }
    )


def outlier_counts(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            count = 0
        else:
            count = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        rows.append({"Variable": col, "Valeurs extrêmes": count,
                     "% du total": round(count / max(len(series), 1) * 100, 2)})
    return pd.DataFrame(rows).sort_values("Valeurs extrêmes", ascending=False)


def top_correlations(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    corr = numeric.corr(numeric_only=True).abs()
    stacked = corr.mask(corr.ge(0.999)).stack().sort_values(ascending=False)
    seen, rows = set(), []
    for (a, b), value in stacked.items():
        key = frozenset((a, b))
        if key in seen:
            continue
        seen.add(key)
        rows.append({"Variable A": a, "Variable B": b, "Corrélation |r|": round(float(value), 3)})
        if len(rows) == limit:
            break
    return pd.DataFrame(rows)


def auto_insights(df: pd.DataFrame) -> list[str]:
    notes: list[str] = []
    quality = quality_table(df)
    worst = quality.sort_values("% manquant", ascending=False).iloc[0]
    if worst["% manquant"] > 5:
        notes.append(
            f"**{worst['Variable']}** est incomplète à {worst['% manquant']} % — "
            "les analyses par cette variable resteront partielles."
        )
    duplicates = int(df.duplicated().sum())
    if duplicates:
        mot = "ligne" if duplicates == 1 else "lignes"
        verbe = "a été détectée" if duplicates == 1 else "ont été détectées"
        notes.append(f"{duplicates} {mot} strictement {'identique' if duplicates == 1 else 'identiques'} {verbe}.")
    outliers = outlier_counts(df)
    if not outliers.empty and outliers.iloc[0]["Valeurs extrêmes"] > 0:
        row = outliers.iloc[0]
        notes.append(
            f"**{row['Variable']}** contient {int(row['Valeurs extrêmes'])} valeurs extrêmes "
            f"({row['% du total']} % des observations)."
        )
    correlations = top_correlations(df, limit=1)
    if not correlations.empty:
        row = correlations.iloc[0]
        notes.append(
            f"Corrélation la plus forte : **{row['Variable A']}** et **{row['Variable B']}** "
            f"(|r| = {row['Corrélation |r|']})."
        )
    dates = df.select_dtypes(include="datetime").columns.tolist()
    if dates:
        series = df[dates[0]].dropna()
        if not series.empty:
            notes.append(
                f"Période couverte par **{dates[0]}** : "
                f"{series.min():%d/%m/%Y} → {series.max():%d/%m/%Y}."
            )
    return notes


def build_dataset_summary(df: pd.DataFrame) -> str:
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(exclude=["number", "datetime"])
    parts = [
        f"Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes.",
        "Colonnes: " + ", ".join(map(str, df.columns)),
        "Types:\n" + df.dtypes.astype(str).to_string(),
        "Valeurs manquantes:\n" + df.isna().sum().to_string(),
        f"Lignes dupliquées: {int(df.duplicated().sum())}",
    ]
    if not numeric.empty:
        parts.append("Statistiques numériques:\n" + numeric.describe().round(3).to_string())
        correlations = top_correlations(df)
        if not correlations.empty:
            parts.append("Corrélations principales:\n" + correlations.to_string(index=False))
        outliers = outlier_counts(df)
        if not outliers.empty:
            parts.append("Valeurs extrêmes (IQR):\n" + outliers.head(8).to_string(index=False))
    if not categorical.empty:
        blocks = []
        for col in categorical.columns[:10]:
            counts = df[col].astype(str).value_counts(dropna=False).head(8)
            blocks.append(f"{col}:\n{counts.to_string()}")
        parts.append("Principales modalités:\n" + "\n\n".join(blocks))
    for col in df.select_dtypes(include="datetime").columns[:2]:
        series = df[col].dropna()
        if not series.empty:
            parts.append(f"Plage de {col}: {series.min()} → {series.max()}")
    parts.append("Échantillon:\n" + df.head(12).to_csv(index=False))
    return "\n\n".join(parts)


SYSTEM_PROMPT = (
    "Tu es VisualizeData Assistant, un analyste de données professionnel qui conseille "
    "des dirigeants de PME. Réponds en français, de façon structurée et concise : "
    "constat, chiffre à l'appui, implication opérationnelle. "
    "Base tes conclusions uniquement sur le résumé statistique et l'échantillon fournis. "
    "Ne prétends jamais avoir calculé une information absente et signale les limites "
    "de l'analyse (données manquantes, échantillon partiel) quand elles pèsent sur la réponse. "
    "Termine par une seule recommandation actionnable."
)

SUGGESTIONS = [
    "Quelles sont les tendances principales et les anomalies à surveiller ?",
    "Quelles variables expliquent le mieux les écarts observés ?",
    "Quelles données faudrait-il compléter en priorité ?",
]


# Fournisseurs compatibles OpenAI : une seule bibliothèque, plusieurs services.
PROVIDERS = {
    "OpenAI": {
        "env": "OPENAI_API_KEY",
        "base_url": None,
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "note": "Le plus complet. Payant à l'usage.",
    },
    "Groq": {
        "env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "note": "Palier gratuit généreux, réponses très rapides.",
    },
    "Mistral": {
        "env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1",
        "model": os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        "note": "Hébergement européen, bon français.",
    },
    "Google Gemini": {
        "env": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        "note": "Palier gratuit, bonne tenue sur les tableaux.",
    },
    "OpenRouter": {
        "env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "model": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct"),
        "note": "Un seul compte, de nombreux modèles.",
    },
}


def available_providers() -> dict:
    return {name: cfg for name, cfg in PROVIDERS.items() if os.getenv(cfg["env"])}


def make_client(provider: str):
    cfg = PROVIDERS[provider]
    kwargs = {"api_key": os.getenv(cfg["env"])}
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    return OpenAI(**kwargs)


def local_answer(df: pd.DataFrame, question: str) -> str:
    """Analyse sans IA : rédige une réponse à partir des statistiques calculées."""
    lines = ["**Analyse locale** — calculée sur vos données, sans service externe.", ""]
    for note in auto_insights(df):
        lines.append(f"- {note}")

    numeric = df.select_dtypes(include="number")
    words = question.lower()
    target = next((c for c in df.columns if str(c).lower() in words), None)

    if target is not None and target in numeric.columns:
        series = df[target].dropna()
        lines += [
            "",
            f"**{target}** — moyenne {series.mean():,.2f}, médiane {series.median():,.2f}, "
            f"écart-type {series.std():,.2f}, minimum {series.min():,.2f}, maximum {series.max():,.2f}."
            .replace(",", " "),
        ]
    elif target is not None:
        counts = df[target].astype(str).value_counts().head(5)
        lines += ["", f"**{target}** — cinq modalités les plus fréquentes :"]
        lines += [f"- {k} : {v} occurrences" for k, v in counts.items()]
    elif not numeric.empty:
        top = numeric.mean().sort_values(ascending=False).head(3)
        lines += ["", "Moyennes des principales variables numériques :"]
        lines += [f"- {k} : {v:,.2f}".replace(",", " ") for k, v in top.items()]

    dates = df.select_dtypes(include="datetime").columns.tolist()
    if dates and not numeric.empty:
        col, value = dates[0], numeric.columns[0]
        monthly = (
            df[[col, value]].dropna(subset=[col]).set_index(col)[value]
            .resample("MS").sum()
        )
        if len(monthly) >= 2:
            change = monthly.iloc[-1] - monthly.iloc[-2]
            sense = "en hausse" if change > 0 else "en baisse"
            lines += [
                "",
                f"Sur **{value}**, le dernier mois est {sense} de "
                f"{abs(change):,.0f} par rapport au précédent.".replace(",", " "),
            ]

    lines += [
        "",
        "_Pour une lecture rédigée et des recommandations, activez un fournisseur IA "
        "dans la barre latérale._",
    ]
    return "\n".join(lines)


def ask_assistant(client: OpenAI, model: str, question: str, summary: str, history: list[dict]):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
    messages.append({"role": "user", "content": f"QUESTION:\n{question}\n\nDONNÉES RÉSUMÉES:\n{summary}"})
    return client.chat.completions.create(model=model, messages=messages, temperature=0.2, stream=True)


def markdown_report(df: pd.DataFrame, name: str, insights: list[str], history: list[dict]) -> str:
    lines = [
        f"# VisualizeData — rapport d'analyse",
        f"Fichier : **{name}** · généré le {datetime.now():%d/%m/%Y à %H:%M}",
        "",
        "## Vue d'ensemble",
        f"- Lignes : {df.shape[0]}",
        f"- Colonnes : {df.shape[1]}",
        f"- Valeurs manquantes : {int(df.isna().sum().sum())}",
        f"- Doublons : {int(df.duplicated().sum())}",
        "",
        "## Constats automatiques",
    ]
    lines += [f"- {note}" for note in insights] or ["- Aucun signal notable."]
    lines += ["", "## Qualité des données", quality_table(df).to_markdown(index=False)]
    numeric = df.select_dtypes(include="number")
    if not numeric.empty:
        lines += ["", "## Statistiques descriptives",
                  numeric.describe().T.round(3).to_markdown()]
    if history:
        lines += ["", "## Échanges avec l'assistant"]
        for message in history:
            role = "Question" if message["role"] == "user" else "Assistant"
            lines += [f"**{role} —** {message['content']}", ""]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Barre latérale
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html(
        f'<div style="display:flex;align-items:center;gap:10px;padding:2px 0 6px">'
        f'{MARK}'
        f'<span style="font-family:Archivo,sans-serif;font-weight:800;font-size:18px;letter-spacing:-.035em">'
        f'Visualize<span style="color:{INDIGO}">Data</span></span></div>'
        f'<div style="color:{MUTED};font-size:12px">Transformer les données en décisions</div>'
    )

    st.html('<hr class="vd-rule" style="margin:14px 0">')

    uploaded_file = st.file_uploader(
        "Fichier CSV ou Excel", type=["csv", "xlsx", "xls"], label_visibility="collapsed"
    )

    sheet_name = None
    if uploaded_file is not None and not uploaded_file.name.lower().endswith(".csv"):
        sheets = excel_sheets(uploaded_file.getvalue())
        if len(sheets) > 1:
            sheet_name = st.selectbox("Feuille", sheets)

    st.html('<div class="vd-kicker" style="margin-top:20px">Parcours</div>')
    for index, step in enumerate(
        ["Importer un fichier", "Explorer les indicateurs",
         "Visualiser les données", "Interroger avec l'IA"], start=1
    ):
        st.html(
            f'<div style="display:flex;gap:12px;padding:9px 0;'
            f'border-bottom:1px solid {LINE};font-size:14px">'
            f'<span style="font-weight:700;color:{INDIGO}">{index}</span><span>{step}</span></div>'
        )

    st.html('<div class="vd-kicker" style="margin-top:20px">Moteur d\'analyse</div>')
    providers = available_providers()
    engine_options = ["Analyse locale (sans clé)"] + list(providers)
    engine = st.selectbox("Moteur", engine_options, label_visibility="collapsed")
    if engine in providers:
        st.html(f'<span class="vd-tag">{providers[engine]["model"]}</span>')
        st.caption(providers[engine]["note"])
    else:
        st.caption(
            "Réponses calculées sur place à partir de vos statistiques. "
            "Aucune donnée ne sort de l'application."
        )
        if not providers:
            st.caption(
                "Pour des réponses rédigées, ajoutez une clé dans Render → Environment : "
                "OPENAI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY "
                "ou OPENROUTER_API_KEY."
            )

# ─────────────────────────────────────────────────────────────────────────────
# En-tête
# ─────────────────────────────────────────────────────────────────────────────
st.html(
    """
<div class="vd-hero">
  <div class="vd-kicker">Assistant IA</div>
  <h1>Transformer les données en décisions</h1>
  <p>Importez un fichier CSV ou Excel : audit de qualité, statistiques descriptives,
  visualisations et réponses en langage naturel — sans Python ni SQL.</p>
</div>
"""
)

# ─────────────────────────────────────────────────────────────────────────────
# État d'accueil
# ─────────────────────────────────────────────────────────────────────────────
if uploaded_file is None:
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.html('<div class="vd-kicker" style="margin-top:26px">Pour commencer</div>')
        st.markdown("#### Déposez un fichier dans la barre latérale")
        st.caption("CSV, XLSX ou XLS · séparateur et encodage détectés automatiquement.")
        st.html('<hr class="vd-rule">')
        features = [
            ("Audit rapide", "Manquants, doublons, types, modalités, valeurs extrêmes."),
            ("Statistiques descriptives", "Moyennes, écarts, quantiles par variable."),
            ("Visualisations", "Histogramme, nuage de points, boîte, séries temporelles."),
            ("Questions en langage naturel", "Conversation suivie, sources rappelées."),
        ]
        cols = st.columns(2, gap="large")
        for index, (title, description) in enumerate(features):
            with cols[index % 2]:
                st.html(
                    f'<div class="vd-feature"><b>{title}</b><span>{description}</span></div>'
                )
    with right:
        st.html(
    """
<div class="vd-poster">
  <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;opacity:.75;margin-bottom:14px">Exemple de sortie</div>
  <p class="q">« Le canal revendeur recule de 9 % pendant que <em>le direct progresse.</em> »</p>
  <div style="margin-top:34px">
    <div class="row"><span style="opacity:.85">Fichiers acceptés</span><span style="font-weight:800">CSV · XLSX · XLS</span></div>
    <div class="row"><span style="opacity:.85">Temps moyen d'analyse</span><span style="font-weight:800">&lt; 5 s</span></div>
    <div class="row"><span style="opacity:.85">Installation</span><span style="font-weight:800">Aucune</span></div>
  </div>
</div>
"""
        )
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Lecture du fichier
# ─────────────────────────────────────────────────────────────────────────────
try:
    df = load_data(uploaded_file.getvalue(), uploaded_file.name, sheet_name)
except Exception as exc:
    st.error(f"Erreur de lecture : {exc}")
    st.stop()

if df.empty:
    st.warning("Le fichier ne contient aucune donnée.")
    st.stop()

df = coerce_dates(df)
numeric_cols = df.select_dtypes(include="number").columns.tolist()
date_cols = df.select_dtypes(include="datetime").columns.tolist()
all_cols = df.columns.tolist()
missing_total = int(df.isna().sum().sum())
duplicates_total = int(df.duplicated().sum())
completeness = round(df.notna().mean().mean() * 100, 1)
insights = auto_insights(df)

if st.session_state.get("vd_file") != (uploaded_file.name, sheet_name):
    st.session_state["vd_file"] = (uploaded_file.name, sheet_name)
    st.session_state["vd_history"] = []

file_line, action = st.columns([3, 1])
with file_line:
    st.html(
        f'<div style="padding:14px 0 0"><b style="font-family:Archivo,sans-serif;font-weight:800;color:{NAVY}">{uploaded_file.name}</b>'
        f'<span style="color:{MUTED}"> · {df.shape[0]:,} lignes · {df.shape[1]} colonnes'
        f' · complétude {completeness} %</span></div>'.replace(",", " ")
    )
with action:
    st.download_button(
        "Exporter le rapport",
        data=markdown_report(df, uploaded_file.name, insights,
                             st.session_state.get("vd_history", [])),
        file_name=f"rapport_{uploaded_file.name.rsplit('.', 1)[0]}.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )

m1, m2, m3, m4 = st.columns(4, gap="small")
m1.metric("Lignes", f"{df.shape[0]:,}".replace(",", " "))
m2.metric("Colonnes", df.shape[1])
m3.metric("Valeurs manquantes", f"{missing_total:,}".replace(",", " "))
m4.metric("Doublons", duplicates_total)

if insights:
    st.html('<div class="vd-kicker" style="margin-top:26px">Constats automatiques</div>')
    for note in insights:
        st.markdown(f"- {note}")

tabs = st.tabs(["Aperçu", "Qualité", "Statistiques", "Visualisations", "Assistant IA"])

# ── Aperçu ───────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("#### Aperçu du jeu de données")
    st.dataframe(df.head(MAX_PREVIEW_ROWS), use_container_width=True, height=420)
    st.caption(f"{MAX_PREVIEW_ROWS} premières lignes affichées.")

    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("#### Types de variables")
        st.dataframe(
            quality_table(df)[["Variable", "Type", "Uniques"]],
            use_container_width=True, hide_index=True, height=320,
        )
    with right:
        st.markdown("#### Données exportables")
        st.caption("Le fichier lu, dédoublonné, prêt à être réutilisé.")
        st.download_button(
            "Télécharger le CSV nettoyé",
            data=df.drop_duplicates().to_csv(index=False).encode("utf-8"),
            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_nettoye.csv",
            mime="text/csv",
        )

# ── Qualité ──────────────────────────────────────────────────────────────────
with tabs[1]:
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown("#### Qualité des données")
        st.dataframe(
            quality_table(df).drop(columns=["Complétude %"]),
            use_container_width=True, hide_index=True, height=380,
        )
        st.markdown(f"**Doublons détectés :** {duplicates_total}")
    with right:
        st.markdown("#### Complétude par variable")
        quality = quality_table(df).sort_values("Complétude %")
        for _, row in quality.head(10).iterrows():
            alert = " alert" if row["Complétude %"] < 90 else ""
            st.html(
                f'<div class="vd-bar-label"><span>{row["Variable"]}</span>'
                f'<span style="color:{MUTED}">{row["Complétude %"]} %</span></div>'
                f'<div class="vd-bar{alert}"><div style="width:{row["Complétude %"]}%"></div></div>'
                '<div style="height:12px"></div>'
            )
        outliers = outlier_counts(df)
        if not outliers.empty:
            st.html('<hr class="vd-rule">')
            st.markdown("#### Valeurs extrêmes (méthode IQR)")
            st.dataframe(outliers, use_container_width=True, hide_index=True, height=220)

# ── Statistiques ─────────────────────────────────────────────────────────────
with tabs[2]:
    if not numeric_cols:
        st.info("Aucune variable numérique détectée.")
    else:
        st.markdown("#### Statistiques descriptives")
        st.dataframe(
            df[numeric_cols].describe().T.round(3),
            use_container_width=True, height=340,
        )
        correlations = top_correlations(df)
        if not correlations.empty:
            st.html('<hr class="vd-rule">')
            left, right = st.columns([1, 1.3], gap="large")
            with left:
                st.markdown("#### Corrélations principales")
                st.dataframe(correlations, use_container_width=True, hide_index=True)
            with right:
                st.markdown("#### Matrice de corrélation")
                fig = px.imshow(
                    df[numeric_cols].corr(numeric_only=True).round(2),
                    color_continuous_scale=[WHITE, "#ff9783", INDIGO],
                    aspect="auto", text_auto=True,
                )
                fig.update_layout(coloraxis_showscale=False, height=380)
                st.plotly_chart(fig, use_container_width=True)

# ── Visualisations ───────────────────────────────────────────────────────────
with tabs[3]:
    if not numeric_cols:
        st.info("Aucune variable numérique détectée pour ces graphiques.")
    else:
        options = ["Histogramme", "Nuage de points", "Boîte à moustaches"]
        if date_cols:
            options.append("Série temporelle")
        chart_type = st.radio("Type de graphique", options, horizontal=True,
                              label_visibility="collapsed")
        st.html('<hr class="vd-rule" style="margin:14px 0 20px">')
        controls, chart = st.columns([1, 2.4], gap="large")

        if chart_type == "Histogramme":
            with controls:
                x = st.selectbox("Variable", numeric_cols)
                bins = st.slider("Nombre de classes", 10, 100, 30, step=5)
                split = st.selectbox("Découper par", ["Aucune"] + [c for c in all_cols if c != x])
            with chart:
                fig = px.histogram(df, x=x, nbins=bins,
                                   color=None if split == "Aucune" else split)
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Nuage de points":
            if len(numeric_cols) < 2:
                st.info("Il faut au moins deux variables numériques.")
            else:
                with controls:
                    x = st.selectbox("Axe X", numeric_cols, key="scatter_x")
                    y = st.selectbox("Axe Y", numeric_cols, index=1, key="scatter_y")
                    color = st.selectbox("Couleur", ["Aucune"] + all_cols)
                    trend = st.checkbox("Ajouter une tendance", value=False)
                with chart:
                    fig = px.scatter(
                        df, x=x, y=y,
                        color=None if color == "Aucune" else color,
                        trendline="ols" if trend else None,
                        trendline_color_override=ORANGE,
                        opacity=0.75,
                    )
                    st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Boîte à moustaches":
            with controls:
                y = st.selectbox("Variable numérique", numeric_cols, key="box_y")
                category = st.selectbox("Catégorie", ["Aucune"] + [c for c in all_cols if c != y])
            with chart:
                fig = px.box(df, x=None if category == "Aucune" else category, y=y, points="outliers")
                st.plotly_chart(fig, use_container_width=True)

        else:
            with controls:
                date_col = st.selectbox("Date", date_cols)
                value_col = st.selectbox("Mesure", numeric_cols)
                grain = st.selectbox("Granularité", ["Jour", "Semaine", "Mois", "Trimestre"], index=2)
                aggregate = st.selectbox("Agrégation", ["Somme", "Moyenne", "Nombre"])
            rule = {"Jour": "D", "Semaine": "W", "Mois": "MS", "Trimestre": "QS"}[grain]
            how = {"Somme": "sum", "Moyenne": "mean", "Nombre": "count"}[aggregate]
            series = (
                df[[date_col, value_col]].dropna(subset=[date_col])
                .set_index(date_col)[value_col].resample(rule).agg(how).reset_index()
            )
            with chart:
                fig = px.line(series, x=date_col, y=value_col, markers=True)
                fig.update_traces(line_color=INDIGO, line_width=2.5, marker_color=ORANGE)
                st.plotly_chart(fig, use_container_width=True)

# ── Assistant IA ─────────────────────────────────────────────────────────────
with tabs[4]:
    history = st.session_state.setdefault("vd_history", [])
    summary = build_dataset_summary(df)
    use_ai = engine in providers

    left, right = st.columns([1.6, 1], gap="large")
    with right:
        st.html('<div class="vd-kicker">Questions suggérées</div>')
        for index, suggestion in enumerate(SUGGESTIONS):
            if st.button(suggestion, key=f"sugg_{index}", use_container_width=True):
                st.session_state["vd_pending"] = suggestion
        st.html('<hr class="vd-rule">')
        if use_ai:
            st.caption(
                f"{engine} · {providers[engine]['model']}. L'assistant ne reçoit qu'un résumé "
                "statistique et un échantillon de 12 lignes — jamais le fichier complet."
            )
        else:
            st.caption(
                "Analyse locale : les réponses sont calculées à partir de vos statistiques, "
                "sans appel externe. Changez de moteur dans la barre latérale pour une "
                "lecture rédigée."
            )
        if history and st.button("Effacer la conversation"):
            st.session_state["vd_history"] = []
            st.rerun()

    with left:
        st.markdown("#### Interroger les données")
        for message in history:
            if message["role"] == "user":
                st.markdown(f"**Question —** {message['content']}")
            else:
                st.markdown(message["content"])

        question = st.chat_input("Posez une question sur vos données…")
        pending = st.session_state.pop("vd_pending", None)
        question = question or pending

        if question:
            st.markdown(f"**Question —** {question}")
            history.append({"role": "user", "content": question})
            if use_ai:
                try:
                    with st.spinner("Analyse en cours…"):
                        stream = ask_assistant(
                            make_client(engine), providers[engine]["model"],
                            question, summary, history[:-1],
                        )
                        answer = st.write_stream(
                            chunk.choices[0].delta.content or "" for chunk in stream
                        )
                    history.append({"role": "assistant", "content": answer})
                except Exception as exc:
                    history.pop()
                    st.error(f"Impossible d'obtenir l'analyse via {engine} : {exc}")
            else:
                answer = local_answer(df, question)
                st.markdown(answer)
                history.append({"role": "assistant", "content": answer})

st.html('<hr class="vd-rule">')
st.caption("VisualizeData Assistant · build modernist-8 · accès libre")
