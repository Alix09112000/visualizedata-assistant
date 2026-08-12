# VisualizeData

> Transformez vos données en décisions stratégiques.

## Structure du repo

```
visualizedata/
├── site/               ← Site vitrine HTML (Render Static Site)
│   └── index.html
├── app/                ← Assistant IA Streamlit (Render Web Service)
│   ├── app.py
│   ├── requirements.txt
│   └── .python-version
├── render.yaml         ← Config des 2 services Render
├── .gitignore
└── README.md
```

## Déploiement sur Render

### 1. Pousser sur GitHub
```bash
git add .
git commit -m "feat: site vitrine + assistant IA"
git push origin main
```

### 2. Créer les services sur Render
- Aller sur https://render.com
- New → Blueprint → sélectionner ce repo
- Render lit automatiquement `render.yaml` et crée les 2 services

### 3. Configurer la clé OpenAI
Dans Render > visualizedata-assistant > Environment :
- `OPENAI_API_KEY` = votre clé OpenAI (ne jamais la mettre dans le code)

### 4. Mettre à jour l'URL dans le site
Une fois l'assistant déployé, copier son URL Render et remplacer dans `site/index.html` :
```
https://visualizedata-assistant.onrender.com
```
par votre vraie URL.

## Lancer localement

```bash
cd app
pip install -r requirements.txt
streamlit run app.py
```

## Stack
- Python · Streamlit · Pandas · Plotly · OpenAI API
- Site vitrine : HTML/CSS vanilla
- Hébergement : Render (Static Site + Web Service)
