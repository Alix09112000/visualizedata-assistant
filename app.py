"""
VisualizeData Assistant — v2.0
Design premium + GPT-4 + Nouveaux modules
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisualizeData Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE COULEURS ───────────────────────────────────────────
COLORS = {
    'primary': '#5B4EFF',
    'secondary': '#FF6B35',
    'green': '#00D4AA',
    'navy': '#08102B',
    'dark': '#1C2640',
    'light': '#F8FAFF',
    'gray': '#8892A4',
    'white': '#FFFFFF',
    'red': '#EF4444',
    'yellow': '#F59E0B',
}

CHART_COLORS = ['#5B4EFF','#FF6B35','#00D4AA','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#84CC16']

# ── CSS PREMIUM ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

* { font-family: 'Plus Jakarta Sans', sans-serif !important; }
h1,h2,h3,h4 { font-family: 'Outfit', sans-serif !important; }

.stApp { background: #F0F4FF; }
section[data-testid="stSidebar"] { background: #08102B !important; border-right: 1px solid rgba(91,78,255,0.2); }
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.7) !important; font-size: 13px !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] { background: rgba(91,78,255,0.1) !important; border: 1.5px dashed rgba(91,78,255,0.4) !important; border-radius: 12px !important; }

/* Header */
.vda-hero {
    background: linear-gradient(135deg, #08102B 0%, #1C2640 50%, #0D1A3A 100%);
    border-radius: 20px; padding: 28px 32px; margin-bottom: 20px;
    border: 1px solid rgba(91,78,255,0.25);
    box-shadow: 0 20px 60px rgba(8,16,43,0.3);
    position: relative; overflow: hidden;
}
.vda-hero::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px; border-radius: 50%;
    background: radial-gradient(circle, rgba(91,78,255,0.2), transparent);
}
.vda-hero::after {
    content: ''; position: absolute; bottom: -40px; left: 30%;
    width: 150px; height: 150px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,107,53,0.1), transparent);
}
.hero-title { font-family: 'Outfit', sans-serif !important; font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin: 0; }
.hero-sub { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 4px; }
.hero-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(91,78,255,0.2); border: 1px solid rgba(91,78,255,0.4); color: #A5B4FC; padding: 4px 12px; border-radius: 100px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-left: auto; }

/* KPI Cards */
.kpi-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi-card {
    background: #fff; border-radius: 14px; padding: 18px 16px;
    border: 1.5px solid #E2E8F0; border-top: 3px solid;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.kpi-icon { font-size: 22px; margin-bottom: 8px; }
.kpi-value { font-family: 'Outfit', sans-serif !important; font-size: 26px; font-weight: 800; letter-spacing: -1px; color: #08102B; }
.kpi-label { font-size: 11px; color: #8892A4; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px; }

/* Cards génériques */
.card {
    background: #fff; border-radius: 16px; padding: 22px;
    border: 1.5px solid #E2E8F0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}
.card-title { font-family: 'Outfit', sans-serif !important; font-size: 15px; font-weight: 700; color: #08102B; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }

/* Insight boxes */
.insight-box { background: #EEF4FF; border-left: 4px solid #5B4EFF; border-radius: 10px; padding: 13px 16px; margin: 8px 0; font-size: 13px; color: #1C2640; line-height: 1.6; }
.warning-box { background: #FFF7ED; border-left: 4px solid #F59E0B; border-radius: 10px; padding: 13px 16px; margin: 8px 0; font-size: 13px; color: #1C2640; }
.error-box { background: #FFF1F2; border-left: 4px solid #EF4444; border-radius: 10px; padding: 13px 16px; margin: 8px 0; font-size: 13px; color: #1C2640; }
.success-box { background: #F0FDF4; border-left: 4px solid #00D4AA; border-radius: 10px; padding: 13px 16px; margin: 8px 0; font-size: 13px; color: #1C2640; }

/* Chat */
.chat-container { max-height: 420px; overflow-y: auto; padding: 10px 0; }
.msg-user { display: flex; justify-content: flex-end; margin: 8px 0; }
.msg-user-bubble { background: linear-gradient(135deg, #5B4EFF, #7C6FFF); color: #fff; border-radius: 16px 16px 4px 16px; padding: 12px 16px; max-width: 75%; font-size: 13px; line-height: 1.6; box-shadow: 0 4px 12px rgba(91,78,255,0.3); }
.msg-ai { display: flex; gap: 10px; margin: 8px 0; align-items: flex-start; }
.msg-ai-avatar { width: 32px; height: 32px; min-width: 32px; border-radius: 50%; background: linear-gradient(135deg, #5B4EFF, #FF6B35); display: flex; align-items: center; justify-content: center; font-size: 14px; }
.msg-ai-bubble { background: #fff; border: 1.5px solid #E2E8F0; border-radius: 4px 16px 16px 16px; padding: 12px 16px; max-width: 80%; font-size: 13px; line-height: 1.7; color: #1C2640; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.msg-label { font-size: 10px; color: #8892A4; margin-bottom: 3px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }

/* Suggestion chips */
.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.chip { background: #EEF4FF; border: 1px solid rgba(91,78,255,0.2); color: #5B4EFF; border-radius: 100px; padding: 6px 14px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.chip:hover { background: #5B4EFF; color: #fff; }

/* Score gauge */
.score-container { text-align: center; padding: 16px; }
.score-value { font-family: 'Outfit', sans-serif !important; font-size: 52px; font-weight: 900; letter-spacing: -2px; }
.score-label { font-size: 13px; color: #8892A4; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

/* Section header */
.section-hd { font-family: 'Outfit', sans-serif !important; font-size: 14px; font-weight: 700; color: #08102B; margin: 20px 0 10px; display: flex; align-items: center; gap: 8px; padding-bottom: 8px; border-bottom: 2px solid #F0F4FF; }

/* Progress bars */
.progress-bar { background: #F0F4FF; border-radius: 100px; height: 8px; overflow: hidden; margin-top: 4px; }
.progress-fill { height: 100%; border-radius: 100px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #F0F4FF; border-radius: 12px; padding: 4px; gap: 3px; }
.stTabs [data-baseweb="tab"] { border-radius: 9px; padding: 8px 16px; font-size: 13px; font-weight: 600; color: #8892A4 !important; border: none !important; }
.stTabs [aria-selected="true"] { background: #fff !important; color: #5B4EFF !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }

/* Buttons */
.stButton > button { border-radius: 10px !important; font-weight: 700 !important; font-size: 13px !important; transition: all 0.25s !important; border: none !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #5B4EFF, #7C6FFF) !important; box-shadow: 0 4px 16px rgba(91,78,255,0.35) !important; }
.stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(91,78,255,0.45) !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0; }

/* Metrics */
[data-testid="metric-container"] { background: #fff; border: 1.5px solid #E2E8F0; border-radius: 12px; padding: 14px !important; }

/* Hide defaults */
#MainMenu, footer, .stDeployButton { visibility: hidden; }

/* Sidebar styling */
.sidebar-logo { padding: 16px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.sidebar-logo-title { font-family: 'Outfit', sans-serif !important; font-size: 18px; font-weight: 800; color: #fff !important; letter-spacing: -0.3px; }
.sidebar-logo-sub { font-size: 11px; color: rgba(255,255,255,0.4) !important; }
.sidebar-section { font-size: 10px; font-weight: 800; color: rgba(255,255,255,0.35) !important; text-transform: uppercase; letter-spacing: 1px; padding: 12px 0 6px; }

/* Upload zone */
[data-testid="stFileUploader"] label { color: rgba(255,255,255,0.7) !important; font-size: 13px !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F0F4FF; }
::-webkit-scrollbar-thumb { background: #5B4EFF; border-radius: 3px; }

/* Welcome screen */
.welcome-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; }
.welcome-card { background: #fff; border: 1.5px solid #E2E8F0; border-radius: 16px; padding: 24px 20px; border-top: 3px solid; transition: all 0.3s; }
.welcome-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,0.08); }
.welcome-icon { font-size: 30px; margin-bottom: 12px; }
.welcome-title { font-family: 'Outfit', sans-serif !important; font-size: 15px; font-weight: 700; color: #08102B; margin-bottom: 6px; }
.welcome-desc { font-size: 12px; color: #8892A4; line-height: 1.6; }

/* Anomaly item */
.anomaly-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 14px; background: #fff; border: 1px solid #E2E8F0; border-radius: 10px; margin: 6px 0; }
.anomaly-icon { font-size: 18px; min-width: 24px; }
.anomaly-title { font-size: 13px; font-weight: 600; color: #08102B; }
.anomaly-desc { font-size: 12px; color: #8892A4; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ── FONCTIONS ──────────────────────────────────────────────────

@st.cache_data
def load_data(file_bytes, file_name):
    try:
        if file_name.endswith('.csv'):
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=sep)
                        if df.shape[1] > 1:
                            return df, None
                    except: continue
            return pd.read_csv(io.BytesIO(file_bytes)), None
        elif file_name.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(io.BytesIO(file_bytes))
            sheets = xl.sheet_names
            return xl.parse(sheets[0]), sheets
    except Exception as e:
        return None, str(e)


def clean_dataframe(df):
    """Nettoyage basique du dataframe"""
    df = df.copy()
    # Supprimer lignes complètement vides
    df = df.dropna(how='all')
    # Supprimer colonnes complètement vides
    df = df.dropna(axis=1, how='all')
    # Nettoyer noms de colonnes
    df.columns = [str(c).strip() for c in df.columns]
    return df


def data_audit(df):
    total = len(df)
    total_cells = total * len(df.columns)
    missing = df.isnull().sum()
    missing_dict = missing[missing > 0].to_dict()
    missing_pct = {k: round(v/total*100, 1) for k,v in missing_dict.items()}
    completeness = round((1 - df.isnull().sum().sum() / total_cells) * 100, 1) if total_cells > 0 else 100
    duplicates = df.duplicated().sum()

    num_cols = df.select_dtypes(include=[np.number]).columns
    outliers = {}
    for col in num_cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR > 0:
            n = ((df[col] < Q1-1.5*IQR) | (df[col] > Q3+1.5*IQR)).sum()
            if n > 0:
                outliers[col] = {'count': int(n), 'pct': round(n/total*100, 1)}

    score = completeness
    if duplicates > 0: score -= min(10, round(duplicates/total*100))
    if outliers: score -= min(15, len(outliers)*3)
    score = max(0, round(score))

    return {
        'total_rows': total, 'total_cols': len(df.columns),
        'completeness': completeness, 'missing': missing_dict,
        'missing_pct': missing_pct, 'duplicates': int(duplicates),
        'dup_pct': round(duplicates/total*100, 1) if total > 0 else 0,
        'outliers': outliers, 'quality_score': score
    }


def smart_analytics(df):
    results = {}
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    if num_cols:
        results['stats'] = df[num_cols].describe().round(2)

    if len(num_cols) >= 2:
        corr = df[num_cols].corr().round(3)
        results['corr'] = corr
        strong = []
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                v = corr.iloc[i,j]
                if abs(v) > 0.6:
                    strong.append({'c1': corr.columns[i], 'c2': corr.columns[j], 'v': round(v,3)})
        results['strong_corr'] = strong

    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        try:
            grp = df.groupby(cat)[num].agg(['sum','mean','count']).round(2)
            grp.columns = ['Total','Moyenne','Nb']
            results['group'] = grp.sort_values('Total', ascending=False).head(15)
            results['group_cat'] = cat
            results['group_num'] = num
        except: pass

    return results


def generate_insights(df, audit, analytics):
    insights, warnings, errors = [], [], []
    score = audit['quality_score']

    if score >= 85:
        insights.append(f"✅ Excellent score de qualité ({score}/100) — vos données sont fiables pour l'analyse.")
    elif score >= 65:
        warnings.append(f"⚠️ Score de qualité moyen ({score}/100) — quelques améliorations recommandées avant analyse.")
    else:
        errors.append(f"🚨 Score de qualité insuffisant ({score}/100) — les résultats peuvent être biaisés.")

    if audit['duplicates'] > 0:
        errors.append(f"🔴 {audit['duplicates']} ligne(s) en double ({audit['dup_pct']}%) — à supprimer avant analyse.")

    if audit['missing']:
        top = max(audit['missing_pct'], key=audit['missing_pct'].get)
        pct = audit['missing_pct'][top]
        if pct > 20:
            errors.append(f"🔴 '{top}' a {pct}% de valeurs manquantes — impact majeur sur les analyses.")
        elif pct > 5:
            warnings.append(f"🟡 '{top}' a {pct}% de valeurs manquantes — à traiter avant analyse.")

    if audit['outliers']:
        for col, info in list(audit['outliers'].items())[:2]:
            warnings.append(f"📍 {info['count']} valeur(s) aberrante(s) dans '{col}' ({info['pct']}%).")

    if 'strong_corr' in analytics:
        for sc in analytics['strong_corr'][:2]:
            direction = "positive 📈" if sc['v'] > 0 else "négative 📉"
            insights.append(f"🔗 '{sc['c1']}' et '{sc['c2']}' sont fortement corrélées ({direction}, r={sc['v']}).")

    if 'group' in analytics:
        grp = analytics['group']
        top_item = grp.index[0]
        top_pct = round(grp['Total'].iloc[0] / grp['Total'].sum() * 100, 1)
        insights.append(f"🏆 '{top_item}' est le leader avec {top_pct}% du total de '{analytics['group_num']}'.")

    return insights, warnings, errors


def ai_response(question, df):
    q = question.lower().strip()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    total = len(df)

    # Top / Meilleur
    if any(w in q for w in ['top','meilleur','plus grand','maximum','premier','classement']):
        n = 5
        for word in q.split():
            if word.isdigit(): n = int(word); break
        if num_cols and cat_cols:
            cat, num = cat_cols[0], num_cols[0]
            top = df.groupby(cat)[num].sum().sort_values(ascending=False).head(n)
            r = f"**🏆 Top {n} — {cat} par {num} :**\n\n"
            for i,(k,v) in enumerate(top.items(),1):
                bar = "█" * int(v/top.max()*10)
                r += f"**{i}. {k}** : {v:,.0f} {bar}\n"
            r += f"\n💡 *{top.index[0]}* représente **{round(top.iloc[0]/top.sum()*100,1)}%** du total."
            return r

    # Moyenne
    elif any(w in q for w in ['moyenne','moyen','moy','average']):
        if num_cols:
            r = "**📊 Moyennes :**\n\n"
            for col in num_cols[:6]:
                v = df[col].mean()
                r += f"• **{col}** : {v:,.2f}\n"
            return r

    # Total / Somme
    elif any(w in q for w in ['total','somme','sum','cumul']):
        if num_cols:
            r = "**💰 Totaux :**\n\n"
            for col in num_cols[:6]:
                r += f"• **{col}** : {df[col].sum():,.0f}\n"
            return r

    # Manquants
    elif any(w in q for w in ['manquant','vide','null','missing','incomplet']):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            return "✅ **Aucune valeur manquante** dans vos données !"
        r = f"**⚠️ {len(missing)} colonne(s) avec des valeurs manquantes :**\n\n"
        for col, n in missing.items():
            pct = round(n/total*100,1)
            r += f"• **{col}** : {n} valeurs manquantes ({pct}%)\n"
        return r

    # Doublons
    elif any(w in q for w in ['doublon','duplicate','répété','double']):
        n = df.duplicated().sum()
        if n == 0:
            return "✅ **Aucun doublon** dans vos données !"
        return f"⚠️ **{n} ligne(s) en double** ({round(n/total*100,1)}%). Recommandation : supprimez-les avant l'analyse."

    # Résumé
    elif any(w in q for w in ['résumé','résume','synthèse','overview','analyse','bilan']):
        num_s = f"{len(num_cols)} num." if num_cols else "aucune num."
        cat_s = f"{len(cat_cols)} cat." if cat_cols else "aucune cat."
        comp = round((1-df.isnull().sum().sum()/(total*len(df.columns)))*100,1)
        return f"""**📊 Résumé de vos données :**

• **Taille** : {total:,} lignes × {len(df.columns)} colonnes
• **Variables** : {num_s}, {cat_s}
• **Complétude** : {comp}%
• **Doublons** : {df.duplicated().sum()}

**Colonnes numériques** : {', '.join(num_cols[:5]) if num_cols else 'Aucune'}
**Colonnes texte** : {', '.join(cat_cols[:5]) if cat_cols else 'Aucune'}

💡 Posez des questions plus précises : *"Top 5 par ventes"*, *"Moyenne de X"*, *"Y a-t-il des anomalies ?"*"""

    # Corrélation
    elif any(w in q for w in ['corrél','lien','relation','impact']):
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            strong = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    v = corr.iloc[i,j]
                    if abs(v) > 0.5:
                        strong.append((corr.columns[i], corr.columns[j], round(v,3)))
            if strong:
                r = "**🔗 Corrélations fortes :**\n\n"
                for c1,c2,v in strong[:5]:
                    typ = "positive 📈" if v>0 else "négative 📉"
                    r += f"• **{c1}** ↔ **{c2}** : {typ} (r={v})\n"
                return r
            return "ℹ️ Aucune corrélation forte (>0.5) détectée entre vos variables."
        return "⚠️ Besoin d'au moins 2 colonnes numériques."

    # Min / Max
    elif any(w in q for w in ['minimum','min','plus petit','plus faible']):
        if num_cols:
            r = "**📉 Valeurs minimales :**\n\n"
            for col in num_cols[:5]:
                r += f"• **{col}** : {df[col].min():,.2f}\n"
            return r
    elif any(w in q for w in ['maximum','max','plus élevé','plus grand']):
        if num_cols:
            r = "**📈 Valeurs maximales :**\n\n"
            for col in num_cols[:5]:
                r += f"• **{col}** : {df[col].max():,.2f}\n"
            return r

    # Taille
    elif any(w in q for w in ['taille','dimension','lignes','colonnes','shape']):
        return f"**📋 Dimensions :**\n\n• **{total:,} lignes** × **{len(df.columns)} colonnes**\n• Total : **{total*len(df.columns):,} cellules**\n• Colonnes : {', '.join(df.columns.tolist()[:8])}{'...' if len(df.columns)>8 else ''}"

    # Anomalie
    elif any(w in q for w in ['anomalie','aberrant','outlier','bizarre','erreur']):
        num_cols_df = df.select_dtypes(include=[np.number]).columns
        anomalies = []
        for col in num_cols_df:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3-Q1
            if IQR > 0:
                n = ((df[col]<Q1-1.5*IQR)|(df[col]>Q3+1.5*IQR)).sum()
                if n > 0:
                    anomalies.append(f"• **{col}** : {n} valeur(s) aberrante(s)")
        if anomalies:
            return "**🔍 Anomalies détectées :**\n\n" + "\n".join(anomalies)
        return "✅ Aucune valeur aberrante détectée dans vos données numériques."

    # Par défaut
    return f"""🤖 Je n'ai pas compris précisément cette question.

**Essayez ces formulations :**
• *"Quels sont les top 5 [élément] par [valeur] ?"*
• *"Quelle est la moyenne / le total de [colonne] ?"*
• *"Y a-t-il des valeurs manquantes / doublons / anomalies ?"*
• *"Donne-moi un résumé complet"*
• *"Montre-moi les corrélations"*

**Colonnes disponibles :** {', '.join(df.columns.tolist()[:8])}{'...' if len(df.columns)>8 else ''}"""


def create_charts(df):
    charts = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    layout_base = dict(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Plus Jakarta Sans', color='#08102B', size=11),
        title_font=dict(family='Outfit', size=14, color='#08102B'),
        margin=dict(t=40, b=30, l=20, r=20),
        xaxis=dict(gridcolor='#F0F4FF', linecolor='#E2E8F0'),
        yaxis=dict(gridcolor='#F0F4FF', linecolor='#E2E8F0'),
    )

    # 1. Barres
    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        try:
            agg = df.groupby(cat)[num].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(agg, x=cat, y=num, title=f"📊 {num} par {cat}",
                        color_discrete_sequence=[COLORS['primary']])
            fig.update_layout(**layout_base)
            fig.update_traces(marker_line_width=0, opacity=0.9)
            charts.append(('bar', fig))
        except: pass

    # 2. Distribution
    if num_cols:
        col = num_cols[0]
        fig = px.histogram(df, x=col, nbins=25, title=f"📈 Distribution — {col}",
                          color_discrete_sequence=[COLORS['secondary']])
        fig.update_layout(**layout_base)
        fig.update_traces(marker_line_width=0, opacity=0.85)
        charts.append(('hist', fig))

    # 3. Scatter
    if len(num_cols) >= 2:
        x, y = num_cols[0], num_cols[1]
        color = cat_cols[0] if cat_cols else None
        fig = px.scatter(df, x=x, y=y, color=color, title=f"🔵 {x} vs {y}",
                        color_discrete_sequence=CHART_COLORS, opacity=0.7)
        fig.update_layout(**layout_base)
        charts.append(('scatter', fig))

    # 4. Camembert
    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        try:
            pie_data = df.groupby(cat)[num].sum().sort_values(ascending=False).head(7)
            fig = px.pie(values=pie_data.values, names=pie_data.index,
                        title=f"🥧 Répartition {num}", color_discrete_sequence=CHART_COLORS,
                        hole=0.4)
            fig.update_layout(paper_bgcolor='white', font=dict(family='Plus Jakarta Sans'),
                            title_font=dict(family='Outfit', size=14), margin=dict(t=40,b=20))
            fig.update_traces(textposition='inside', textinfo='percent+label')
            charts.append(('pie', fig))
        except: pass

    # 5. Heatmap corrélations
    if len(num_cols) >= 3:
        corr = df[num_cols[:8]].corr().round(2)
        fig = px.imshow(corr, text_auto=True, title="🔥 Carte de corrélations",
                       color_continuous_scale=['#FF6B35','white','#5B4EFF'], zmin=-1, zmax=1)
        fig.update_layout(paper_bgcolor='white', font=dict(family='Plus Jakarta Sans'),
                         title_font=dict(family='Outfit', size=14), margin=dict(t=40,b=20))
        charts.append(('heatmap', fig))

    # 6. Box plot
    if num_cols:
        fig = go.Figure()
        for i, col in enumerate(num_cols[:5]):
            fig.add_trace(go.Box(y=df[col], name=col, marker_color=CHART_COLORS[i%len(CHART_COLORS)],
                               boxpoints='outliers', jitter=0.3))
        fig.update_layout(title="📦 Distribution & Outliers", **layout_base)
        charts.append(('box', fig))

    return charts


# ── MAIN ───────────────────────────────────────────────────────
def main():

    # ── SIDEBAR ────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span style="font-size:28px">📊</span>
                <div>
                    <div class="sidebar-logo-title">VisualizeData</div>
                    <div class="sidebar-logo-sub">Assistant IA v2.0</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">Modules</div>', unsafe_allow_html=True)
        module = st.radio("", [
            "🏠  Accueil",
            "🔍  Data Audit",
            "📊  Smart Analytics",
            "🎨  Dashboards",
            "💬  AI Chat",
            "📄  Rapport",
        ], label_visibility="collapsed")

        st.markdown('<div class="sidebar-section">Import données</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=['csv','xlsx','xls'], label_visibility="collapsed",
                                    help="CSV, Excel jusqu'à 200MB")
        if uploaded:
            st.success(f"✅ {uploaded.name[:25]}...")
            st.caption(f"{uploaded.size/1024:.1f} KB")

        st.markdown("---")
        st.markdown("""
        <div style="padding:8px 0">
            <div style="font-size:11px;color:rgba(255,255,255,0.3);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.8px">À propos</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.5);line-height:1.6">
                VisualizeData Assistant<br>
                <span style="color:#5B4EFF">service@visualizedatacom.com</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── ÉTAT ───────────────────────────────────────────────────
    for key in ['df','audit','analytics','chat','file_name']:
        if key not in st.session_state:
            st.session_state[key] = None if key != 'chat' else []

    # ── CHARGEMENT ─────────────────────────────────────────────
    if uploaded and (st.session_state.file_name != uploaded.name):
        with st.spinner("⚡ Analyse en cours..."):
            df_raw, err = load_data(uploaded.getvalue(), uploaded.name)
            if df_raw is not None:
                df = clean_dataframe(df_raw)
                st.session_state.df = df
                st.session_state.audit = data_audit(df)
                st.session_state.analytics = smart_analytics(df)
                st.session_state.file_name = uploaded.name
                st.session_state.chat = []

    df = st.session_state.df
    audit = st.session_state.audit
    analytics = st.session_state.analytics

    # ── HEADER ─────────────────────────────────────────────────
    if df is not None:
        score = audit['quality_score']
        score_color = COLORS['green'] if score >= 85 else COLORS['yellow'] if score >= 65 else COLORS['red']
        score_label = "Excellent" if score >= 85 else "Correct" if score >= 65 else "À améliorer"

        st.markdown(f"""
        <div class="vda-hero">
            <div style="display:flex;align-items:center;gap:16px;position:relative;z-index:1">
                <span style="font-size:36px">📊</span>
                <div style="flex:1">
                    <div class="hero-title">VisualizeData Assistant</div>
                    <div class="hero-sub">📁 {st.session_state.file_name} · {len(df):,} lignes × {len(df.columns)} colonnes</div>
                </div>
                <div style="text-align:center;background:rgba(255,255,255,0.06);border-radius:12px;padding:12px 20px">
                    <div style="font-family:Outfit,sans-serif;font-size:28px;font-weight:900;color:{score_color}">{score}</div>
                    <div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.5px">{score_label}</div>
                </div>
                <div class="hero-badge">✨ MVP v2.0</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI bar
        num_cols = df.select_dtypes(include=[np.number]).columns
        completeness = audit['completeness']
        comp_color = COLORS['green'] if completeness >= 90 else COLORS['yellow'] if completeness >= 70 else COLORS['red']

        c1,c2,c3,c4,c5 = st.columns(5)
        kpis = [
            (c1, "📋", f"{len(df):,}", "Lignes", COLORS['primary']),
            (c2, "📊", str(len(df.columns)), "Colonnes", COLORS['secondary']),
            (c3, "✅", f"{completeness}%", "Complétude", comp_color),
            (c4, "🔄", str(audit['duplicates']), "Doublons", COLORS['red'] if audit['duplicates'] > 0 else COLORS['green']),
            (c5, "🔢", str(len(num_cols)), "Cols numériques", COLORS['primary']),
        ]
        for widget, icon, val, label, color in kpis:
            with widget:
                st.markdown(f"""
                <div class="kpi-card" style="border-top-color:{color}">
                    <div class="kpi-icon">{icon}</div>
                    <div class="kpi-value" style="color:{color}">{val}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="vda-hero">
            <div style="display:flex;align-items:center;gap:16px;position:relative;z-index:1">
                <span style="font-size:36px">📊</span>
                <div>
                    <div class="hero-title">VisualizeData Assistant</div>
                    <div class="hero-sub">Votre analyste de données alimenté par l'IA · Transforming Data Into Decisions</div>
                </div>
                <div class="hero-badge">✨ MVP v2.0</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # ACCUEIL
    # ══════════════════════════════════════════════════════════
    if "Accueil" in module or df is None:
        if df is None:
            st.markdown("""
            <div style="text-align:center;padding:40px 0 20px">
                <div style="font-size:56px;margin-bottom:16px">📂</div>
                <div style="font-family:Outfit,sans-serif;font-size:22px;font-weight:800;color:#08102B;margin-bottom:10px">Importez vos données pour commencer</div>
                <div style="font-size:15px;color:#8892A4;max-width:400px;margin:0 auto;line-height:1.7">Glissez un fichier <strong>Excel (.xlsx)</strong> ou <strong>CSV</strong> dans la barre latérale gauche</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="welcome-grid">
            <div class="welcome-card" style="border-top-color:#5B4EFF">
                <div class="welcome-icon">🔍</div>
                <div class="welcome-title">Data Audit</div>
                <div class="welcome-desc">Score de qualité, valeurs manquantes, doublons et anomalies détectés automatiquement.</div>
            </div>
            <div class="welcome-card" style="border-top-color:#FF6B35">
                <div class="welcome-icon">📊</div>
                <div class="welcome-title">Smart Analytics</div>
                <div class="welcome-desc">Statistiques, corrélations, Pareto et insights générés en quelques secondes.</div>
            </div>
            <div class="welcome-card" style="border-top-color:#00D4AA">
                <div class="welcome-icon">🎨</div>
                <div class="welcome-title">Dashboards Auto</div>
                <div class="welcome-desc">6 graphiques interactifs créés automatiquement selon vos données.</div>
            </div>
            <div class="welcome-card" style="border-top-color:#5B4EFF">
                <div class="welcome-icon">💬</div>
                <div class="welcome-title">AI Chat</div>
                <div class="welcome-desc">Posez vos questions en français : "Quels sont mes meilleurs clients ?"</div>
            </div>
            <div class="welcome-card" style="border-top-color:#FF6B35">
                <div class="welcome-icon">📄</div>
                <div class="welcome-title">Rapport Auto</div>
                <div class="welcome-desc">Téléchargez vos données nettoyées et un rapport JSON complet en 1 clic.</div>
            </div>
            <div class="welcome-card" style="border-top-color:#00D4AA">
                <div class="welcome-icon">🚀</div>
                <div class="welcome-title">Tous formats</div>
                <div class="welcome-desc">Excel, CSV, fichiers "moches" — l'app s'adapte automatiquement à vos données.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ══════════════════════════════════════════════════════════
    # DATA AUDIT
    # ══════════════════════════════════════════════════════════
    elif "Audit" in module:
        insights, warnings_list, errors = generate_insights(df, audit, analytics)

        col_gauge, col_detail = st.columns([1, 2])
        with col_gauge:
            score = audit['quality_score']
            color = COLORS['green'] if score >= 85 else COLORS['yellow'] if score >= 65 else COLORS['red']
            label = "Excellent ✨" if score >= 85 else "Correct 👍" if score >= 65 else "À améliorer ⚠️"
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x':[0,1],'y':[0,1]},
                title={'text':"Score Qualité",'font':{'size':14,'family':'Outfit','color':'#08102B'}},
                number={'font':{'size':42,'family':'Outfit','color':color}},
                gauge={
                    'axis':{'range':[0,100],'tickfont':{'family':'Plus Jakarta Sans'}},
                    'bar':{'color':color,'thickness':0.7},
                    'bgcolor':'white',
                    'steps':[{'range':[0,65],'color':'#FEE2E2'},{'range':[65,85],'color':'#FEF3C7'},{'range':[85,100],'color':'#D1FAE5'}],
                    'threshold':{'line':{'color':color,'width':3},'thickness':0.8,'value':score}
                }
            ))
            fig_g.update_layout(height=220, paper_bgcolor='white', font_family='Plus Jakarta Sans', margin=dict(t=30,b=10,l=20,r=20))
            st.plotly_chart(fig_g, use_container_width=True)
            st.markdown(f'<div style="text-align:center;font-family:Outfit,sans-serif;font-size:16px;font-weight:800;color:{color};margin-top:-15px">{label}</div>', unsafe_allow_html=True)

        with col_detail:
            st.markdown('<div class="section-hd">⚠️ Alertes & Insights</div>', unsafe_allow_html=True)
            for e in errors:
                st.markdown(f'<div class="error-box">{e}</div>', unsafe_allow_html=True)
            for w in warnings_list:
                st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)
            for i in insights:
                st.markdown(f'<div class="insight-box">{i}</div>', unsafe_allow_html=True)
            if not errors and not warnings_list and not insights:
                st.markdown('<div class="success-box">✅ Données en parfait état !</div>', unsafe_allow_html=True)

        # Détails
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Vue d'ensemble", "⚠️ Valeurs manquantes", "🔴 Doublons", "📍 Outliers"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="section-hd">📊 Profil des données</div>', unsafe_allow_html=True)
                profile = pd.DataFrame({
                    'Métrique': ['Lignes total', 'Colonnes total', 'Cellules total', 'Complétude', 'Doublons', 'Score qualité'],
                    'Valeur': [f"{audit['total_rows']:,}", f"{audit['total_cols']}", f"{audit['total_rows']*audit['total_cols']:,}", f"{audit['completeness']}%", f"{audit['duplicates']}", f"{audit['quality_score']}/100"]
                })
                st.dataframe(profile, use_container_width=True, hide_index=True)
            with c2:
                st.markdown('<div class="section-hd">🔢 Types de colonnes</div>', unsafe_allow_html=True)
                types = df.dtypes.value_counts().reset_index()
                types.columns = ['Type', 'Nombre']
                types['Type'] = types['Type'].astype(str)
                st.dataframe(types, use_container_width=True, hide_index=True)

        with tab2:
            if audit['missing']:
                miss_df = pd.DataFrame({
                    'Colonne': list(audit['missing'].keys()),
                    'Nb manquant': list(audit['missing'].values()),
                    'Pourcentage': [f"{v}%" for v in audit['missing_pct'].values()]
                }).sort_values('Nb manquant', ascending=False)
                fig_miss = px.bar(miss_df, x='Colonne', y='Nb manquant',
                                 color='Nb manquant',
                                 color_continuous_scale=['#00D4AA','#F59E0B','#EF4444'],
                                 title="Valeurs manquantes par colonne")
                fig_miss.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                                      font_family='Plus Jakarta Sans', showlegend=False,
                                      title_font=dict(family='Outfit',size=14))
                st.plotly_chart(fig_miss, use_container_width=True)
                st.dataframe(miss_df, use_container_width=True, hide_index=True)
            else:
                st.markdown('<div class="success-box">✅ Aucune valeur manquante détectée !</div>', unsafe_allow_html=True)

        with tab3:
            if audit['duplicates'] > 0:
                st.markdown(f'<div class="error-box">🔴 {audit["duplicates"]} ligne(s) en double ({audit["dup_pct"]}% des données)</div>', unsafe_allow_html=True)
                dups = df[df.duplicated(keep=False)].head(10)
                st.dataframe(dups, use_container_width=True)
            else:
                st.markdown('<div class="success-box">✅ Aucun doublon détecté !</div>', unsafe_allow_html=True)

        with tab4:
            if audit['outliers']:
                for col, info in audit['outliers'].items():
                    st.markdown(f'<div class="warning-box">📍 <strong>{col}</strong> : {info["count"]} valeur(s) aberrante(s) ({info["pct"]}%)</div>', unsafe_allow_html=True)
                # Box plot des outliers
                num_cols_list = list(audit['outliers'].keys())[:5]
                fig_box = go.Figure()
                for i, col in enumerate(num_cols_list):
                    fig_box.add_trace(go.Box(y=df[col], name=col,
                                            marker_color=CHART_COLORS[i%len(CHART_COLORS)],
                                            boxpoints='outliers'))
                fig_box.update_layout(title="Distribution & Outliers", plot_bgcolor='white',
                                     paper_bgcolor='white', font_family='Plus Jakarta Sans',
                                     title_font=dict(family='Outfit',size=14))
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.markdown('<div class="success-box">✅ Aucune valeur aberrante détectée !</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # SMART ANALYTICS
    # ══════════════════════════════════════════════════════════
    elif "Analytics" in module:
        insights, warnings_list, errors = generate_insights(df, audit, analytics)

        # Insights rapides
        col_i, col_w = st.columns(2)
        with col_i:
            st.markdown('<div class="section-hd">💡 Insights automatiques</div>', unsafe_allow_html=True)
            for i in insights:
                st.markdown(f'<div class="insight-box">{i}</div>', unsafe_allow_html=True)
            if not insights:
                st.markdown('<div class="success-box">Analysez vos données pour voir les insights.</div>', unsafe_allow_html=True)
        with col_w:
            st.markdown('<div class="section-hd">⚠️ Points d\'attention</div>', unsafe_allow_html=True)
            for e in errors:
                st.markdown(f'<div class="error-box">{e}</div>', unsafe_allow_html=True)
            for w in warnings_list:
                st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)
            if not errors and not warnings_list:
                st.markdown('<div class="success-box">✅ Aucun point d\'attention.</div>', unsafe_allow_html=True)

        # Stats
        if 'stats' in analytics:
            st.markdown('<div class="section-hd">📋 Statistiques descriptives</div>', unsafe_allow_html=True)
            st.dataframe(analytics['stats'].style.background_gradient(cmap='Blues', axis=None),
                        use_container_width=True)

        # Groupby
        if 'group' in analytics:
            st.markdown(f'<div class="section-hd">📊 Analyse par {analytics["group_cat"]}</div>', unsafe_allow_html=True)
            col_g1, col_g2 = st.columns([2,1])
            with col_g1:
                grp = analytics['group'].reset_index()
                fig_g = px.bar(grp, x=analytics['group_cat'], y='Total',
                              color='Moyenne', color_continuous_scale=['#5B4EFF','#FF6B35'],
                              title=f"Total de {analytics['group_num']} par {analytics['group_cat']}")
                fig_g.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                                   font_family='Plus Jakarta Sans', title_font=dict(family='Outfit',size=14))
                st.plotly_chart(fig_g, use_container_width=True)
            with col_g2:
                st.dataframe(analytics['group'], use_container_width=True)

        # Corrélations
        if 'corr' in analytics:
            st.markdown('<div class="section-hd">🔗 Matrice de corrélations</div>', unsafe_allow_html=True)
            fig_c = px.imshow(analytics['corr'], text_auto=True,
                             color_continuous_scale=['#FF6B35','white','#5B4EFF'],
                             zmin=-1, zmax=1, title="Corrélations entre variables numériques")
            fig_c.update_layout(paper_bgcolor='white', font_family='Plus Jakarta Sans',
                               title_font=dict(family='Outfit',size=14))
            st.plotly_chart(fig_c, use_container_width=True)
            if analytics.get('strong_corr'):
                st.markdown('<div class="section-hd">💪 Corrélations fortes (|r| > 0.6)</div>', unsafe_allow_html=True)
                for sc in analytics['strong_corr']:
                    color = COLORS['primary'] if sc['v'] > 0 else COLORS['secondary']
                    direction = "positive 📈" if sc['v'] > 0 else "négative 📉"
                    st.markdown(f'<div class="insight-box">🔗 <strong>{sc["c1"]}</strong> ↔ <strong>{sc["c2"]}</strong> : corrélation {direction} (r = {sc["v"]})</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # DASHBOARDS
    # ══════════════════════════════════════════════════════════
    elif "Dashboard" in module:
        with st.spinner("🎨 Génération des visualisations..."):
            charts = create_charts(df)

        if not charts:
            st.warning("Pas assez de données numériques pour générer des graphiques.")
        else:
            for i in range(0, len(charts), 2):
                cols = st.columns(2)
                for j, col_w in enumerate(cols):
                    if i+j < len(charts):
                        _, fig = charts[i+j]
                        with col_w:
                            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-hd">📋 Aperçu des données</div>', unsafe_allow_html=True)
        n = st.slider("Lignes à afficher", 5, min(50, len(df)), 10)
        st.dataframe(df.head(n), use_container_width=True)

    # ══════════════════════════════════════════════════════════
    # AI CHAT
    # ══════════════════════════════════════════════════════════
    elif "Chat" in module:
        st.markdown('<div class="section-hd">💬 Posez vos questions en français</div>', unsafe_allow_html=True)

        # Suggestions
        suggestions = ["Top 5 meilleurs ?", "Quelle est la moyenne ?", "Y a-t-il des doublons ?",
                      "Valeurs manquantes ?", "Résumé complet", "Corrélations ?", "Anomalies ?", "Total par colonne ?"]
        st.markdown('<div class="chip-row">' + ''.join([f'<div class="chip">{s}</div>' for s in suggestions]) + '</div>', unsafe_allow_html=True)

        cols_sug = st.columns(4)
        for i, sug in enumerate(suggestions[:4]):
            with cols_sug[i]:
                if st.button(sug, key=f"s{i}", use_container_width=True):
                    st.session_state.chat.append(("user", sug))
                    st.session_state.chat.append(("ai", ai_response(sug, df)))
                    st.rerun()
        cols_sug2 = st.columns(4)
        for i, sug in enumerate(suggestions[4:]):
            with cols_sug2[i]:
                if st.button(sug, key=f"s{i+4}", use_container_width=True):
                    st.session_state.chat.append(("user", sug))
                    st.session_state.chat.append(("ai", ai_response(sug, df)))
                    st.rerun()

        st.markdown("---")

        # Historique
        if not st.session_state.chat:
            st.markdown("""
            <div style="text-align:center;padding:40px;color:#8892A4">
                <div style="font-size:40px;margin-bottom:12px">💬</div>
                <div style="font-size:15px;font-weight:600;color:#08102B">Posez votre première question</div>
                <div style="font-size:13px;margin-top:6px">Cliquez sur une suggestion ou tapez ci-dessous</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for role, msg in st.session_state.chat:
                if role == "user":
                    st.markdown(f"""
                    <div class="msg-user">
                        <div class="msg-user-bubble">{msg}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="msg-ai">
                        <div class="msg-ai-avatar">🤖</div>
                        <div>
                            <div class="msg-label">VisualizeData Assistant</div>
                            <div class="msg-ai-bubble">{msg}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Input
        col_in, col_btn = st.columns([5,1])
        with col_in:
            user_input = st.text_input("", placeholder="Ex: Quels sont mes 10 meilleurs clients par chiffre d'affaires ?",
                                      label_visibility="collapsed", key="chat_in")
        with col_btn:
            if st.button("Envoyer →", type="primary", use_container_width=True):
                if user_input.strip():
                    st.session_state.chat.append(("user", user_input))
                    st.session_state.chat.append(("ai", ai_response(user_input, df)))
                    st.rerun()

        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.chat = []
            st.rerun()

    # ══════════════════════════════════════════════════════════
    # RAPPORT
    # ══════════════════════════════════════════════════════════
    elif "Rapport" in module:
        st.markdown('<div class="section-hd">📄 Rapport d\'analyse automatique</div>', unsafe_allow_html=True)
        insights, warnings_list, errors = generate_insights(df, audit, analytics)

        # Aperçu rapport
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📊 Résumé du rapport</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div>
                    <div style="font-size:13px;color:#8892A4;margin-bottom:8px">Informations générales</div>
                    <div style="font-size:13px;line-height:2;color:#1C2640">
                        📁 Fichier : <strong>{st.session_state.file_name}</strong><br>
                        📅 Date : <strong>{datetime.now().strftime('%d/%m/%Y %H:%M')}</strong><br>
                        📋 Dimensions : <strong>{len(df):,} × {len(df.columns)}</strong><br>
                        ⭐ Score qualité : <strong>{audit['quality_score']}/100</strong>
                    </div>
                </div>
                <div>
                    <div style="font-size:13px;color:#8892A4;margin-bottom:8px">Points clés</div>
                    <div style="font-size:13px;line-height:2;color:#1C2640">
                        ✅ Complétude : <strong>{audit['completeness']}%</strong><br>
                        🔄 Doublons : <strong>{audit['duplicates']}</strong><br>
                        📍 Outliers : <strong>{len(audit['outliers'])} colonne(s)</strong><br>
                        💡 Insights : <strong>{len(insights)}</strong>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if insights:
            st.markdown("**💡 Insights principaux**")
            for i in insights[:3]:
                st.markdown(f'<div class="insight-box">{i}</div>', unsafe_allow_html=True)
        if errors:
            st.markdown("**⚠️ Points d'attention**")
            for e in errors[:3]:
                st.markdown(f'<div class="error-box">{e}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-hd">📥 Téléchargements</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        with c1:
            df_clean = df.drop_duplicates()
            buf = io.StringIO()
            df_clean.to_csv(buf, index=False, encoding='utf-8-sig')
            st.download_button("📊 Données nettoyées (CSV)",
                              data=buf.getvalue().encode('utf-8-sig'),
                              file_name=f"VDA_clean_{datetime.now().strftime('%Y%m%d')}.csv",
                              mime="text/csv", use_container_width=True, type="primary")

        with c2:
            rapport = {
                "date": datetime.now().strftime('%d/%m/%Y %H:%M'),
                "fichier": st.session_state.file_name,
                "dimensions": {"lignes": len(df), "colonnes": len(df.columns)},
                "qualite": {"score": audit['quality_score'], "completude": audit['completeness'],
                           "doublons": audit['duplicates'], "outliers": len(audit['outliers'])},
                "insights": insights, "alertes": errors + warnings_list,
                "colonnes": df.columns.tolist()
            }
            st.download_button("📄 Rapport JSON",
                              data=json.dumps(rapport, ensure_ascii=False, indent=2),
                              file_name=f"VDA_rapport_{datetime.now().strftime('%Y%m%d')}.json",
                              mime="application/json", use_container_width=True)

        with c3:
            if 'stats' in analytics:
                st.download_button("📋 Statistiques (CSV)",
                                  data=analytics['stats'].to_csv().encode('utf-8-sig'),
                                  file_name=f"VDA_stats_{datetime.now().strftime('%Y%m%d')}.csv",
                                  mime="text/csv", use_container_width=True)

    # Reset
    st.markdown("---")
    if st.button("🔄 Changer de fichier", use_container_width=False):
        for key in ['df','audit','analytics','chat','file_name']:
            st.session_state[key] = None if key != 'chat' else []
        st.rerun()


if __name__ == "__main__":
    main()
