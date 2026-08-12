# VisualizeData

> Transformez vos données en décisions stratégiques.

## Structure du repo

```
visualizedata-assistant/
├── app/                    ← Assistant IA Streamlit (Render Web Service)
│   ├── app.py
│   ├── requirements.txt
│   ├── .python-version
│   └── .streamlit/
│       └── config.toml     ← thème Modernist (accent #ec3013, angles à 0)
├── site/                   ← Site vitrine HTML (Render Static Site)
│   └── index.html
├── render.yaml
├── .gitignore
└── README.md
```

## Version 2 de l'assistant — ce qui change

**Design (système Modernist)**
- Typographie Archivo, accent rouge unique `#ec3013`, aucun angle arrondi, filets de 2 px.
- Thème Plotly `modernist` appliqué à tous les graphiques (axes à filets, palette à plat).
- Grille modulaire : bandeau de métriques en cellules séparées, colonnes contrôles / graphique.
- Écran d'accueil repensé : zone d'import, quatre fonctionnalités, bloc « exemple de sortie ».
- Thème Streamlit natif dans `.streamlit/config.toml` (couleurs, fond, texte).

**Analyse**
- Détection automatique des colonnes de dates (`coerce_dates`).
- Constats automatiques : variable la plus incomplète, doublons, valeurs extrêmes (IQR), corrélation la plus forte, période couverte.
- Onglet Qualité : complétude par variable en barres, table des valeurs extrêmes.
- Onglet Statistiques : corrélations principales + matrice de corrélation.
- Onglet Visualisations : histogramme (classes réglables, découpage), nuage de points (tendance OLS), boîte à moustaches, série temporelle avec granularité et agrégation.
- Choix de la feuille pour les classeurs Excel multi-feuilles.
- Lecture CSV plus robuste (utf-8, utf-8-sig, latin-1) et mise en cache (`st.cache_data`).

**Assistant IA**
- Conversation suivie : historique en `st.session_state`, `st.chat_input`, réponse en streaming.
- Questions suggérées en un clic.
- Contexte enrichi envoyé au modèle : corrélations, valeurs extrêmes, doublons, plages de dates.
- Prompt système orienté décision : constat → chiffre → implication → une recommandation.
- Rappel explicite : seul un résumé statistique et un échantillon de 12 lignes sont transmis.

**Export**
- Rapport Markdown téléchargeable (vue d'ensemble, constats, qualité, statistiques, échanges IA).
- Export CSV du jeu de données dédoublonné.

## Déploiement sur Render

```bash
git add .
git commit -m "feat: assistant v2 — design Modernist + analyses enrichies"
git push origin main
```

- Render → New → Blueprint → sélectionner ce repo (`render.yaml` crée les 2 services).
- Dans Render > visualizedata-assistant > Environment : `OPENAI_API_KEY` = votre clé (jamais dans le code).
- `OPENAI_MODEL` est déjà défini sur `gpt-4o-mini` ; changez-le pour un autre modèle si besoin.
- Une fois l'assistant déployé, remplacez `https://visualizedata-assistant.onrender.com` dans `site/index.html` par votre vraie URL.

## Lancer localement

```bash
cd app
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
streamlit run app.py
```

## Stack
- Python · Streamlit · Pandas · Plotly · statsmodels · OpenAI API
- Site vitrine : HTML/CSS vanilla
- Hébergement : Render (Static Site + Web Service)
