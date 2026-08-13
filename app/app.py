import io
import os
from datetime import datetime

import numpy as np
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
pio.templates["visualizedata_dark"] = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Archivo, system-ui, sans-serif", size=13, color="#f3f2f2"),
        paper_bgcolor="#1c1a19",
        plot_bgcolor="#1c1a19",
        colorway=[INDIGO, "#ff5c3d", "#bab6b6", "#7d7979", "#dd2b0f", "#f3f2f2"],
        margin=dict(l=44, r=18, t=32, b=42),
        xaxis=dict(showgrid=False, linecolor="rgba(243,242,242,.25)", linewidth=1,
                   ticks="outside", tickcolor="rgba(243,242,242,.25)", zeroline=False),
        yaxis=dict(gridcolor="rgba(243,242,242,.12)", linecolor="rgba(243,242,242,.25)",
                   linewidth=1, zeroline=False),
        bargap=0.08,
        hoverlabel=dict(bgcolor="#f3f2f2", bordercolor="#f3f2f2",
                        font=dict(color="#141312", family="Archivo")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    bgcolor="rgba(0,0,0,0)"),
    )
)
pio.templates.default = "visualizedata"

# ─────────────────────────────────────────────────────────────────────────────
# CSS — applique l'identité VisualizeData à l'interface Streamlit
# ─────────────────────────────────────────────────────────────────────────────
st.html(
    f"""<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap" rel="stylesheet"> <style> :root {{ --vd-navy:{NAVY}; --vd-indigo:{INDIGO}; --vd-orange:{ORANGE}; --vd-pale:{PALE}; --vd-ink:{INK}; --vd-muted:{MUTED}; --vd-line:{LINE}; --vd-r:{RADIUS}; }} html, body, .stApp, [class*="css"] {{ font-family:'Archivo', system-ui, sans-serif; background:{WHITE}; color:var(--vd-ink); }} h1,h2,h3,h4,h5,h6 {{ font-family:'Archivo', system-ui, sans-serif !important; font-weight:800 !important; letter-spacing:-.02em; line-height:1.16; color:var(--vd-navy); }} #MainMenu, footer, header [data-testid="stStatusWidget"] {{visibility:hidden}} .block-container {{padding-top:2rem; padding-bottom:4rem; max-width:1500px}} section[data-testid="stSidebar"] {{ background:var(--vd-pale); border-right:1px solid var(--vd-line); }} section[data-testid="stSidebar"] .block-container {{padding-top:1.5rem}} div[data-testid="stMetric"] {{ background:{WHITE}; padding:16px 18px; border:1px solid var(--vd-line); border-radius:var(--vd-r); }} div[data-testid="stMetricLabel"] p {{ font-size:12px !important; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:var(--vd-muted) !important; }} div[data-testid="stMetricValue"] {{ font-family:'Archivo', sans-serif; font-size:32px !important; font-weight:600; color:var(--vd-navy); }} .stTabs [data-baseweb="tab-list"] {{gap:6px; border-bottom:1px solid var(--vd-line)}} .stTabs [data-baseweb="tab"] {{ background:transparent; padding:11px 16px; font-weight:600; color:var(--vd-muted); }} .stTabs [aria-selected="true"] {{ color:var(--vd-indigo) !important; box-shadow:inset 0 -2px 0 0 var(--vd-indigo); }} .stTabs [data-baseweb="tab-highlight"] {{background:transparent}} .stButton button, .stDownloadButton button, .stFormSubmitButton button {{ font-family:'Archivo', sans-serif; font-weight:700; font-size:15px; border-radius:var(--vd-r); border:1px solid var(--vd-line); background:{WHITE}; color:var(--vd-navy); padding:10px 18px; }} .stButton button:hover {{border-color:var(--vd-indigo); color:var(--vd-indigo)}} .stButton button[kind="primary"], .stDownloadButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{ background:var(--vd-indigo); border-color:var(--vd-indigo); color:{WHITE}; }} .stButton button[kind="primary"]:hover, .stDownloadButton button[kind="primary"]:hover {{ background:{INDIGO_DARK}; border-color:{INDIGO_DARK}; color:{WHITE}; }} .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div, .stChatInput textarea {{ background:{WHITE} !important; border:1px solid var(--vd-line) !important; border-radius:var(--vd-r) !important; color:var(--vd-ink) !important; font-family:'Archivo', sans-serif; }} .stTextInput input:focus, .stTextArea textarea:focus {{border-color:var(--vd-indigo) !important}} *:focus-visible {{outline:2px solid var(--vd-indigo) !important; outline-offset:2px}} ::selection {{background:rgba(79,70,229,.18)}} .stSlider [data-baseweb="slider"] div[role="slider"] {{background:var(--vd-indigo)}} section[data-testid="stFileUploaderDropzone"] {{ background:{WHITE}; border:1.5px dashed #C3D3F5; border-radius:var(--vd-r); padding:22px; }} div[data-testid="stDataFrame"] {{ border:1px solid var(--vd-line); border-radius:var(--vd-r); overflow:hidden; }} .vd-rule {{height:1px; background:var(--vd-line); border:0; margin:24px 0}} .vd-kicker {{ font-size:12px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--vd-indigo); margin-bottom:10px; }} .vd-hero {{ background:linear-gradient(180deg,var(--vd-pale) 0%,{WHITE} 100%); border:1px solid var(--vd-line); border-radius:0; padding:30px 32px; margin-bottom:22px; }} .vd-hero h1 {{font-size:34px; margin:0 0 8px}} .vd-hero p {{color:var(--vd-muted); max-width:70ch; margin:0}} .vd-answer {{ background:var(--vd-pale); border:1px solid var(--vd-line); border-left:3px solid var(--vd-indigo); border-radius:var(--vd-r); padding:16px 18px; margin:6px 0 14px; }} .vd-poster {{ background:var(--vd-navy); color:{WHITE}; border-radius:0; padding:30px; }} .vd-poster .q {{ font-family:'Archivo', sans-serif; font-weight:600; font-size:24px; line-height:1.2; margin:0; }} .vd-poster .q em {{font-style:normal; color:var(--vd-orange)}} .vd-poster .row {{ display:flex; justify-content:space-between; padding:12px 0; border-top:1px solid rgba(255,255,255,.16); font-size:14px; }} .vd-feature {{ border:1px solid var(--vd-line); border-radius:var(--vd-r); padding:16px 18px; height:100%; }} .vd-feature b {{font-family:'Archivo', sans-serif; font-weight:600; display:block; margin-bottom:4px; color:var(--vd-navy)}} .vd-feature span {{color:var(--vd-muted); font-size:14px}} .vd-bar-label {{display:flex; justify-content:space-between; font-size:14px; margin-bottom:5px}} .vd-bar {{height:7px; background:var(--vd-pale); border-radius:0; overflow:hidden}} .vd-bar > div {{height:100%; background:var(--vd-indigo)}} .vd-bar.alert > div {{background:var(--vd-orange)}} .vd-tag {{ display:inline-block; font-size:12px; font-weight:700; padding:4px 12px; border-radius:0; background:rgba(79,70,229,.12); color:var(--vd-indigo); }}   .stApp {{ -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }} h1,h2,h3 {{ text-wrap:balance; }} p, li {{ text-wrap:pretty; }} .vd-kicker {{ font-weight:800; }}  .stTabs [data-baseweb="tab-list"] {{ overflow-x:auto !important; overflow-y:hidden; flex-wrap:nowrap !important; scrollbar-width:none; -webkit-overflow-scrolling:touch; }} .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display:none; }} .stTabs [data-baseweb="tab"] {{ flex:0 0 auto !important; white-space:nowrap !important; }} .stTabs [data-baseweb="tab"] p {{ white-space:nowrap !important; margin:0; }} div[data-testid="stPopover"] > div, div[data-baseweb="popover"] > div {{ border-radius:0 !important; }} .stTabs [data-baseweb="tab-list"] {{ display:flex !important; flex-wrap:nowrap !important; overflow-x:auto !important; overflow-y:hidden !important; scrollbar-width:none; -webkit-overflow-scrolling:touch; }} .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display:none; }} .stTabs [data-baseweb="tab"] {{ flex:0 0 auto !important; min-width:max-content !important; white-space:nowrap !important; }} .stTabs [data-baseweb="tab"] * {{ white-space:nowrap !important; word-break:keep-all !important; overflow-wrap:normal !important; }}</style>"""
)


# ─────────────────────────────────────────────────────────────────────────────
# Thème clair / sombre
# ─────────────────────────────────────────────────────────────────────────────
DARK_RULES = """ div[data-baseweb="popover"] div[data-testid="stPopoverBody"], div[data-testid="stPopover"] div[data-testid="stPopoverBody"] { background:#1c1a19 !important; border:1px solid rgba(243,242,242,.2) !important; } div[data-testid="stPopover"] button { background:#1c1a19 !important; border:1px solid rgba(243,242,242,.25) !important; color:#f3f2f2 !important; } .stApp, html, body { background:#141312 !important; color:#f3f2f2 !important; } .block-container { padding:1rem .9rem 3.5rem !important; max-width:100% !important; } h1,h2,h3,h4,h5,h6 { color:#f3f2f2 !important; letter-spacing:-.045em; } h1 {font-size:28px !important} h2 {font-size:23px !important} h3 {font-size:20px !important} h4 {font-size:17px !important} p, li, span, label, .stMarkdown { color:rgba(243,242,242,.85) !important; } .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:rgba(243,242,242,.45) !important; } section[data-testid="stSidebar"] { background:#0d0c0c !important; border-right:1px solid rgba(243,242,242,.14) !important; } section[data-testid="stSidebar"] * { color:#f3f2f2 !important; } div[data-testid="stHorizontalBlock"] { flex-direction:column; gap:12px; } div[data-testid="column"] { width:100% !important; flex:1 1 100% !important; min-width:100% !important; } div[data-testid="stMetric"] { background:#1c1a19 !important; border:0 !important; border-radius:0 !important; padding:14px 16px !important; } div[data-testid="stMetricValue"] { color:#f3f2f2 !important; font-size:27px !important; letter-spacing:-.04em; } div[data-testid="stMetricLabel"] p { color:rgba(243,242,242,.45) !important; font-size:9px !important; letter-spacing:.14em; } .stTabs [data-baseweb="tab-list"] { overflow-x:auto; scrollbar-width:none; gap:0; border-bottom:1px solid rgba(243,242,242,.16); } .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {display:none} .stTabs [data-baseweb="tab"] { padding:12px 14px; font-size:13px; white-space:nowrap; color:rgba(243,242,242,.5) !important; } .stTabs [aria-selected="true"] { color:#ff5c3d !important; box-shadow:inset 0 -2px 0 0 #ec3013; } .stTabs [aria-selected="true"] p { color:#ff5c3d !important; } .stButton button, .stDownloadButton button, .stFormSubmitButton button { min-height:48px; width:100%; font-size:15px; border-radius:0 !important; background:transparent !important; border:1px solid rgba(243,242,242,.3) !important; color:#f3f2f2 !important; } .stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background:#ec3013 !important; border-color:#ec3013 !important; color:#f3f2f2 !important; } .stTextInput input, .stTextArea textarea, .stNumberInput input, .stChatInput textarea, div[data-baseweb="select"] > div { background:#1c1a19 !important; border:1px solid rgba(243,242,242,.22) !important; color:#f3f2f2 !important; min-height:48px; font-size:16px; border-radius:0 !important; } div[data-baseweb="select"] svg { fill:#f3f2f2 !important; } section[data-testid="stFileUploaderDropzone"] { background:#1c1a19 !important; border:1.5px dashed rgba(243,242,242,.3) !important; } section[data-testid="stFileUploaderDropzone"] * { color:rgba(243,242,242,.75) !important; } div[data-testid="stDataFrame"] { border:1px solid rgba(243,242,242,.16) !important; font-size:12px; } .stExpander, details { background:#1c1a19 !important; border:1px solid rgba(243,242,242,.16) !important; border-radius:0 !important; } .stExpander summary, details summary { color:#f3f2f2 !important; } .vd-rule { background:rgba(243,242,242,.16) !important; } .vd-kicker { color:#ff5c3d !important; } .vd-hero { background:#1c1a19 !important; border:0 !important; border-left:2px solid #ec3013 !important; padding:20px 18px !important; } .vd-hero h1 { font-size:26px !important; } .vd-hero p { color:rgba(243,242,242,.65) !important; } .vd-answer { background:#1c1a19 !important; border:0 !important; border-left:2px solid #ec3013 !important; border-radius:0 !important; color:rgba(243,242,242,.9) !important; } .vd-answer * { color:rgba(243,242,242,.9) !important; } .vd-feature { background:#1c1a19 !important; border:0 !important; padding:14px 16px !important; } .vd-feature b { color:#f3f2f2 !important; } .vd-feature span { color:rgba(243,242,242,.55) !important; } .vd-poster { background:#ec3013 !important; padding:22px !important; } .vd-poster .q { font-size:20px !important; } .vd-bar { background:rgba(243,242,242,.16) !important; } .vd-bar > div { background:#f3f2f2 !important; } .vd-bar.alert > div { background:#ec3013 !important; } .vd-tag { background:rgba(236,48,19,.22) !important; color:#ff5c3d !important; } hr { border-color:rgba(243,242,242,.16) !important; } .stAlert { border-radius:0 !important; } ::selection { background:rgba(236,48,19,.4); } h1 { font-size:30px !important; line-height:.98 !important; letter-spacing:-.05em !important; } h2 { font-size:24px !important; line-height:1.02 !important; } h3 { font-size:20px !important; } h4 { font-size:17px !important; } p, li, .stMarkdown p { font-size:15px !important; line-height:1.55 !important; } .vd-kicker { font-size:10px !important; letter-spacing:.18em !important; } .vd-hero h1 { font-size:28px !important; line-height:.98 !important; } .vd-hero p { font-size:14px !important; } div[data-testid="stMetricValue"] { font-variant-numeric:tabular-nums; } section[data-testid="stFileUploaderDropzone"] { padding:26px 18px !important; } section[data-testid="stFileUploaderDropzone"] button { background:#ec3013 !important; border-color:#ec3013 !important; color:#f3f2f2 !important; } label[data-testid="stWidgetLabel"] p { font-size:11px !important; letter-spacing:.16em; text-transform:uppercase; color:#ff5c3d !important; font-weight:800 !important; } .vd-feature { margin-bottom:10px; }"""

_theme = st.session_state.get("vd_theme", "Auto")
if _theme == "Sombre":
    st.html("<style>" + DARK_RULES + "</style>")
    pio.templates.default = "visualizedata_dark"
elif _theme == "Auto":
    st.html("<style>@media (max-width: 900px) {" + DARK_RULES + "}</style>")


# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Exemples, limites de session et retours
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = {
    "Ventes d'une PME de distribution": (
        "ventes_distribution.csv",
        "1 400 commandes sur un an : régions, canaux, familles de produits, remises.",
    ),
    "Enquête de satisfaction client": (
        "satisfaction_clients.csv",
        "820 réponses NPS par agence et par canal de contact.",
    ),
    "Suivi de stocks": (
        "suivi_stocks.csv",
        "540 références, seuils, délais de réapprovisionnement, rotation.",
    ),
    "Fichier volontairement sale": (
        "commandes_brut.csv",
        "Export brut avec lignes de titre, montants en texte et régions fusionnées.",
    ),
}

MAX_UPLOAD_MB = 50
MAX_AI_QUESTIONS = 30


@st.cache_data(show_spinner=False)
def example_bytes(filename: str) -> bytes:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exemples", filename)
    with open(path, "rb") as handle:
        return handle.read()


class ExampleFile:
    """Se comporte comme un fichier importé, pour réutiliser le même pipeline."""

    def __init__(self, name: str, payload: bytes):
        self.name = name
        self._payload = payload

    def getvalue(self) -> bytes:
        return self._payload


def ai_quota_left() -> int:
    return MAX_AI_QUESTIONS - st.session_state.get("vd_ai_calls", 0)


def consume_ai_quota() -> None:
    st.session_state["vd_ai_calls"] = st.session_state.get("vd_ai_calls", 0) + 1


def send_feedback(subject: str, body: str) -> tuple[bool, str]:
    """Envoie un retour via un service compatible SMTP (Resend, Brevo…)."""
    import smtplib
    from email.message import EmailMessage

    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user or "")
    recipient = os.getenv("FEEDBACK_TO", "mdjoman@upb.ci")

    if not (host and user and password and sender):
        return False, "envoi non configuré"

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(body)
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=12) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(message)
        return True, "envoyé"
    except Exception as exc:
        return False, str(exc)


def record_feedback(kind: str, detail: str, extra: str = "") -> None:
    """Consigne le retour dans la session et tente l'envoi par e-mail."""
    entry = {
        "moment": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "type": kind,
        "detail": detail,
        "contexte": extra,
    }
    st.session_state.setdefault("vd_feedback", []).append(entry)
    body = (
        f"Type : {kind}\n"
        f"Détail : {detail}\n"
        f"Contexte : {extra}\n"
        f"Moment : {entry['moment']}\n"
        f"Moteur : {st.session_state.get('vd_engine_label', 'inconnu')}\n"
    )
    send_feedback(f"VisualizeData — retour ({kind})", body)



# Chargement des données
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(raw: bytes, name: str, sheet: str | None = None,
              smart_header: bool = True) -> pd.DataFrame:
    lower = name.lower()
    if lower.endswith(".csv"):
        last_error: Exception | None = None
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                table = pd.read_csv(
                    io.BytesIO(raw), encoding=encoding, sep=None, engine="python",
                    header=None if smart_header else 0,
                )
                return _promote_header(table) if smart_header else table
            except Exception as exc:  # séparateur ou encodage incompatible
                last_error = exc
        raise ValueError(f"Impossible de lire ce fichier CSV : {last_error}")

    table = pd.read_excel(
        io.BytesIO(raw), sheet_name=sheet or 0, header=None if smart_header else 0
    )
    return _promote_header(table) if smart_header else table


def _promote_header(raw: pd.DataFrame) -> pd.DataFrame:
    """Promeut en en-tête la première ligne réellement porteuse de noms de colonnes."""
    if raw.empty:
        return raw
    index = detect_header_row(raw)
    table = raw.iloc[index + 1:].copy()
    table.columns = raw.iloc[index]
    return table.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def excel_sheets(raw: bytes) -> list[str]:
    return pd.ExcelFile(io.BytesIO(raw)).sheet_names


def detect_header_row(raw: pd.DataFrame, scan: int = 12) -> int:
    """Trouve la ligne qui sert réellement d'en-tête dans un export brut."""
    best, best_score = 0, -1.0
    for i in range(min(scan, len(raw))):
        row = raw.iloc[i]
        values = [str(v).strip() for v in row if str(v).strip() not in ("", "nan", "None")]
        if len(values) < max(2, int(raw.shape[1] * 0.5)):
            continue
        unique = len(set(values)) / len(values)
        textual = sum(not str(v).replace(".", "", 1).replace("-", "", 1).isdigit()
                      for v in values) / len(values)
        below = raw.iloc[i + 1: i + 6]
        filled = below.notna().mean().mean() if len(below) else 0
        score = unique + textual + filled
        if score > best_score:
            best, best_score = i, score
    return best


def clean_columns(columns) -> list[str]:
    seen, output = {}, []
    for index, name in enumerate(columns):
        label = str(name).strip()
        if label.lower().startswith("unnamed") or label in ("", "nan", "None"):
            label = f"colonne_{index + 1}"
        label = " ".join(label.split())
        if label in seen:
            seen[label] += 1
            label = f"{label}_{seen[label]}"
        else:
            seen[label] = 0
        output.append(label)
    return output


def autoclean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Rend exploitable un export brut. Retourne le tableau nettoyé et le journal."""
    log: list[str] = []
    out = df.copy()

    before = out.shape
    out = out.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if out.shape != before:
        log.append(
            f"{before[0] - out.shape[0]} lignes et {before[1] - out.shape[1]} colonnes "
            "entièrement vides supprimées."
        )

    renamed = clean_columns(out.columns)
    if list(out.columns) != renamed:
        log.append("En-têtes normalisés (espaces, doublons, colonnes sans nom).")
    out.columns = renamed

    # cellules fusionnées : une colonne d'étiquettes trouée se propage vers le bas
    for col in out.columns:
        series = out[col]
        if series.dtype == object:
            ratio = series.isna().mean()
            filled = series.dropna()
            if 0.3 < ratio < 0.95 and filled.nunique() < max(2, len(filled) * 0.4):
                out[col] = series.ffill()
                log.append(f"Cellules fusionnées reconstituées sur « {col} ».")

    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].astype(str).str.strip().replace(
            {"": None, "nan": None, "None": None, "-": None, "N/A": None, "n/a": None}
        )

    converted = []
    for col in out.select_dtypes(include="object").columns:
        sample = out[col].dropna().astype(str)
        if sample.empty:
            continue
        candidate = (
            sample.str.replace(r"[\s\u00a0]", "", regex=True)
            .str.replace("%", "", regex=False)
            .str.replace(r"^([^\d\-\.,]+)", "", regex=True)
            .str.replace(",", ".", regex=False)
        )
        numeric = pd.to_numeric(candidate, errors="coerce")
        if numeric.notna().mean() > 0.9:
            full = (
                out[col].astype(str)
                .str.replace(r"[\s\u00a0]", "", regex=True)
                .str.replace("%", "", regex=False)
                .str.replace(r"^([^\d\-\.,]+)", "", regex=True)
                .str.replace(",", ".", regex=False)
            )
            out[col] = pd.to_numeric(full, errors="coerce")
            converted.append(col)
    if converted:
        log.append("Converti en nombres : " + ", ".join(converted) + ".")

    duplicates = int(out.duplicated().sum())
    if duplicates:
        log.append(f"{duplicates} lignes en double détectées (conservées, à vous de trancher).")

    return out.reset_index(drop=True), log


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


def is_identifier(series: pd.Series, name: str) -> bool:
    """Repère les colonnes d'identifiants : inutiles à représenter en histogramme."""
    label = str(name).lower()
    if any(token in label for token in ("_id", "id_", "code", "numero", "num_", "ref", "matricule")):
        return True
    if label in ("id", "index", "n", "no"):
        return True
    valid = series.dropna()
    if valid.empty:
        return False
    if valid.nunique() / len(valid) > 0.95 and len(valid) > 20:
        return True
    return False


def rank_measures(df: pd.DataFrame) -> list[str]:
    """Colonnes numériques ordonnées de la plus parlante à la moins parlante."""
    numeric = df.select_dtypes(include="number").columns.tolist()
    measures = [c for c in numeric if not is_identifier(df[c], c)]
    return measures or numeric


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


def business_context() -> str:
    """Contexte métier, saisi depuis la barre d'état ou depuis le fil de discussion."""
    for key in ("vd_context", "vd_context_inline"):
        value = st.session_state.get(key, "")
        if value and value.strip():
            return value.strip()
    return ""


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


# ──────────────────────────────────────────────────────────────────
# Moteur de calcul — l'IA écrit du code pandas, on l'exécute nous-mêmes
# ──────────────────────────────────────────────────────────────────
SAFE_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "filter": filter, "float": float, "int": int,
    "len": len, "list": list, "map": map, "max": max, "min": min,
    "range": range, "round": round, "set": set, "sorted": sorted, "str": str,
    "sum": sum, "tuple": tuple, "zip": zip, "isinstance": isinstance,
    "type": type, "print": lambda *a, **k: None,
}

FORBIDDEN = (
    "import ", "__", "open(", "eval(", "exec(", "compile(", "globals(",
    "locals(", "getattr", "setattr", "delattr", "input(", "exit(", "quit(",
    "os.", "sys.", "subprocess", "socket", "requests", "urllib", "shutil",
    "pathlib", "pickle", "to_csv", "to_excel", "to_pickle", "read_csv",
    "read_excel", "write", "remove", "rmtree", "system",
)

CODE_PROMPT = """Tu écris du code Python pandas pour répondre à une question sur un DataFrame nommé `df`.

RÈGLES ABSOLUES :
- Réponds UNIQUEMENT par du code Python, sans texte, sans balises markdown.
- `df`, `pd` et `px` (plotly.express) sont déjà disponibles. N'importe RIEN.
- Affecte le résultat chiffré à une variable nommée `result` (DataFrame, Series ou nombre).
- Si un graphique éclaire la réponse, affecte une figure plotly à `fig`. Sinon, ne définis pas `fig`.
- N'écris aucun fichier, n'accède à aucune ressource externe, n'utilise pas print().
- Reste sur les colonnes réellement présentes.
- Code court : cinq lignes au maximum.

SCHÉMA DU DATAFRAME :
{schema}
"""


def dataframe_schema(df: pd.DataFrame) -> str:
    lines = [f"{len(df)} lignes, {len(df.columns)} colonnes", ""]
    for col in df.columns:
        series = df[col]
        detail = f"- {col} ({series.dtype})"
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            if not valid.empty:
                detail += f" — de {valid.min():.4g} à {valid.max():.4g}, moyenne {valid.mean():.4g}"
        elif pd.api.types.is_datetime64_any_dtype(series):
            valid = series.dropna()
            if not valid.empty:
                detail += f" — du {valid.min():%Y-%m-%d} au {valid.max():%Y-%m-%d}"
        else:
            modalities = series.dropna().astype(str).unique()[:8]
            if len(modalities):
                detail += " — ex. " + ", ".join(map(str, modalities))
        if series.isna().any():
            detail += f" [{series.isna().sum()} manquants]"
        lines.append(detail)
    return "\n".join(lines)


def generate_code(client: OpenAI, model: str, question: str, df: pd.DataFrame) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CODE_PROMPT.format(schema=dataframe_schema(df))},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    code = response.choices[0].message.content or ""
    code = code.replace("```python", "```").split("```")
    code = code[1] if len(code) > 1 else code[0]
    return code.strip()


def run_code(code: str, df: pd.DataFrame) -> tuple[object, object, str | None]:
    """Exécute le code dans un espace restreint. Retourne (result, fig, erreur)."""
    lowered = code.lower()
    for pattern in FORBIDDEN:
        if pattern in lowered:
            return None, None, f"Instruction refusée par la sécurité : `{pattern.strip()}`"

    scope = {"df": df.copy(), "pd": pd, "px": px, "go": go}
    try:
        exec(code, {"__builtins__": SAFE_BUILTINS}, scope)
    except Exception as exc:
        return None, None, f"{type(exc).__name__} : {exc}"
    return scope.get("result"), scope.get("fig"), None


def result_to_text(result: object) -> str:
    if result is None:
        return "aucun résultat"
    if isinstance(result, pd.DataFrame):
        return result.head(30).to_string()
    if isinstance(result, pd.Series):
        return result.head(30).to_string()
    if isinstance(result, float):
        return f"{result:,.4g}".replace(",", " ")
    return str(result)


COMMENT_PROMPT = """Tu es VisualizeData Assistant, analyste de données pour des dirigeants de PME
sans compétence technique. On te donne une question, le code exécuté et son RÉSULTAT RÉEL.

Rédige en français une réponse courte et directe :
- Commence par la réponse chiffrée, en reprenant EXACTEMENT les chiffres du résultat.
- Explique ce que cela signifie pour l'activité, en une ou deux phrases.
- Termine par une seule recommandation actionnable.
N'invente aucun chiffre absent du résultat. Ne mentionne ni le code ni pandas.
{context}"""


def comment_result(client: OpenAI, model: str, question: str, code: str,
                   result: object, context: str):
    context_block = f"\nCONTEXTE MÉTIER FOURNI PAR LE CLIENT :\n{context}" if context else ""
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": COMMENT_PROMPT.format(context=context_block)},
            {"role": "user", "content": (
                f"QUESTION :\n{question}\n\nCODE EXÉCUTÉ :\n{code}\n\n"
                f"RÉSULTAT RÉEL :\n{result_to_text(result)}"
            )},
        ],
        temperature=0.2,
        stream=True,
    )


def ask_assistant(client: OpenAI, model: str, question: str, summary: str, history: list[dict]):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
    messages.append({"role": "user", "content": f"QUESTION:\n{question}\n\nDONNÉES RÉSUMÉES:\n{summary}"})
    return client.chat.completions.create(model=model, messages=messages, temperature=0.2, stream=True)


BRIEF_PROMPT = """Tu es analyste de données pour des dirigeants de PME sans compétence technique.
À partir du diagnostic ci-dessous, rédige en français un briefing de lecture immédiate :

**Ce qu'il faut retenir** — trois puces maximum, chacune avec un chiffre du diagnostic.
**Ce qu'il faut surveiller** — une puce sur la fiabilité des données.
**Prochaine action** — une seule phrase, concrète.

N'invente aucun chiffre. Pas de préambule, pas de conclusion générale.
{context}"""


def ai_briefing(client: OpenAI, model: str, summary: str, insights: list[str], context: str) -> str:
    context_block = f"\nCONTEXTE MÉTIER :\n{context}" if context else ""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": BRIEF_PROMPT.format(context=context_block)},
            {"role": "user", "content": "DIAGNOSTIC :\n" + "\n".join(insights) + "\n\n" + summary},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def forecast_series(df: pd.DataFrame, date_col: str, value_col: str, periods: int = 3):
    """Projection linéaire simple sur les valeurs mensuelles agrégées."""
    monthly = (
        df[[date_col, value_col]].dropna(subset=[date_col])
        .set_index(date_col)[value_col].resample("MS").sum()
    )
    monthly = monthly[monthly.notna()]
    if len(monthly) < 4:
        return None, None
    x = np.arange(len(monthly))
    slope, intercept = np.polyfit(x, monthly.values, 1)
    future_x = np.arange(len(monthly), len(monthly) + periods)
    future_index = pd.date_range(
        monthly.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="MS"
    )
    projection = pd.Series(slope * future_x + intercept, index=future_index)
    return monthly, projection


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
# Modélisation — prédiction, importance des variables, fiabilité
# ──────────────────────────────────────────────────────────────────
def suggest_target(df: pd.DataFrame) -> str | None:
    """Propose la colonne la plus intéressante à prédire."""
    priority = ("montant", "chiffre", "ca", "revenu", "prix", "total", "quantite",
                "score", "nps", "satisfaction", "churn", "retard", "statut", "resultat")
    candidates = []
    for col in df.columns:
        series = df[col]
        label = str(col).lower()
        if is_identifier(series, col) or series.isna().mean() > 0.4:
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            continue
        if pd.api.types.is_numeric_dtype(series):
            kind, score = "num", 2
        elif 2 <= series.nunique(dropna=True) <= 12:
            kind, score = "cat", 2
        else:
            continue
        if any(token in label for token in priority):
            score += 4
        candidates.append((score, col, kind))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def modelable_targets(df: pd.DataFrame) -> list[str]:
    targets = []
    for col in df.columns:
        series = df[col]
        if is_identifier(series, col) or series.isna().mean() > 0.4:
            continue
        if pd.api.types.is_datetime64_any_dtype(series):
            continue
        if pd.api.types.is_numeric_dtype(series) or 2 <= series.nunique(dropna=True) <= 12:
            targets.append(col)
    return targets


@st.cache_data(show_spinner=False)
def train_model(df: pd.DataFrame, target: str) -> dict:
    """Entraîne un modèle léger et retourne tout ce qu'il faut pour l'expliquer."""
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error
    from sklearn.model_selection import train_test_split

    work = df.dropna(subset=[target]).copy()
    if len(work) < 40:
        return {"error": "Il faut au moins 40 lignes renseignées pour entraîner un modèle."}

    y = work[target]
    features = [
        c for c in work.columns
        if c != target and not is_identifier(work[c], c) and work[c].isna().mean() < 0.5
    ]
    if not features:
        return {"error": "Aucune variable explicative exploitable dans ce fichier."}

    X = work[features].copy()
    for col in X.columns:
        if pd.api.types.is_datetime64_any_dtype(X[col]):
            X[col] = X[col].view("int64") // 10**9
        elif not pd.api.types.is_numeric_dtype(X[col]):
            if X[col].nunique() > 40:
                X = X.drop(columns=[col])
                continue
            X[col] = X[col].astype("category").cat.codes
    X = X.fillna(X.median(numeric_only=True)).fillna(-1)
    if X.empty:
        return {"error": "Aucune variable explicative exploitable dans ce fichier."}

    classification = not pd.api.types.is_numeric_dtype(y) or y.nunique() <= 12
    if classification:
        y = y.astype(str)
        if y.value_counts().min() < 5:
            return {"error": "Certaines catégories sont trop rares pour être apprises."}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=0,
        stratify=y if classification and y.nunique() > 1 else None,
    )
    model = (
        RandomForestClassifier(n_estimators=160, random_state=0, n_jobs=-1, min_samples_leaf=2)
        if classification else
        RandomForestRegressor(n_estimators=160, random_state=0, n_jobs=-1, min_samples_leaf=2)
    )
    model.fit(X_train, y_train)
    predicted = model.predict(X_test)

    importance = (
        pd.Series(model.feature_importances_, index=X.columns)
        .sort_values(ascending=False).head(8)
    )
    result = {
        "target": target,
        "classification": classification,
        "features": list(X.columns),
        "importance": importance,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
    if classification:
        result["score"] = float(accuracy_score(y_test, predicted))
        result["baseline"] = float(y_train.value_counts(normalize=True).max())
        result["classes"] = sorted(y.unique().tolist())
        probabilities = model.predict_proba(X_test)
        result["risk"] = pd.DataFrame({
            "ligne": X_test.index,
            "prédit": predicted,
            "réel": y_test.values,
            "confiance": probabilities.max(axis=1).round(3),
        }).sort_values("confiance")
    else:
        result["score"] = float(r2_score(y_test, predicted))
        result["mae"] = float(mean_absolute_error(y_test, predicted))
        result["moyenne"] = float(y_test.mean())
        comparison = pd.DataFrame({"réel": y_test.values, "prédit": predicted}, index=X_test.index)
        comparison["écart"] = (comparison["prédit"] - comparison["réel"]).round(2)
        result["comparison"] = comparison
        result["risk"] = comparison.reindex(
            comparison["écart"].abs().sort_values(ascending=False).index
        ).head(20)
    return result


def reliability_label(score: float, classification: bool, baseline: float = 0.0) -> tuple[str, str]:
    """Retourne (niveau, phrase) — affirmatif, mais jamais trompeur."""
    if classification:
        gain = score - baseline
        if score >= 0.85 and gain > 0.1:
            return "Élevée", "Le modèle reconnaît bien les cas de votre historique."
        if score >= 0.7 and gain > 0.05:
            return "Correcte", "Le modèle est utile pour orienter, pas pour trancher seul."
        return "Faible", "Les données actuelles n'expliquent pas assez ce résultat."
    if score >= 0.7:
        return "Élevée", "Le modèle reproduit fidèlement les valeurs observées."
    if score >= 0.4:
        return "Correcte", "Le modèle capte la tendance générale, avec une marge d'erreur réelle."
    return "Faible", "Les variables disponibles n'expliquent pas assez cette valeur."


MODEL_PROMPT = """Tu es analyste de données pour un dirigeant de PME sans compétence technique.
On te donne le résultat d'un modèle prédictif. Rédige en français, ton affirmatif et direct :

**Conclusion** — une phrase : ce que le modèle permet de faire concrètement.
**Ce qui pèse le plus** — deux ou trois puces reprenant les variables les plus importantes,
traduites en langage métier.
**Action** — une seule phrase.

N'emploie aucun terme technique (pas de R², accuracy, random forest, features).
N'invente aucun chiffre absent des données fournies.
{context}"""


def explain_model(client: OpenAI, model_name: str, result: dict, context: str):
    context_block = f"\nCONTEXTE MÉTIER :\n{context}" if context else ""
    kind = "catégorie" if result["classification"] else "valeur"
    payload = (
        f"On cherche à estimer la {kind} de « {result['target']} ».\n"
        f"Fiabilité : {result['label']} — {result['sentence']}\n"
        f"Variables les plus influentes (de la plus forte à la plus faible) :\n"
        + result["importance"].round(3).to_string()
    )
    return client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": MODEL_PROMPT.format(context=context_block)},
            {"role": "user", "content": payload},
        ],
        temperature=0.2,
        stream=True,
    )


# ──────────────────────────────────────────────────────────────────
# En-tête et import — dans le flux principal, visible sur téléphone
# ──────────────────────────────────────────────────────────────────
st.html(
    """<div class="vd-hero"> <div class="vd-kicker">Assistant IA</div> <h1>Transformer les données en décisions</h1> <p>Importez un fichier CSV ou Excel : audit de qualité, statistiques, visualisations et réponses en langage naturel — sans Python ni SQL.</p> </div>"""
)

st.segmented_control(
    "Apparence", ["Auto", "Clair", "Sombre"], default="Auto",
    key="vd_theme", label_visibility="collapsed",
    help="Auto : sombre sur téléphone et tablette, clair sur ordinateur.",
)

uploaded_file = st.file_uploader(
    "Déposez un fichier CSV ou Excel",
    type=["csv", "xlsx", "xls"],
    help=f"CSV, XLSX ou XLS · jusqu'à {MAX_UPLOAD_MB} Mo · séparateur et encodage "
         "détectés automatiquement.",
)

if uploaded_file is not None and uploaded_file.size > MAX_UPLOAD_MB * 1024 * 1024:
    st.error(
        f"Ce fichier dépasse {MAX_UPLOAD_MB} Mo. Réduisez-le ou envoyez seulement "
        "les colonnes utiles à l'analyse."
    )
    st.stop()

st.caption(
    "Vos fichiers ne sont jamais enregistrés : ils restent en mémoire le temps de la "
    "session et disparaissent à la fermeture de l'onglet. L'assistant IA ne reçoit "
    "qu'un résumé statistique et un échantillon de douze lignes, jamais le fichier entier."
)

if uploaded_file is None:
    st.html('<div class="vd-kicker" style="margin-top:26px">Ou essayez un exemple</div>')
    st.caption("Aucun fichier sous la main ? Chargez un jeu de démonstration en un clic.")
    example_choice = st.selectbox(
        "Jeu d'exemple", list(EXAMPLES),
        format_func=lambda name: f"{name} — {EXAMPLES[name][1]}",
        label_visibility="collapsed",
    )
    if st.button("Charger cet exemple", type="primary", use_container_width=True):
        filename = EXAMPLES[example_choice][0]
        st.session_state["vd_example"] = filename
        record_feedback("exemple chargé", example_choice)
        st.rerun()

if uploaded_file is None and st.session_state.get("vd_example"):
    _name = st.session_state["vd_example"]
    uploaded_file = ExampleFile(_name, example_bytes(_name))

sheet_name = None
if uploaded_file is not None and not uploaded_file.name.lower().endswith(".csv"):
    sheets = excel_sheets(uploaded_file.getvalue())
    if len(sheets) > 1:
        sheet_name = st.selectbox("Feuille du classeur", sheets)

if uploaded_file is None:
    st.html('<div class="vd-kicker" style="margin-top:28px">Ce que fait l\'assistant</div>')
    features = [
        ("Nettoyage automatique", "Détecte l'en-tête réel, supprime les lignes vides, "
                                  "reconstitue les cellules fusionnées, convertit les nombres."),
        ("Audit de qualité", "Manquants, doublons, valeurs extrêmes, complétude par variable."),
        ("Statistiques et graphiques", "Descriptives, corrélations, histogramme, nuage, "
                                       "boîte, série temporelle, projection."),
        ("Questions en français", "L'assistant calcule sur vos données puis explique le résultat."),
    ]
    for title, description in features:
        st.html(f'<div class="vd-feature"><b>{title}</b><span>{description}</span></div>')

    st.html(
        """<div class="vd-poster" style="margin-top:22px"> <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;opacity:.75;margin-bottom:14px">Exemple de sortie</div> <p class="q">« Le canal revendeur recule de 9 % pendant que <em>le direct progresse.</em> »</p> <div style="margin-top:26px"> <div class="row"><span style="opacity:.85">Fichiers acceptés</span><span style="font-weight:800">CSV · XLSX · XLS</span></div> <div class="row"><span style="opacity:.85">Temps moyen d'analyse</span><span style="font-weight:800">&lt; 5 s</span></div> <div class="row"><span style="opacity:.85">Installation</span><span style="font-weight:800">Aucune</span></div> </div> </div>"""
    )
    st.html('<hr class="vd-rule">')
    st.caption(
        "Application hébergée sur une instance gratuite : après une période d'inactivité, "
        "le premier chargement peut prendre une minute, le temps que le service se réveille. "
        "Les suivants sont immédiats."
    )
    st.caption("VisualizeData Assistant · build modernist-20")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────
# Barre latérale — réglages, une fois le fichier chargé
# ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html(
        f'<div style="display:flex;align-items:center;gap:10px;padding:2px 0 6px">'
        f'{MARK}'
        f'<span style="font-family:Archivo,sans-serif;font-weight:800;font-size:18px;letter-spacing:-.035em">'
        f'Visualize<span style="color:{INDIGO}">Data</span></span></div>'
        f'<div style="color:{MUTED};font-size:12px">Transformer les données en décisions</div>'
    )

    st.html('<hr class="vd-rule" style="margin:14px 0">')

    st.html(
        f'<div style="padding:2px 0 8px"><b style="font-weight:800">{uploaded_file.name}</b></div>'
    )
    smart_header = st.toggle(
        "Nettoyage automatique", value=True,
        help="Détecte la ligne d'en-tête, supprime les lignes et colonnes vides, "
             "reconstitue les cellules fusionnées et convertit les nombres écrits en texte.",
    )

    if st.session_state.get("vd_example"):
        st.caption("Jeu de démonstration")
        if st.button("Charger mon propre fichier", use_container_width=True):
            del st.session_state["vd_example"]
            st.rerun()

    st.html('<div class="vd-kicker" style="margin-top:18px">Parcours</div>')
    for index, step in enumerate(
        ["Importer un fichier", "Explorer les indicateurs",
         "Visualiser les données", "Interroger avec l'IA"], start=1
    ):
        st.html(
            f'<div style="display:flex;gap:12px;padding:9px 0;'
            f'border-bottom:1px solid {LINE};font-size:14px">'
            f'<span style="font-weight:700;color:{INDIGO}">{index}</span><span>{step}</span></div>'
        )



# ─────────────────────────────────────────────────────────────────────────────
# Lecture du fichier
# ─────────────────────────────────────────────────────────────────────────────
try:
    df = load_data(uploaded_file.getvalue(), uploaded_file.name, sheet_name, smart_header)
except Exception as exc:
    st.error(f"Erreur de lecture : {exc}")
    st.stop()

if df.empty:
    st.warning("Le fichier ne contient aucune donnée.")
    st.stop()

df, clean_log = autoclean(df)
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

if clean_log:
    with st.expander(f"Nettoyage automatique — {len(clean_log)} correction(s) appliquée(s)"):
        for entry in clean_log:
            st.markdown(f"- {entry}")
        st.caption(
            "Le fichier d'origine n'est pas modifié. Le CSV nettoyé est téléchargeable "
            "dans l'onglet Aperçu."
        )

if insights:
    st.html('<div class="vd-kicker" style="margin-top:26px">Constats automatiques</div>')
    for note in insights:
        st.markdown(f"- {note}")

# ──────────────────────────────────────────────────────────────────
# Moteur d'analyse — dans le flux principal, atteignable sur téléphone
# ──────────────────────────────────────────────────────────────────
providers = available_providers()
engine_options = ["Analyse locale (sans clé)"] + list(providers)

# Barre d'état : moteur, calcul exact, contexte — toujours visibles
_context_set = bool(business_context())
bar_engine, bar_compute, bar_context = st.columns(3, gap="small")

with bar_engine:
    engine = st.selectbox("Moteur d'analyse", engine_options)
    st.session_state["vd_engine_label"] = engine
    if engine in providers:
        st.caption(providers[engine]["model"])
    else:
        st.caption("Sans clé · aucune donnée ne sort")

with bar_compute:
    if engine in providers:
        compute_mode = st.toggle(
            "Calcul exact", value=True,
            help="L'assistant écrit une requête, l'exécute sur votre fichier et commente "
                 "le résultat réel. Désactivé, il raisonne sur le résumé statistique.",
        )
        st.caption("Requête exécutée sur le fichier" if compute_mode
                   else "Raisonnement sur le résumé")
    else:
        compute_mode = False
        st.toggle("Calcul exact", value=False, disabled=True,
                  help="Nécessite une clé IA.")
        st.caption("Indisponible sans clé IA")

with bar_context:
    with st.popover(
        ("Contexte renseigné" if _context_set else "Contexte métier — à renseigner"),
        use_container_width=True,
    ):
        st.text_area(
            "Décrivez votre activité en deux phrases",
            placeholder="Ex. : distributeur de matériaux, 3 agences, saison haute de mars "
                        "à juin. Le canal revendeur est prioritaire cette année.",
            height=140,
            key="vd_context",
        )
        st.caption(
            "L'assistant s'en sert pour interpréter vos chiffres au lieu de les décrire. "
            "Repris dans le briefing, les réponses et la conclusion du modèle."
        )
    st.caption("Améliore nettement les réponses" if not _context_set
               else "Repris dans toutes les réponses")

if not providers:
    st.caption(
        "Aucune clé IA détectée. Pour des réponses rédigées, ajoutez une variable dans "
        "Render → Environment : GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, "
        "MISTRAL_API_KEY ou OPENROUTER_API_KEY."
    )

_engine_ready = engine in providers
if _engine_ready:
    _brief_key = f"vd_brief::{uploaded_file.name}::{sheet_name}"
    if _brief_key not in st.session_state:
        if st.button("Lire le briefing de l'assistant", type="primary"):
            try:
                with st.spinner("Lecture du jeu de données…"):
                    st.session_state[_brief_key] = ai_briefing(
                        make_client(engine), providers[engine]["model"],
                        build_dataset_summary(df), insights,
                        business_context(),
                    )
                st.rerun()
            except Exception as exc:
                st.error(f"Briefing indisponible : {exc}")
    else:
        st.html('<div class="vd-kicker" style="margin-top:22px">Briefing de l\'assistant</div>')
        st.html(f'<div class="vd-answer">{st.session_state[_brief_key]}</div>')

tabs = st.tabs(["Aperçu", "Qualité", "Stats", "Graphiques",
                "Prédire", "Assistant"])

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
            options += ["Série temporelle", "Projection"]
        measures = rank_measures(df)
        ignored = [c for c in numeric_cols if c not in measures]
        chart_type = st.radio("Type de graphique", options, horizontal=True,
                              label_visibility="collapsed")
        if ignored:
            st.caption(
                "Colonnes écartées par défaut car ce sont des identifiants : "
                + ", ".join(ignored) + "."
            )
        st.html('<hr class="vd-rule" style="margin:14px 0 20px">')
        controls, chart = st.columns([1, 2.4], gap="large")

        if chart_type == "Histogramme":
            with controls:
                x = st.selectbox("Variable", measures + ignored)
                bins = st.slider("Nombre de classes", 5, 100, 30, step=5)
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
                    x = st.selectbox("Axe X", measures + ignored, key="scatter_x")
                    y = st.selectbox("Axe Y", measures + ignored, index=1, key="scatter_y")
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
                y = st.selectbox("Variable numérique", measures + ignored, key="box_y")
                category = st.selectbox("Catégorie", ["Aucune"] + [c for c in all_cols if c != y])
            with chart:
                fig = px.box(df, x=None if category == "Aucune" else category, y=y, points="outliers")
                st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Projection":
            with controls:
                date_col = st.selectbox("Date", date_cols, key="fc_date")
                value_col = st.selectbox("Mesure", measures, key="fc_value")
                horizon = st.slider("Mois à projeter", 1, 12, 3)
            observed, projection = forecast_series(df, date_col, value_col, horizon)
            with chart:
                if observed is None:
                    st.info("Il faut au moins quatre mois de données pour projeter une tendance.")
                else:
                    fig = go.Figure()
                    fig.add_scatter(
                        x=observed.index, y=observed.values, mode="lines+markers",
                        name="Observé", line=dict(color=INDIGO, width=2.5),
                    )
                    fig.add_scatter(
                        x=[observed.index[-1]] + list(projection.index),
                        y=[observed.iloc[-1]] + list(projection.values),
                        mode="lines+markers", name="Projection",
                        line=dict(color=ORANGE, width=2.5, dash="dot"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    total = projection.sum()
                    st.caption(
                        f"Projection linéaire sur {horizon} mois : {total:,.0f} au total, "
                        f"soit {projection.mean():,.0f} par mois en moyenne. "
                        "Tendance calculée sur l'historique disponible, hors saisonnalité "
                        "et hors événement exceptionnel.".replace(",", " ")
                    )

        else:
            with controls:
                date_col = st.selectbox("Date", date_cols)
                value_col = st.selectbox("Mesure", measures)
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

# ── Prédiction ───────────────────────────────────────────────────────────────
with tabs[4]:
    targets = modelable_targets(df)
    if not targets:
        st.info(
            "Aucune colonne de ce fichier ne se prête à une prédiction : il faut une "
            "mesure chiffrée ou une catégorie à deux à douze valeurs, renseignée sur "
            "au moins 60 % des lignes."
        )
    else:
        proposed = suggest_target(df) or targets[0]
        st.markdown("#### Que voulez-vous estimer ?")
        st.caption(
            f"L'application propose « {proposed} ». Changez-la si une autre colonne "
            "vous intéresse davantage."
        )
        choice, action = st.columns([2, 1], gap="large")
        with choice:
            target = st.selectbox(
                "Colonne à estimer", targets, index=targets.index(proposed),
                label_visibility="collapsed",
            )
        with action:
            launch = st.button("Lancer l'analyse", type="primary", use_container_width=True)

        state_key = f"vd_model::{uploaded_file.name}::{target}"
        if launch:
            with st.spinner("Apprentissage sur votre historique…"):
                st.session_state[state_key] = train_model(df, target)

        outcome = st.session_state.get(state_key)
        if outcome and outcome.get("error"):
            st.warning(outcome["error"])
        elif outcome:
            label, sentence = reliability_label(
                outcome["score"], outcome["classification"], outcome.get("baseline", 0.0)
            )
            outcome["label"], outcome["sentence"] = label, sentence

            st.html('<hr class="vd-rule">')
            k1, k2, k3 = st.columns(3, gap="small")
            k1.metric("Fiabilité", label)
            if outcome["classification"]:
                k2.metric("Cas correctement retrouvés", f"{outcome['score'] * 100:.0f} %")
                k3.metric("Catégories", len(outcome["classes"]))
            else:
                k2.metric("Écart moyen", f"{outcome['mae']:,.0f}".replace(",", " "))
                k3.metric("Valeur moyenne", f"{outcome['moyenne']:,.0f}".replace(",", " "))
            st.caption(
                f"{sentence} Modèle appris sur {outcome['n_train']} lignes et vérifié "
                f"sur {outcome['n_test']} lignes jamais vues."
            )

            if engine in providers:
                explain_key = state_key + "::texte"
                if explain_key not in st.session_state:
                    if st.button("Lire la conclusion de l'assistant"):
                        try:
                            with st.spinner("Rédaction…"):
                                stream = explain_model(
                                    make_client(engine), providers[engine]["model"],
                                    outcome, business_context(),
                                )
                                st.session_state[explain_key] = st.write_stream(
                                    chunk.choices[0].delta.content or "" for chunk in stream
                                )
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Conclusion indisponible : {exc}")
                else:
                    st.html(f'<div class="vd-answer">{st.session_state[explain_key]}</div>')

            st.html('<hr class="vd-rule">')
            weight_col, chart_col = st.columns([1, 1.3], gap="large")
            with weight_col:
                st.markdown("#### Ce qui pèse le plus")
                weights = (outcome["importance"] / outcome["importance"].sum() * 100).round(1)
                for name, value in weights.items():
                    alert = " alert" if value == weights.max() else ""
                    st.html(
                        f'<div class="vd-bar-label"><span>{name}</span>'
                        f'<span style="color:{MUTED}">{value} %</span></div>'
                        f'<div class="vd-bar{alert}"><div style="width:{value / weights.max() * 100:.0f}%"></div></div>'
                        '<div style="height:12px"></div>'
                    )
            with chart_col:
                if outcome["classification"]:
                    st.markdown("#### Répartition des estimations")
                    counts = outcome["risk"]["prédit"].value_counts().reset_index()
                    counts.columns = ["catégorie", "lignes"]
                    fig = px.bar(counts, x="catégorie", y="lignes")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown("#### Prédit contre réel")
                    comparison = outcome["comparison"]
                    fig = px.scatter(comparison, x="réel", y="prédit", opacity=0.7)
                    low = float(min(comparison["réel"].min(), comparison["prédit"].min()))
                    high = float(max(comparison["réel"].max(), comparison["prédit"].max()))
                    fig.add_shape(type="line", x0=low, y0=low, x1=high, y1=high,
                                  line=dict(color=ORANGE, width=2, dash="dot"))
                    st.plotly_chart(fig, use_container_width=True)

            st.html('<hr class="vd-rule">')
            st.markdown("#### Lignes à regarder en priorité")
            st.caption(
                "Les cas où le modèle hésite le plus."
                if outcome["classification"] else
                "Les cas où l'écart entre estimation et réalité est le plus fort."
            )
            st.dataframe(outcome["risk"].head(20), use_container_width=True, hide_index=True)
        else:
            st.caption(
                "Rien n'est calculé tant que vous ne lancez pas l'analyse : "
                "l'apprentissage prend quelques secondes."
            )

# ── Assistant IA ─────────────────────────────────────────────────────────────
with tabs[5]:
    history = st.session_state.setdefault("vd_history", [])
    summary = build_dataset_summary(df)
    use_ai = engine in providers
    context = business_context()

    left, right = st.columns([1.6, 1], gap="large")

    with right:
        st.html('<div class="vd-kicker">Questions suggérées</div>')
        for index, suggestion in enumerate(SUGGESTIONS):
            if st.button(suggestion, key=f"sugg_{index}", use_container_width=True):
                st.session_state["vd_pending"] = suggestion
        st.html('<hr class="vd-rule">')
        if use_ai and compute_mode:
            st.caption(
                f"{engine} · {providers[engine]['model']} — mode calcul exact. "
                "L'assistant écrit une requête, elle est exécutée sur votre fichier, "
                "et la réponse commente le résultat réel. Le code est vérifié avant "
                "exécution et ne peut ni écrire de fichier ni accéder au réseau."
            )
        elif use_ai:
            st.caption(
                f"{engine} · {providers[engine]['model']}. L'assistant ne reçoit qu'un résumé "
                "statistique et un échantillon de 12 lignes — jamais le fichier complet."
            )
        else:
            st.caption(
                "Analyse locale : les réponses sont calculées à partir de vos statistiques, "
                "sans appel externe. Ajoutez une clé IA pour une lecture rédigée."
            )
        if context:
            st.caption("Contexte métier pris en compte.")
        if history and st.button("Effacer la conversation"):
            st.session_state["vd_history"] = []
            st.rerun()

    with left:
        st.markdown("#### Interroger les données")

        if not context and not st.session_state.get("vd_context_dismissed"):
            st.html(
                '<div class="vd-answer"><b style="font-weight:800">Pour de meilleures '
                'réponses</b><br>Décrivez votre activité en deux phrases. L\'assistant '
                'interprétera vos chiffres au lieu de les décrire.</div>'
            )
            invite, dismiss = st.columns([2, 1], gap="small")
            with invite:
                with st.popover("Ajouter le contexte", use_container_width=True):
                    st.text_area(
                        "Décrivez votre activité en deux phrases",
                        placeholder="Ex. : distributeur de matériaux, 3 agences, saison "
                                    "haute de mars à juin. Le canal revendeur est "
                                    "prioritaire cette année.",
                        height=140,
                        key="vd_context_inline",
                    )
            with dismiss:
                if st.button("Plus tard", use_container_width=True):
                    st.session_state["vd_context_dismissed"] = True
                    st.rerun()

        for message in history:
            if message["role"] == "user":
                st.markdown(f"**Question —** {message['content']}")
            else:
                st.markdown(message["content"])
                if message.get("code"):
                    with st.expander("Voir le calcul effectué"):
                        st.code(message["code"], language="python")

        question = st.chat_input("Posez une question sur vos données…")
        pending = st.session_state.pop("vd_pending", None)
        question = question or pending

        if question:
            st.markdown(f"**Question —** {question}")
            history.append({"role": "user", "content": question})

            if use_ai and ai_quota_left() <= 0:
                st.warning(
                    f"Limite de {MAX_AI_QUESTIONS} questions atteinte pour cette session. "
                    "Rechargez la page pour repartir, ou utilisez l'analyse locale."
                )
                use_ai = False

            if use_ai and compute_mode:
                consume_ai_quota()
                client, model = make_client(engine), providers[engine]["model"]
                try:
                    with st.spinner("Calcul sur vos données…"):
                        code = generate_code(client, model, question, df)
                        result, fig, error = run_code(code, df)

                    if error:
                        st.warning(f"Le calcul n'a pas abouti ({error}). Réponse sur le résumé statistique.")
                        with st.spinner("Analyse en cours…"):
                            stream = ask_assistant(client, model, question, summary, history[:-1])
                            answer = st.write_stream(
                                chunk.choices[0].delta.content or "" for chunk in stream
                            )
                        history.append({"role": "assistant", "content": answer})
                    else:
                        if isinstance(result, (pd.DataFrame, pd.Series)) and len(result) > 1:
                            st.dataframe(
                                result.head(50) if isinstance(result, pd.DataFrame)
                                else result.head(50).to_frame(),
                                use_container_width=True,
                            )
                        if fig is not None:
                            st.plotly_chart(fig, use_container_width=True)
                        with st.spinner("Rédaction…"):
                            stream = comment_result(client, model, question, code, result, context)
                            answer = st.write_stream(
                                chunk.choices[0].delta.content or "" for chunk in stream
                            )
                        with st.expander("Voir le calcul effectué"):
                            st.code(code, language="python")
                        history.append({"role": "assistant", "content": answer, "code": code})
                except Exception as exc:
                    history.pop()
                    st.error(f"Impossible d'obtenir l'analyse via {engine} : {exc}")

            elif use_ai:
                consume_ai_quota()
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

        if history and history[-1]["role"] == "assistant":
            rated_key = f"vd_rated::{len(history)}"
            if not st.session_state.get(rated_key):
                st.caption("Cette réponse vous a-t-elle aidé ?")
                yes, no, _ = st.columns([1, 1, 3], gap="small")
                with yes:
                    if st.button("Oui", use_container_width=True, key=f"up::{len(history)}"):
                        record_feedback("réponse utile", history[-2]["content"][:300])
                        st.session_state[rated_key] = True
                        st.rerun()
                with no:
                    if st.button("Non", use_container_width=True, key=f"down::{len(history)}"):
                        record_feedback("réponse inutile", history[-2]["content"][:300],
                                        history[-1]["content"][:500])
                        st.session_state[rated_key] = True
                        st.rerun()
            else:
                st.caption("Merci, c'est noté.")

st.html('<hr class="vd-rule">')

if not st.session_state.get("vd_session_feedback"):
    st.html('<div class="vd-kicker">Votre avis</div>')
    st.markdown("#### Qu'est-ce qui vous manque ?")
    st.caption(
        "Une phrase suffit. C'est ce qui décide des prochaines améliorations."
    )
    remark = st.text_area(
        "Votre remarque", height=90, label_visibility="collapsed",
        placeholder="Ex. : j'aimerais comparer deux fichiers, ou exporter en Excel.",
        key="vd_remark",
    )
    send_col, skip_col, _ = st.columns([1, 1, 2], gap="small")
    with send_col:
        if st.button("Envoyer", type="primary", use_container_width=True):
            if remark.strip():
                record_feedback("remarque", remark.strip(),
                                f"fichier {uploaded_file.name}")
                st.session_state["vd_session_feedback"] = True
                st.rerun()
            else:
                st.caption("Écrivez d'abord une phrase.")
    with skip_col:
        if st.button("Plus tard", use_container_width=True):
            st.session_state["vd_session_feedback"] = True
            st.rerun()
else:
    st.caption("Merci pour votre retour.")

with st.expander("Nouveautés"):
    st.markdown(
        "**Août 2026**\n"
        "- Prédiction : estimez une valeur ou une catégorie, avec les variables qui pèsent le plus.\n"
        "- Calcul exact : l'assistant exécute une requête sur votre fichier avant de répondre.\n"
        "- Nettoyage automatique des exports bruts : en-tête réel, lignes vides, cellules fusionnées.\n"
        "- Jeux de données d'exemple, thème sombre, application utilisable sur téléphone.\n"
        "- Projection à trois mois sur les séries temporelles.\n"
        "\n**À venir**\n"
        "- Comparaison de deux fichiers, segmentation automatique, export du rapport en PDF."
    )
    st.caption("Une idée, un problème ? Écrivez à mdjoman@upb.ci.")

st.caption("VisualizeData Assistant · build modernist-20")
