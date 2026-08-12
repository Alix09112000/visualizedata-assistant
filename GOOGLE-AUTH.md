# Activer la connexion Google — pas à pas

## 1. Créer l'identifiant OAuth

1. Ouvrez <https://console.cloud.google.com/apis/credentials>
2. Sélectionnez ou créez un projet (nom libre, ex. « VisualizeData »).
3. Si demandé : **OAuth consent screen** → *External* → nom de l'app « VisualizeData Assistant », votre e-mail d'assistance, *Save*. Publiez en *Testing* et ajoutez votre adresse dans *Test users* (ou *Publish app* pour ouvrir à tous).
4. **Credentials** → *Create credentials* → **OAuth client ID** → type **Web application**.
5. Dans **Authorized redirect URIs**, ajoutez exactement ces deux lignes :

```
https://visualizedata-assistant.onrender.com/oauth2callback
http://localhost:8501/oauth2callback
```

6. *Create* → notez le **Client ID** et le **Client secret**.

## 2. Générer le cookie_secret

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 3. Créer le fichier de secrets

Contenu final (remplacez les trois valeurs) :

```toml
[auth]
redirect_uri = "https://visualizedata-assistant.onrender.com/oauth2callback"
cookie_secret = "COLLEZ_ICI_LA_CHAINE_GENEREE"

[auth.google]
client_id = "VOTRE_CLIENT_ID.apps.googleusercontent.com"
client_secret = "VOTRE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

## 4. Déposer le fichier sur Render

Ce fichier ne doit **jamais** être commité (il est dans `.gitignore`).

Render n'accepte ni les `/` ni le `.` initial dans le nom d'un Secret File. On dépose donc le fichier à plat et la commande de démarrage le recopie au bon endroit.

1. Render → service `visualizedata-assistant` → **Environment**
2. Section **Secret Files** → *Add file*
3. **Filename** : `secrets.toml` (rien d'autre — pas de dossier, pas de point devant)
4. **Contents** : collez le TOML de l'étape 3.
5. *Save, rebuild and deploy*.

Render place le fichier dans `/etc/secrets/secrets.toml`. Le `startCommand` de `render.yaml` fait :

```
mkdir -p .streamlit && cp /etc/secrets/secrets.toml .streamlit/secrets.toml && streamlit run app.py …
```

Si votre service a été créé à la main (sans Blueprint), reportez cette commande dans **Settings → Start Command**.

## 5. Vérifier

- Le pied de page doit afficher **build modernist-4 · connexion Google requise**.
- L'écran d'accueil affiche « Connectez-vous pour analyser vos données » avec le bouton **Continuer avec Google**.
- Après connexion, votre nom et votre adresse apparaissent dans la barre latérale avec un bouton *Se déconnecter*.

## En cas d'erreur

| Message | Cause |
| --- | --- |
| `redirect_uri_mismatch` | L'URI dans Google Cloud ne correspond pas exactement à `redirect_uri` du TOML (attention au `https`, au domaine et à `/oauth2callback`). |
| Écran de configuration toujours affiché | Le fichier de secrets n'est pas lu : vérifiez le chemin, puis **Clear build cache & deploy**. |
| `Authlib` introuvable | `requirements.txt` doit contenir `streamlit>=1.42` et `Authlib>=1.3` — refaites le build sans cache. |
| `access_blocked` | Votre adresse n'est pas dans *Test users* de l'écran de consentement. |

## Test en local

Placez le même TOML dans `app/.streamlit/secrets.toml` avec
`redirect_uri = "http://localhost:8501/oauth2callback"`, puis :

```bash
cd app
streamlit run app.py
```
