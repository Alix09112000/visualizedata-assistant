# Implémenter l'application (design Modernist)

## Fichiers à remplacer dans votre repo

| Fichier | Action |
| --- | --- |
| `app/app.py` | remplacer entièrement |
| `app/.streamlit/config.toml` | créer (nouveau dossier `.streamlit/`) |
| `app/requirements.txt` | remplacer (ajoute statsmodels, tabulate) |
| `render.yaml` | remplacer |
| `README.md` | remplacer |

Le site vitrine (`site/index.html`) est à refaire dans un second temps — on y passe maintenant.

## Déploiement

```bash
cd visualizedata-assistant
git add .
git commit -m "feat: refonte design de l'assistant (Modernist)"
git push origin main
```

Puis sur Render : **Manual Deploy → Clear build cache & deploy** (sinon l'ancien CSS reste en cache).

## Vérifications après déploiement

1. La page s'affiche en Archivo, fond `#f3f2f2`, accent rouge `#ec3013`, aucun angle arrondi.
2. Aucun bloc de CSS visible en texte dans la page — tout passe par `st.html()`.
3. Les graphiques Plotly reprennent la palette (rouge en série principale).
4. `OPENAI_API_KEY` est bien définie dans Render → Environment, sinon l'onglet Assistant IA affiche un avertissement.

## Local

```bash
cd app
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
streamlit run app.py
```

Streamlit 1.33 minimum est requis (`st.html`).

## Écrans de référence

Le design complet — version web 1440 px et version iPhone 402 × 874 (import, analyse, graphiques, assistant, rapports, connexion Google), plus les états accueil, erreur de lecture, export et réglages — est dans `Assistant App.dc.html` à la racine du projet de design.
