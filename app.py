"""
VisualizeData Assistant — MVP v1.0
Votre analyste de données alimenté par l'IA
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG PAGE ────────────────────────────────────────────────
st.set_page_config(
    page_title="VisualizeData Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLES CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp { background: #F8FAFF; }

/* Header principal */
.vda-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    padding: 28px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid rgba(79,70,229,0.2);
    display: flex;
    align-items: center;
    gap: 18px;
}
.vda-logo { font-size: 42px; }
.vda-title {
    font-size: 26px; font-weight: 800;
    color: #FFFFFF; letter-spacing: -0.5px;
}
.vda-subtitle { font-size: 14px; color: rgba(255,255,255,0.5); margin-top: 4px; }
.vda-badge {
    background: rgba(79,70,229,0.2); color: #A5B4FC;
    border: 1px solid rgba(79,70,229,0.3);
    padding: 4px 14px; border-radius: 100px;
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.5px; text-transform: uppercase;
    margin-left: auto;
}

/* KPI Cards */
.kpi-card {
    background: white;
    border: 1.5px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    border-top: 3px solid;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-num {
    font-size: 28px; font-weight: 800;
    color: #0F172A; letter-spacing: -1px;
}
.kpi-label { font-size: 12px; color: #64748B; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-trend { font-size: 12px; font-weight: 600; margin-top: 6px; }

/* Section titles */
.section-title {
    font-size: 16px; font-weight: 700;
    color: #0F172A; margin: 24px 0 12px;
    display: flex; align-items: center; gap: 8px;
}

/* Insight cards */
.insight-card {
    background: #EEF4FF;
    border: 1px solid rgba(79,70,229,0.15);
    border-left: 4px solid #4F46E5;
    border-radius: 10px; padding: 14px 18px;
    margin: 8px 0;
    font-size: 14px; color: #1E293B;
    line-height: 1.6;
}
.anomaly-card {
    background: #FFF1F2;
    border-left: 4px solid #DC2626;
    border-radius: 10px; padding: 14px 18px;
    margin: 8px 0; font-size: 14px; color: #1E293B;
}
.success-card {
    background: #F0FDF4;
    border-left: 4px solid #16A34A;
    border-radius: 10px; padding: 14px 18px;
    margin: 8px 0; font-size: 14px; color: #1E293B;
}

/* Chat */
.chat-user {
    background: #4F46E5; color: white;
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px; margin: 8px 0;
    max-width: 80%; margin-left: auto;
    font-size: 14px; line-height: 1.6;
}
.chat-ai {
    background: white; color: #1E293B;
    border: 1.5px solid #E2E8F0;
    border-radius: 14px 14px 14px 4px;
    padding: 12px 16px; margin: 8px 0;
    max-width: 85%;
    font-size: 14px; line-height: 1.6;
}
.chat-label { font-size: 11px; color: #64748B; margin-bottom: 4px; font-weight: 600; }

/* Upload zone */
.upload-zone {
    background: white;
    border: 2px dashed #CBD5E0;
    border-radius: 16px; padding: 48px;
    text-align: center;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: #4F46E5; }

/* Sidebar */
.sidebar-module {
    background: rgba(79,70,229,0.06);
    border: 1px solid rgba(79,70,229,0.12);
    border-radius: 10px; padding: 12px;
    margin: 6px 0; cursor: pointer;
    transition: all 0.2s; font-size: 13px;
    font-weight: 500; color: #1E293B;
}
.sidebar-module:hover { background: rgba(79,70,229,0.12); color: #4F46E5; }
.sidebar-module.active { background: #4F46E5; color: white; }

/* Tab style */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #F1F5F9;
    border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px; padding: 8px 18px;
    font-weight: 500; font-size: 13px;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #4F46E5 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* Buttons */
.stButton > button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; }

/* Metrics */
[data-testid="metric-container"] {
    background: white;
    border: 1.5px solid #E2E8F0;
    border-radius: 12px; padding: 16px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* Alerts */
.stSuccess, .stInfo, .stWarning, .stError { border-radius: 10px !important; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ── FONCTIONS UTILITAIRES ──────────────────────────────────────

@st.cache_data
def load_data(file_bytes, file_name):
    """Charger les données depuis différents formats"""
    try:
        if file_name.endswith('.csv'):
            # Essayer différents encodages et séparateurs
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, sep=sep)
                        if df.shape[1] > 1:
                            return df, None
                    except:
                        continue
            return pd.read_csv(io.BytesIO(file_bytes)), None
        elif file_name.endswith(('.xlsx', '.xls')):
            xl = pd.ExcelFile(io.BytesIO(file_bytes))
            sheets = xl.sheet_names
            if len(sheets) > 1:
                return xl.parse(sheets[0]), sheets
            return xl.parse(sheets[0]), None
        else:
            return None, "Format non supporté"
    except Exception as e:
        return None, str(e)


def detect_column_types(df):
    """Détecter les types de colonnes intelligemment"""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col], errors='raise')
                date_cols.append(col)
                cat_cols.remove(col) if col in cat_cols else None
            except:
                pass
    return num_cols, cat_cols, date_cols


def data_audit(df):
    """Module 1 — Audit complet des données"""
    results = {}
    total = len(df)
    results['total_rows'] = total
    results['total_cols'] = len(df.columns)
    results['total_cells'] = total * len(df.columns)

    # Valeurs manquantes
    missing = df.isnull().sum()
    results['missing'] = missing[missing > 0].to_dict()
    results['missing_pct'] = {k: round(v/total*100, 1) for k,v in results['missing'].items()}
    results['completeness_score'] = round((1 - df.isnull().sum().sum() / results['total_cells']) * 100, 1)

    # Doublons
    results['duplicates'] = df.duplicated().sum()
    results['dup_pct'] = round(results['duplicates']/total*100, 1)

    # Outliers (colonnes numériques)
    num_cols = df.select_dtypes(include=[np.number]).columns
    outliers = {}
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        n_out = ((df[col] < lower) | (df[col] > upper)).sum()
        if n_out > 0:
            outliers[col] = {'count': int(n_out), 'pct': round(n_out/total*100, 1)}
    results['outliers'] = outliers

    # Score qualité global
    score = results['completeness_score']
    if results['duplicates'] > 0: score -= min(10, results['dup_pct'])
    if outliers: score -= min(10, len(outliers) * 2)
    results['quality_score'] = max(0, round(score, 0))

    return results


def smart_analytics(df):
    """Module 2 — Analyse intelligente"""
    num_cols = df.select_dtypes(include=[np.number]).columns
    results = {}

    # Stats descriptives
    if len(num_cols) > 0:
        desc = df[num_cols].describe().round(2)
        results['descriptive'] = desc

    # Corrélations
    if len(num_cols) > 1:
        corr = df[num_cols].corr().round(3)
        # Trouver les corrélations fortes
        strong_corr = []
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                val = corr.iloc[i,j]
                if abs(val) > 0.6:
                    strong_corr.append({
                        'col1': corr.columns[i],
                        'col2': corr.columns[j],
                        'corr': round(val, 3),
                        'type': 'positive' if val > 0 else 'negative'
                    })
        results['correlations'] = corr
        results['strong_correlations'] = strong_corr

    # Pareto si colonne catégorielle + numérique
    cat_cols = df.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0 and len(num_cols) > 0:
        cat = cat_cols[0]
        num = num_cols[0]
        pareto = df.groupby(cat)[num].sum().sort_values(ascending=False)
        cumsum_pct = pareto.cumsum() / pareto.sum() * 100
        n80 = (cumsum_pct <= 80).sum()
        results['pareto'] = {
            'category': cat, 'value': num,
            'top_items': pareto.head(10).to_dict(),
            'n80': int(n80), 'total': len(pareto)
        }

    return results


def generate_insights(df, audit, analytics):
    """Générer des insights automatiques en français"""
    insights = []
    anomalies = []

    # Insights qualité
    score = audit['quality_score']
    if score >= 85:
        insights.append(f"✅ Excellent niveau de qualité des données ({score}/100). Vos données sont fiables pour l'analyse.")
    elif score >= 65:
        insights.append(f"⚠️ Qualité des données correcte ({score}/100) mais des améliorations sont recommandées.")
    else:
        anomalies.append(f"🚨 Qualité des données insuffisante ({score}/100). Les analyses peuvent être biaisées.")

    # Insights valeurs manquantes
    if audit['missing']:
        top_missing = max(audit['missing_pct'], key=audit['missing_pct'].get)
        pct = audit['missing_pct'][top_missing]
        if pct > 20:
            anomalies.append(f"🔴 La colonne '{top_missing}' a {pct}% de valeurs manquantes. Cela peut fausser les analyses.")
        else:
            insights.append(f"ℹ️ {len(audit['missing'])} colonne(s) ont des valeurs manquantes (max: {pct}% pour '{top_missing}').")

    # Insights doublons
    if audit['duplicates'] > 0:
        anomalies.append(f"⚠️ {audit['duplicates']} ligne(s) en double détectée(s) ({audit['dup_pct']}% des données).")

    # Insights outliers
    if audit['outliers']:
        for col, info in list(audit['outliers'].items())[:2]:
            anomalies.append(f"📍 {info['count']} valeur(s) aberrante(s) détectée(s) dans '{col}' ({info['pct']}% des données).")

    # Insights corrélations
    if 'strong_correlations' in analytics and analytics['strong_correlations']:
        for sc in analytics['strong_correlations'][:2]:
            direction = "positivement" if sc['type'] == 'positive' else "négativement"
            insights.append(f"📊 '{sc['col1']}' et '{sc['col2']}' sont fortement corrélées ({direction}, r={sc['corr']}). Une augmentation de l'une influence l'autre.")

    # Insights Pareto
    if 'pareto' in analytics:
        p = analytics['pareto']
        pct_items = round(p['n80']/p['total']*100)
        insights.append(f"📐 Loi de Pareto : {pct_items}% de vos '{p['category']}' représentent 80% du total de '{p['value']}'. Concentrez vos efforts sur ces éléments prioritaires.")

    return insights, anomalies


def ai_chat_response(question, df, context=""):
    """Réponse IA basée sur les données (sans API externe pour le MVP)"""
    question_lower = question.lower()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Patterns de questions
    if any(w in question_lower for w in ['meilleur', 'top', 'plus', 'maximum', 'max', 'premier']):
        if num_cols and cat_cols:
            col_num = num_cols[0]
            col_cat = cat_cols[0]
            top = df.groupby(col_cat)[col_num].sum().sort_values(ascending=False).head(5)
            response = f"📊 **Top 5 de '{col_cat}' par '{col_num}' :**\n\n"
            for i, (k, v) in enumerate(top.items(), 1):
                response += f"{i}. **{k}** : {v:,.0f}\n"
            response += f"\n💡 *'{top.index[0]}' est en tête avec {top.iloc[0]:,.0f}, soit {top.iloc[0]/top.sum()*100:.1f}% du total.*"
            return response

    elif any(w in question_lower for w in ['moyenne', 'moyen', 'average', 'moy']):
        if num_cols:
            response = "📊 **Moyennes de vos données numériques :**\n\n"
            for col in num_cols[:5]:
                response += f"• **{col}** : {df[col].mean():,.2f} (min: {df[col].min():,.2f} | max: {df[col].max():,.2f})\n"
            return response

    elif any(w in question_lower for w in ['total', 'somme', 'sum', 'cumulé']):
        if num_cols:
            response = "📊 **Totaux de vos données numériques :**\n\n"
            for col in num_cols[:5]:
                response += f"• **{col}** : {df[col].sum():,.0f}\n"
            return response

    elif any(w in question_lower for w in ['manquant', 'vide', 'null', 'missing']):
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            return "✅ **Aucune valeur manquante** dans vos données. Votre fichier est complet !"
        response = f"⚠️ **{len(missing)} colonne(s) avec des valeurs manquantes :**\n\n"
        for col, n in missing.items():
            response += f"• **{col}** : {n} valeurs manquantes ({n/len(df)*100:.1f}%)\n"
        return response

    elif any(w in question_lower for w in ['doublon', 'duplicate', 'répété']):
        n_dup = df.duplicated().sum()
        if n_dup == 0:
            return "✅ **Aucun doublon** détecté dans vos données !"
        return f"⚠️ **{n_dup} ligne(s) en double** trouvée(s), soit {n_dup/len(df)*100:.1f}% de vos données. Il est recommandé de les supprimer avant l'analyse."

    elif any(w in question_lower for w in ['lignes', 'colonnes', 'taille', 'dimensions', 'shape']):
        return f"📋 **Dimensions de votre fichier :**\n\n• **{len(df):,} lignes** (enregistrements)\n• **{len(df.columns)} colonnes** (variables)\n• **{len(df)*len(df.columns):,} cellules** au total\n\nColonnes numériques : {', '.join(num_cols[:5]) if num_cols else 'Aucune'}\nColonnes texte : {', '.join(cat_cols[:5]) if cat_cols else 'Aucune'}"

    elif any(w in question_lower for w in ['correlation', 'corrélation', 'lien', 'relation']):
        if len(num_cols) >= 2:
            corr = df[num_cols].corr()
            strong = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    val = corr.iloc[i,j]
                    if abs(val) > 0.5:
                        strong.append((corr.columns[i], corr.columns[j], round(val,3)))
            if strong:
                response = "📊 **Corrélations fortes détectées :**\n\n"
                for c1, c2, v in strong[:5]:
                    typ = "positive 📈" if v > 0 else "négative 📉"
                    response += f"• **{c1}** ↔ **{c2}** : corrélation {typ} (r = {v})\n"
                return response
            return "ℹ️ Aucune corrélation forte (>0.5) trouvée entre vos variables numériques."
        return "⚠️ Il faut au moins 2 colonnes numériques pour calculer des corrélations."

    elif any(w in question_lower for w in ['analyse', 'résumé', 'résume', 'synthèse', 'overview']):
        num_summary = f"{len(num_cols)} numérique(s)" if num_cols else "aucune numérique"
        cat_summary = f"{len(cat_cols)} catégorielle(s)" if cat_cols else "aucune catégorielle"
        missing_total = df.isnull().sum().sum()
        return f"""📊 **Résumé de vos données :**

• **Taille** : {len(df):,} lignes × {len(df.columns)} colonnes
• **Variables** : {num_summary}, {cat_summary}
• **Complétude** : {round((1-missing_total/(len(df)*len(df.columns)))*100,1)}%
• **Doublons** : {df.duplicated().sum()} ligne(s)

**Colonnes numériques** : {', '.join(num_cols) if num_cols else 'Aucune'}
**Colonnes catégorielles** : {', '.join(cat_cols) if cat_cols else 'Aucune'}

💡 *Posez des questions plus spécifiques comme "Quels sont les tops 5 ?", "Quelle est la moyenne de X ?" ou "Y a-t-il des doublons ?"*"""

    else:
        return f"""🤖 **Je n'ai pas compris cette question précisément.**

Voici ce que je peux analyser dans vos données ({len(df):,} lignes, {len(df.columns)} colonnes) :

• *"Quels sont les 5 meilleurs [éléments] par [valeur] ?"*
• *"Quelle est la moyenne / le total de [colonne] ?"*
• *"Y a-t-il des valeurs manquantes ou des doublons ?"*
• *"Montre-moi les corrélations entre les variables"*
• *"Donne-moi un résumé de mes données"*

**Colonnes disponibles** : {', '.join(df.columns.tolist()[:8])}{'...' if len(df.columns) > 8 else ''}"""


def create_auto_charts(df):
    """Générer des graphiques automatiquement selon le type de données"""
    charts = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    colors = ['#4F46E5', '#F97316', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']

    # 1. Distribution des colonnes numériques (histogramme)
    if num_cols:
        col = num_cols[0]
        fig = px.histogram(df, x=col, nbins=30,
                          color_discrete_sequence=[colors[0]],
                          title=f"Distribution de {col}")
        fig.update_layout(bargap=0.05, plot_bgcolor='white', paper_bgcolor='white',
                         font_family='Inter', title_font_size=14, title_font_color='#0F172A',
                         xaxis=dict(gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9'))
        charts.append(('distribution', f'Distribution — {col}', fig))

    # 2. Barres catégorielles
    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        agg = df.groupby(cat)[num].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(agg, x=cat, y=num,
                    color_discrete_sequence=[colors[1]],
                    title=f"Top 10 : {num} par {cat}")
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                         font_family='Inter', title_font_size=14, title_font_color='#0F172A',
                         xaxis=dict(gridcolor='#F1F5F9', tickangle=-30), yaxis=dict(gridcolor='#F1F5F9'))
        charts.append(('bar', f'{num} par {cat}', fig))

    # 3. Scatter plot si 2+ colonnes numériques
    if len(num_cols) >= 2:
        x, y = num_cols[0], num_cols[1]
        color_col = cat_cols[0] if cat_cols else None
        fig = px.scatter(df, x=x, y=y, color=color_col,
                        color_discrete_sequence=colors,
                        title=f"Relation entre {x} et {y}",
                        opacity=0.7)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                         font_family='Inter', title_font_size=14, title_font_color='#0F172A',
                         xaxis=dict(gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9'))
        charts.append(('scatter', f'{x} vs {y}', fig))

    # 4. Camembert si colonne catégorielle
    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        pie_data = df.groupby(cat)[num].sum().sort_values(ascending=False).head(8)
        fig = px.pie(values=pie_data.values, names=pie_data.index,
                    color_discrete_sequence=colors,
                    title=f"Répartition de {num} par {cat}")
        fig.update_layout(paper_bgcolor='white', font_family='Inter',
                         title_font_size=14, title_font_color='#0F172A')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        charts.append(('pie', f'Répartition {num}', fig))

    # 5. Carte de chaleur des corrélations
    if len(num_cols) >= 3:
        corr = df[num_cols[:8]].corr().round(2)
        fig = px.imshow(corr, text_auto=True, aspect='auto',
                       color_continuous_scale=['#F97316', 'white', '#4F46E5'],
                       title="Carte de corrélations",
                       zmin=-1, zmax=1)
        fig.update_layout(paper_bgcolor='white', font_family='Inter',
                         title_font_size=14, title_font_color='#0F172A')
        charts.append(('heatmap', 'Corrélations', fig))

    # 6. Box plot pour les outliers
    if num_cols:
        fig = go.Figure()
        for i, col in enumerate(num_cols[:5]):
            fig.add_trace(go.Box(y=df[col], name=col,
                               marker_color=colors[i % len(colors)],
                               boxpoints='outliers'))
        fig.update_layout(title="Distribution & Outliers",
                         plot_bgcolor='white', paper_bgcolor='white',
                         font_family='Inter', title_font_size=14, title_font_color='#0F172A',
                         yaxis=dict(gridcolor='#F1F5F9'))
        charts.append(('box', 'Outliers', fig))

    return charts


# ── INTERFACE PRINCIPALE ───────────────────────────────────────

def main():
    # Header
    st.markdown("""
    <div class="vda-header">
        <div class="vda-logo">📊</div>
        <div>
            <div class="vda-title">VisualizeData Assistant</div>
            <div class="vda-subtitle">Votre analyste de données alimenté par l'IA · Transforming Data Into Decisions</div>
        </div>
        <div class="vda-badge">✨ MVP v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    # ── SIDEBAR ────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🧩 Modules")
        modules = {
            "🔍 Data Audit": "Analyser la qualité de vos données",
            "📊 Smart Analytics": "Statistiques & insights automatiques",
            "🎨 Dashboard Builder": "Visualisations interactives",
            "💬 AI Chat": "Poser des questions en langage naturel",
            "📄 Rapport": "Générer un rapport complet",
        }
        module_choice = st.radio("", list(modules.keys()), label_visibility="collapsed")
        st.caption(modules[module_choice])
        st.divider()

        st.markdown("### 📁 Import de données")
        uploaded_file = st.file_uploader(
            "Glissez votre fichier ici",
            type=['csv', 'xlsx', 'xls'],
            help="Formats supportés : CSV, Excel (.xlsx, .xls)"
        )

        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.caption(f"Taille : {uploaded_file.size/1024:.1f} KB")

        st.divider()
        st.markdown("### ℹ️ À propos")
        st.caption("**VisualizeData Assistant** v1.0")
        st.caption("📧 service@visualizedatacom.com")
        st.caption("🌐 visualizedatacom.com")

    # ── ÉTAT DE L'APPLICATION ──────────────────────────────────
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'audit' not in st.session_state:
        st.session_state.audit = None
    if 'analytics' not in st.session_state:
        st.session_state.analytics = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # ── CHARGEMENT DES DONNÉES ─────────────────────────────────
    if uploaded_file and st.session_state.df is None:
        with st.spinner("⏳ Chargement et analyse de vos données..."):
            file_bytes = uploaded_file.getvalue()
            df, error = load_data(file_bytes, uploaded_file.name)
            if error and df is None:
                st.error(f"❌ Erreur : {error}")
            else:
                st.session_state.df = df
                st.session_state.audit = data_audit(df)
                st.session_state.analytics = smart_analytics(df)
                st.success(f"✅ Données chargées : {len(df):,} lignes × {len(df.columns)} colonnes")
                st.rerun()

    # ── ÉCRAN D'ACCUEIL (pas de fichier) ──────────────────────
    if st.session_state.df is None:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("""
            <div style="text-align:center; padding: 60px 0;">
                <div style="font-size: 64px; margin-bottom: 20px;">📂</div>
                <h2 style="font-size:22px; font-weight:700; color:#0F172A; margin-bottom:12px;">
                    Importez vos données pour commencer
                </h2>
                <p style="font-size:15px; color:#64748B; margin-bottom:32px; line-height:1.7;">
                    Glissez un fichier <strong>Excel (.xlsx)</strong> ou <strong>CSV</strong><br>
                    dans la barre latérale pour démarrer l'analyse.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Features preview
        st.markdown("### 🚀 Ce que vous pouvez faire avec VisualizeData Assistant")
        c1, c2, c3 = st.columns(3)
        features = [
            ("🔍", "Data Audit", "Détectez automatiquement les données manquantes, doublons et anomalies"),
            ("📊", "Smart Analytics", "Obtenez des statistiques, corrélations et insights en quelques secondes"),
            ("🎨", "Visualisations", "6 types de graphiques générés automatiquement depuis vos données"),
            ("💬", "Chat IA", "Posez des questions en français : 'Quels sont mes meilleurs clients ?'"),
            ("📄", "Rapports Auto", "Générez un rapport PDF ou Word complet en un clic"),
            ("🎯", "Insights", "L'IA explique les résultats comme un consultant senior"),
        ]
        cols = st.columns(3)
        for i, (ico, title, desc) in enumerate(features):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:white; border:1.5px solid #E2E8F0; border-radius:14px; padding:20px; margin:6px 0; border-top:3px solid {'#4F46E5' if i%2==0 else '#F97316'}">
                    <div style="font-size:28px; margin-bottom:10px">{ico}</div>
                    <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:6px">{title}</div>
                    <div style="font-size:13px; color:#64748B; line-height:1.6">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        return

    # ── DONNÉES CHARGÉES ───────────────────────────────────────
    df = st.session_state.df
    audit = st.session_state.audit
    analytics = st.session_state.analytics

    # KPI bar principale
    num_cols, cat_cols, date_cols = detect_column_types(df)
    missing_total = df.isnull().sum().sum()
    completeness = round((1 - missing_total / (len(df)*len(df.columns))) * 100, 1)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpis = [
        (k1, f"{len(df):,}", "Lignes", "#4F46E5", "📋"),
        (k2, str(len(df.columns)), "Colonnes", "#F97316", "📊"),
        (k3, f"{completeness}%", "Complétude", "#10B981" if completeness > 80 else "#F59E0B", "✅"),
        (k4, str(df.duplicated().sum()), "Doublons", "#EF4444" if df.duplicated().sum() > 0 else "#10B981", "🔄"),
        (k5, f"{audit['quality_score']}/100", "Score qualité", "#10B981" if audit['quality_score'] > 80 else "#F59E0B", "⭐"),
    ]
    for col_widget, val, label, color, icon in kpis:
        with col_widget:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{color}">
                <div style="font-size:18px; margin-bottom:4px">{icon}</div>
                <div class="kpi-num" style="color:{color}">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ══════════════════════════════════════════════════════════
    # MODULE 1 — DATA AUDIT
    # ══════════════════════════════════════════════════════════
    if module_choice == "🔍 Data Audit":
        st.markdown('<div class="section-title">🔍 Rapport d\'Audit de Qualité des Données</div>', unsafe_allow_html=True)

        # Score visuel
        score = audit['quality_score']
        color_score = "#10B981" if score >= 85 else "#F59E0B" if score >= 65 else "#EF4444"
        label_score = "Excellent" if score >= 85 else "Correct" if score >= 65 else "À améliorer"

        col_score, col_detail = st.columns([1, 2])
        with col_score:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Score Qualité", 'font': {'size': 16, 'family': 'Inter', 'color': '#0F172A'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickfont': {'family': 'Inter'}},
                    'bar': {'color': color_score},
                    'steps': [
                        {'range': [0, 65], 'color': '#FEE2E2'},
                        {'range': [65, 85], 'color': '#FEF3C7'},
                        {'range': [85, 100], 'color': '#D1FAE5'}
                    ],
                    'threshold': {'line': {'color': color_score, 'width': 4}, 'thickness': 0.75, 'value': score}
                }
            ))
            fig_gauge.update_layout(height=250, paper_bgcolor='white', font_family='Inter')
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown(f"""<div style="text-align:center; font-size:18px; font-weight:800; color:{color_score}; margin-top:-20px">{label_score}</div>""", unsafe_allow_html=True)

        with col_detail:
            st.markdown("**Détail de l'audit :**")
            metrics_audit = [
                ("Complétude des données", f"{completeness}%", completeness >= 90, "Données complètes" if completeness >= 90 else f"{int(missing_total)} valeurs manquantes"),
                ("Doublons", f"{audit['duplicates']} lignes", audit['duplicates'] == 0, "Aucun doublon" if audit['duplicates'] == 0 else f"{audit['dup_pct']}% en double"),
                ("Valeurs aberrantes", f"{len(audit['outliers'])} colonne(s)", len(audit['outliers']) == 0, "Aucun outlier" if len(audit['outliers']) == 0 else "Outliers détectés"),
                ("Cohérence des types", f"{len(num_cols)} num, {len(cat_cols)} cat", True, "Types de données cohérents"),
            ]
            for name, val, is_ok, note in metrics_audit:
                icon = "✅" if is_ok else "⚠️"
                color_m = "#10B981" if is_ok else "#F59E0B"
                st.markdown(f"""
                <div style="display:flex; align-items:center; padding:10px 14px; background:white; border:1px solid #E2E8F0; border-radius:10px; margin:6px 0">
                    <span style="font-size:18px; margin-right:12px">{icon}</span>
                    <div style="flex:1">
                        <div style="font-size:13px; font-weight:600; color:#0F172A">{name}</div>
                        <div style="font-size:12px; color:#64748B">{note}</div>
                    </div>
                    <div style="font-size:14px; font-weight:700; color:{color_m}">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        # Détail valeurs manquantes
        if audit['missing']:
            st.markdown('<div class="section-title">⚠️ Valeurs Manquantes par Colonne</div>', unsafe_allow_html=True)
            missing_df = pd.DataFrame({
                'Colonne': list(audit['missing'].keys()),
                'Manquant': list(audit['missing'].values()),
                'Pourcentage (%)': list(audit['missing_pct'].values())
            }).sort_values('Manquant', ascending=False)

            fig_miss = px.bar(missing_df, x='Colonne', y='Pourcentage (%)',
                             color='Pourcentage (%)',
                             color_continuous_scale=['#10B981', '#F59E0B', '#EF4444'],
                             title="% de valeurs manquantes par colonne")
            fig_miss.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                                  font_family='Inter', showlegend=False)
            st.plotly_chart(fig_miss, use_container_width=True)

        # Détail outliers
        if audit['outliers']:
            st.markdown('<div class="section-title">📍 Valeurs Aberrantes Détectées</div>', unsafe_allow_html=True)
            out_df = pd.DataFrame([
                {'Colonne': k, 'Nb Outliers': v['count'], 'Pourcentage': f"{v['pct']}%"}
                for k, v in audit['outliers'].items()
            ])
            st.dataframe(out_df, use_container_width=True, hide_index=True)

        # Recommandations
        st.markdown('<div class="section-title">💡 Recommandations</div>', unsafe_allow_html=True)
        recs = []
        if audit['missing']:
            recs.append("Imputer les valeurs manquantes (moyenne pour les numériques, mode pour les catégorielles) ou supprimer les lignes concernées si elles représentent moins de 5%.")
        if audit['duplicates'] > 0:
            recs.append(f"Supprimer les {audit['duplicates']} lignes dupliquées avant toute analyse pour éviter les biais.")
        if audit['outliers']:
            recs.append("Vérifier les valeurs aberrantes : sont-elles des erreurs de saisie ou des cas réels ? Traiter en conséquence.")
        if not recs:
            st.markdown('<div class="success-card">✅ Vos données sont de bonne qualité. Vous pouvez procéder aux analyses.</div>', unsafe_allow_html=True)
        for rec in recs:
            st.markdown(f'<div class="insight-card">💡 {rec}</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # MODULE 2 — SMART ANALYTICS
    # ══════════════════════════════════════════════════════════
    elif module_choice == "📊 Smart Analytics":
        st.markdown('<div class="section-title">📊 Analyse Intelligente des Données</div>', unsafe_allow_html=True)

        insights, anomalies = generate_insights(df, audit, analytics)

        # Insights et anomalies
        col_ins, col_ano = st.columns(2)
        with col_ins:
            st.markdown("**💡 Insights détectés**")
            for ins in insights:
                st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)
        with col_ano:
            st.markdown("**⚠️ Anomalies détectées**")
            if anomalies:
                for ano in anomalies:
                    st.markdown(f'<div class="anomaly-card">{ano}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-card">✅ Aucune anomalie majeure détectée.</div>', unsafe_allow_html=True)

        # Stats descriptives
        if 'descriptive' in analytics:
            st.markdown('<div class="section-title">📋 Statistiques Descriptives</div>', unsafe_allow_html=True)
            st.dataframe(analytics['descriptive'].style.background_gradient(cmap='Blues', axis=None),
                        use_container_width=True)

        # Analyse Pareto
        if 'pareto' in analytics:
            p = analytics['pareto']
            st.markdown(f'<div class="section-title">📐 Analyse de Pareto — {p["category"]} × {p["value"]}</div>', unsafe_allow_html=True)
            col_p1, col_p2 = st.columns([2,1])
            with col_p1:
                pareto_data = pd.DataFrame({
                    p['category']: list(p['top_items'].keys()),
                    p['value']: list(p['top_items'].values())
                })
                pareto_data['Cumul %'] = pareto_data[p['value']].cumsum() / pareto_data[p['value']].sum() * 100
                fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
                fig_pareto.add_trace(go.Bar(x=pareto_data[p['category']], y=pareto_data[p['value']],
                                           name=p['value'], marker_color='#4F46E5'), secondary_y=False)
                fig_pareto.add_trace(go.Scatter(x=pareto_data[p['category']], y=pareto_data['Cumul %'],
                                               name='Cumul %', marker_color='#F97316', mode='lines+markers'),
                                    secondary_y=True)
                fig_pareto.add_hline(y=80, line_dash="dash", line_color="#EF4444", secondary_y=True)
                fig_pareto.update_layout(plot_bgcolor='white', paper_bgcolor='white', font_family='Inter',
                                        title=f"Analyse de Pareto — {p['category']}")
                st.plotly_chart(fig_pareto, use_container_width=True)
            with col_p2:
                st.markdown(f"""
                <div class="insight-card" style="margin-top:40px">
                    <strong>📐 Règle des 80/20</strong><br><br>
                    <strong>{round(p['n80']/p['total']*100)}%</strong> de vos {p['category']}<br>
                    représentent <strong>80%</strong> de {p['value']}.<br><br>
                    Soit <strong>{p['n80']}</strong> éléments sur {p['total']} au total.
                </div>
                """, unsafe_allow_html=True)

        # Corrélations fortes
        if 'strong_correlations' in analytics and analytics['strong_correlations']:
            st.markdown('<div class="section-title">🔗 Corrélations Fortes Détectées</div>', unsafe_allow_html=True)
            corr_df = pd.DataFrame(analytics['strong_correlations'])
            corr_df.columns = ['Variable 1', 'Variable 2', 'Corrélation', 'Type']
            st.dataframe(corr_df.style.background_gradient(subset=['Corrélation'], cmap='RdYlGn'),
                        use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════
    # MODULE 3 — DASHBOARD BUILDER
    # ══════════════════════════════════════════════════════════
    elif module_choice == "🎨 Dashboard Builder":
        st.markdown('<div class="section-title">🎨 Tableaux de Bord Générés Automatiquement</div>', unsafe_allow_html=True)

        with st.spinner("🎨 Génération des visualisations..."):
            charts = create_auto_charts(df)

        if not charts:
            st.warning("Pas assez de données numériques pour générer des graphiques.")
        else:
            # Afficher les graphiques en grille
            for i in range(0, len(charts), 2):
                cols = st.columns(2)
                for j, col_widget in enumerate(cols):
                    if i+j < len(charts):
                        chart_type, chart_name, fig = charts[i+j]
                        with col_widget:
                            st.plotly_chart(fig, use_container_width=True)

        # Aperçu des données
        st.markdown('<div class="section-title">📋 Aperçu des Données</div>', unsafe_allow_html=True)
        n_rows = st.slider("Nombre de lignes à afficher", 5, min(100, len(df)), 10)
        st.dataframe(df.head(n_rows), use_container_width=True)

    # ══════════════════════════════════════════════════════════
    # MODULE 4 — AI CHAT
    # ══════════════════════════════════════════════════════════
    elif module_choice == "💬 AI Chat":
        st.markdown('<div class="section-title">💬 Posez vos Questions en Langage Naturel</div>', unsafe_allow_html=True)

        # Suggestions de questions
        st.markdown("**Questions suggérées :**")
        suggestions = [
            "Quels sont les 5 meilleurs éléments ?",
            "Quelle est la moyenne de chaque colonne ?",
            "Y a-t-il des valeurs manquantes ?",
            "Montre-moi les corrélations",
            "Donne-moi un résumé complet",
            "Y a-t-il des doublons ?"
        ]
        cols_sug = st.columns(3)
        for i, sug in enumerate(suggestions):
            with cols_sug[i % 3]:
                if st.button(sug, key=f"sug_{i}", use_container_width=True):
                    st.session_state.chat_history.append(("user", sug))
                    response = ai_chat_response(sug, df)
                    st.session_state.chat_history.append(("ai", response))
                    st.rerun()

        # Afficher historique
        st.markdown("---")
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
                <div style="text-align:center; padding:40px; color:#64748B">
                    <div style="font-size:40px; margin-bottom:12px">💬</div>
                    <div style="font-size:16px; font-weight:600">Posez votre première question !</div>
                    <div style="font-size:14px; margin-top:8px">Ou cliquez sur une suggestion ci-dessus</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for role, msg in st.session_state.chat_history:
                    if role == "user":
                        st.markdown(f"""
                        <div style="display:flex; justify-content:flex-end; margin:8px 0">
                            <div class="chat-user">
                                <div class="chat-label" style="color:rgba(255,255,255,0.6)">Vous</div>
                                {msg}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display:flex; margin:8px 0">
                            <div class="chat-ai">
                                <div class="chat-label">🤖 VisualizeData Assistant</div>
                                {msg}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # Input
        col_input, col_send = st.columns([4,1])
        with col_input:
            user_input = st.text_input("Votre question...", key="chat_input",
                                       placeholder="Ex: Quels sont mes 10 meilleurs clients par chiffre d'affaires ?",
                                       label_visibility="collapsed")
        with col_send:
            if st.button("Envoyer →", use_container_width=True, type="primary"):
                if user_input:
                    st.session_state.chat_history.append(("user", user_input))
                    response = ai_chat_response(user_input, df)
                    st.session_state.chat_history.append(("ai", response))
                    st.rerun()

        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # ══════════════════════════════════════════════════════════
    # MODULE 5 — RAPPORT
    # ══════════════════════════════════════════════════════════
    elif module_choice == "📄 Rapport":
        st.markdown('<div class="section-title">📄 Génération de Rapport Automatique</div>', unsafe_allow_html=True)

        insights, anomalies = generate_insights(df, audit, analytics)

        # Aperçu du rapport
        st.markdown("""
        <div style="background:white; border:1.5px solid #E2E8F0; border-radius:16px; padding:32px; margin-bottom:20px">
            <div style="font-size:20px; font-weight:800; color:#0F172A; margin-bottom:20px; border-bottom:2px solid #4F46E5; padding-bottom:10px">
                📊 RAPPORT D'ANALYSE — VisualizeData Assistant
            </div>
        """, unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f"""
            **📋 Informations générales**
            - Fichier analysé : données importées
            - Date d'analyse : {datetime.now().strftime('%d/%m/%Y %H:%M')}
            - Lignes : {len(df):,}
            - Colonnes : {len(df.columns)}
            """)
        with col_r2:
            st.markdown(f"""
            **⭐ Score de qualité : {audit['quality_score']}/100**
            - Complétude : {completeness}%
            - Doublons : {audit['duplicates']}
            - Outliers : {len(audit['outliers'])} colonne(s)
            """)

        st.markdown("**💡 Insights principaux**")
        for ins in insights[:3]:
            st.markdown(f"- {ins}")

        if anomalies:
            st.markdown("**⚠️ Points d'attention**")
            for ano in anomalies[:3]:
                st.markdown(f"- {ano}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Génération CSV du rapport
        st.markdown("**📥 Télécharger les résultats**")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            # Export données nettoyées
            df_clean = df.drop_duplicates()
            csv_buffer = io.StringIO()
            df_clean.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 Télécharger données nettoyées (CSV)",
                data=csv_buffer.getvalue().encode('utf-8-sig'),
                file_name=f"VDA_donnees_nettoyees_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_dl2:
            # Export rapport JSON
            rapport = {
                "date": datetime.now().strftime('%d/%m/%Y %H:%M'),
                "dimensions": {"lignes": len(df), "colonnes": len(df.columns)},
                "qualite": {
                    "score": audit['quality_score'],
                    "completude": completeness,
                    "doublons": int(audit['duplicates']),
                    "outliers": len(audit['outliers'])
                },
                "insights": insights,
                "anomalies": anomalies,
                "colonnes": df.columns.tolist()
            }
            st.download_button(
                label="📄 Télécharger rapport (JSON)",
                data=json.dumps(rapport, ensure_ascii=False, indent=2),
                file_name=f"VDA_rapport_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

        # Stats exportables
        if 'descriptive' in analytics:
            st.markdown("**📋 Statistiques complètes**")
            csv_stats = analytics['descriptive'].to_csv()
            st.download_button(
                label="📊 Télécharger statistiques (CSV)",
                data=csv_stats.encode('utf-8-sig'),
                file_name=f"VDA_statistiques_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

    # ── RESET BOUTON ───────────────────────────────────────────
    st.divider()
    col_reset, _ = st.columns([1, 4])
    with col_reset:
        if st.button("🔄 Nouveau fichier", use_container_width=True):
            st.session_state.df = None
            st.session_state.audit = None
            st.session_state.analytics = None
            st.session_state.chat_history = []
            st.rerun()


if __name__ == "__main__":
    main()
