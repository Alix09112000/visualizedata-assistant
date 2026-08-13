# Ouvrir l'application au public

## 1. Variables à ajouter dans Render → Environment

### Moteur IA (au moins une)
| Variable | Où l'obtenir |
| --- | --- |
| `GROQ_API_KEY` | <https://console.groq.com/keys> — gratuit, recommandé |
| `GEMINI_API_KEY` | <https://aistudio.google.com/apikey> |
| `OPENAI_API_KEY` | <https://platform.openai.com/api-keys> — payant |

### Retours par e-mail
Créez un compte **Resend** (<https://resend.com>, 3 000 e-mails gratuits par mois) ou **Brevo**
(<https://brevo.com>, 300 par jour), puis ajoutez :

| Variable | Valeur Resend | Valeur Brevo |
| --- | --- | --- |
| `SMTP_HOST` | `smtp.resend.com` | `smtp-relay.brevo.com` |
| `SMTP_PORT` | `587` | `587` |
| `SMTP_USER` | `resend` | votre identifiant SMTP Brevo |
| `SMTP_PASSWORD` | votre clé API Resend | votre clé SMTP Brevo |
| `SMTP_FROM` | `onboarding@resend.dev` au début, puis une adresse de votre domaine | une adresse vérifiée |
| `FEEDBACK_TO` | `mdjoman@upb.ci` | `mdjoman@upb.ci` |

Sans ces variables, l'application fonctionne normalement : les retours sont simplement
conservés dans la session au lieu d'être envoyés.

## 2. Limites en place

- Fichier : 50 Mo maximum, message clair au-delà.
- Questions à l'IA : 30 par session, puis bascule sur l'analyse locale.
- Ces valeurs se changent en haut de `app/app.py` (`MAX_UPLOAD_MB`, `MAX_AI_QUESTIONS`).

## 3. Ce qui est collecté

Trois signaux, tous envoyés à `FEEDBACK_TO` :

1. **Exemple chargé** — quel jeu de démonstration attire le plus.
2. **Réponse utile / inutile** — sous chaque réponse de l'assistant, avec la question posée.
3. **Remarque de fin de session** — « Qu'est-ce qui vous manque ? », une fois par session.

Aucune donnée du fichier de l'utilisateur n'est transmise : seuls la question, la réponse
et la remarque le sont.

## 4. Avant de diffuser

- [ ] Une clé IA configurée et testée.
- [ ] Les variables SMTP configurées, un retour de test reçu.
- [ ] Le message sur le réveil de l'instance vérifié sur la page d'accueil.
- [ ] Les quatre exemples chargés une fois chacun.
- [ ] L'URL du site vitrine pointant vers la bonne adresse Render.

## 5. Diffusion

Commencez par une dizaine de personnes avec un fichier de leur métier, en les regardant
faire sans les aider. Ouvrez ensuite largement : LinkedIn, groupes de PME, page vitrine.
Relevez les retours chaque semaine et publiez ce que vous corrigez dans la section
« Nouveautés » de l'application — c'est ce qui fait revenir les gens.
