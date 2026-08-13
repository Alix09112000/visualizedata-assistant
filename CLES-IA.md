# Ajouter une clé IA

Sans clé, l'assistant fonctionne en **Analyse locale** : les réponses sont calculées sur vos statistiques, sans appel externe. Une clé sert uniquement à obtenir une réponse rédigée en langage naturel.

## Quel fournisseur choisir

| Fournisseur | Coût | Variable à créer | Modèle utilisé |
| --- | --- | --- | --- |
| **Groq** | Gratuit (quota généreux) | `GROQ_API_KEY` | llama-3.3-70b-versatile |
| **Google Gemini** | Gratuit (quota) | `GEMINI_API_KEY` | gemini-2.0-flash |
| **Mistral** | Gratuit puis payant | `MISTRAL_API_KEY` | mistral-small-latest |
| **OpenRouter** | Crédit prépayé | `OPENROUTER_API_KEY` | llama-3.3-70b-instruct |
| **OpenAI** | Payant à l'usage | `OPENAI_API_KEY` | gpt-4o-mini |

Recommandation : **Groq** pour la rapidité et la gratuité, **Gemini** si vous avez déjà un compte Google.

---

## 1. Obtenir la clé

### Groq
1. <https://console.groq.com>
2. *Sign in with Google* (ou GitHub).
3. Menu gauche → **API Keys** → **Create API Key**.
4. Nom libre (ex. « VisualizeData ») → *Submit*.
5. Copiez la clé immédiatement — elle commence par `gsk_` et ne sera plus jamais affichée.

### Google Gemini
1. <https://aistudio.google.com/apikey>
2. **Create API key** → choisissez un projet (ou laissez-le créer le sien).
3. Copiez la clé — elle commence par `AIza`.

### Mistral
1. <https://console.mistral.ai> → *La Plateforme* → **API Keys** → *Create new key*.
2. Une carte bancaire peut être demandée pour valider le compte.

### OpenAI
1. <https://platform.openai.com/api-keys> → **Create new secret key**.
2. Nécessite un crédit prépayé dans *Billing* (5 $ suffisent largement).
3. La clé commence par `sk-`.

---

## 2. Enregistrer la clé dans Render

1. Ouvrez votre service **visualizedata-assistant** sur <https://dashboard.render.com>
2. Onglet **Environment** (menu de gauche).
3. Section **Environment Variables** → **+ Add Environment Variable**.
4. Remplissez :
   - **Key** : `GROQ_API_KEY` (le nom exact du tableau ci-dessus, en majuscules)
   - **Value** : la clé copiée, sans espace ni guillemets
5. **Save, rebuild and deploy**.

Vous pouvez ajouter plusieurs clés : chaque fournisseur configuré apparaîtra dans le menu déroulant de l'application.

---

## 3. Vérifier

1. Rechargez l'application, importez un fichier.
2. Barre latérale → section **Moteur d'analyse** : le fournisseur doit apparaître dans la liste à côté de « Analyse locale (sans clé) ».
3. Sélectionnez-le, allez dans l'onglet **Assistant IA**, posez une question.

---

## En cas de problème

| Symptôme | Cause probable |
| --- | --- |
| Le fournisseur n'apparaît pas dans la liste | Nom de variable incorrect (respectez les majuscules) ou déploiement non relancé. |
| `401 Unauthorized` | Clé mal copiée, ou révoquée côté fournisseur. |
| `429 Too Many Requests` | Quota gratuit atteint — réessayez plus tard ou changez de fournisseur. |
| `model not found` | Le modèle par défaut n'est pas disponible sur votre compte : modifiez la valeur `model` du fournisseur dans le dictionnaire `PROVIDERS` en haut de `app/app.py`. |

---

## Sécurité

- Ne mettez **jamais** une clé dans le code ni dans un fichier commité — uniquement dans Render → Environment.
- Si une clé fuite, révoquez-la chez le fournisseur et créez-en une nouvelle.
- L'assistant n'envoie au modèle qu'un résumé statistique et un échantillon de 12 lignes : jamais le fichier complet.

## En local

```bash
cd app
export GROQ_API_KEY="gsk_votre_cle"
streamlit run app.py
```

Sous Windows PowerShell : `$env:GROQ_API_KEY = "gsk_votre_cle"`
