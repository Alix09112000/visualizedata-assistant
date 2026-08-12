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
│       └── config.toml     ← thème VisualizeData (indigo #4F46E5)
├── site/                   ← Site vitrine HTML (Render Static Site)
│   └── index.html          ← site complet + assistant intégré en iframe
├── render.yaml
├── .gitignore
└── README.md
```

## Version 2 de l'assistant — ce qui change

**Design (identité VisualizeData)**
- Typographie Sora / Manrope, indigo `#4F46E5` en accent principal, orange `#F97316` réservé aux insights, fonds `#EEF4FF`.
- Thème Plotly `visualizedata` appliqué à tous les graphiques (indigo en série principale, orange en second).
- Grille modulaire : bandeau de métriques en cellules séparées, colonnes contrôles / graphique.
- Écran d'accueil repensé : zone d'import, quatre fonctionnalités, bloc « exemple de sortie ».
- Thème Streamlit natif dans `.streamlit/config.toml` (couleurs, fond, texte) — l'application et le site partagent la même identité.
- Le CSS et les blocs HTML sont injectés avec `st.html()` et non `st.markdown(unsafe_allow_html=True)` : Streamlit interrompait le bloc HTML à la première ligne vide, ce qui affichait la feuille de style en texte brut dans la page.

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

## Identité de marque

| Usage | Couleur |
| --- | --- |
| Bleu marine principal | `#0F172A` |
| Indigo technologique (accent principal) | `#4F46E5` |
| Orange d'accent (insight, point clé) | `#F97316` |
| Bleu très clair / fonds | `#EEF4FF` |
| Blanc | `#FFFFFF` |

Typographie : **Sora** pour les titres, **Manrope** pour le texte. Signature : *Transformer les données en décisions — Transforming Data Into Decisions.* L'orange reste un accent : insight, progression, point important — jamais une surface.

## Site vitrine — version 2

- Positionnement « partenaire Data & AI pour la décision » : chaîne de valeur Données → Analyse → Visualisation → Insight → Décision → Performance, problèmes traités, 7 services, méthode en 7 étapes, technologies, secteurs.
- L'assistant IA est présenté comme **Projet 01** de VisualizeData (FormaPro en Projet 02), et non comme le produit principal.
- La section `#assistant` présente le projet (parcours en 4 étapes + aperçu de l'écran d'analyse) et **ouvre l'application web dans un nouvel onglet** — pas d'iframe.
- Remplacez l'URL `https://visualizedata-assistant.onrender.com` par l'URL Render réelle : elle apparaît dans le bouton de la barre de navigation et dans les deux liens de la section Assistant.
- Le logo est un V construit en SVG inline (marine + indigo, point orange) : lisible en favicon et en noir et blanc. À remplacer par le logo final quand il sera dessiné.

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
