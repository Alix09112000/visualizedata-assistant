# VisualizeData Assistant

MVP d'un assistant IA spécialisé en analyse de données.

## Fonctionnalités

- Import CSV / Excel
- Aperçu du dataset
- Audit des valeurs manquantes et doublons
- Statistiques descriptives
- Visualisations Plotly
- Questions en langage naturel avec l'API OpenAI

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Render

Créez un **Web Service** à partir du dépôt GitHub.

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

Ajoutez dans Render > Environment :

- `OPENAI_API_KEY` : votre clé API OpenAI
- `OPENAI_MODEL` : optionnel, par défaut `gpt-5-mini`

Ne placez jamais votre clé API directement dans le code ou dans GitHub.
