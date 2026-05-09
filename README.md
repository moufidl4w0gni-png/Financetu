# 📈 FinLearn — Plateforme Académique des Instruments Financiers

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Plateforme éducative pour l'apprentissage des instruments financiers, avec données de marché en temps réel et authentification ENT universitaire.

---

## 🎓 Présentation

**FinLearn** est une application web académique permettant aux étudiants en finance d'apprendre les instruments financiers de manière interactive, avec :

- 📊 **Données de marché en temps réel** (Yahoo Finance)
- 🔐 **Authentification ENT** (protocole CAS)
- 📚 **7 modules pédagogiques** complets
- 🧪 **Quiz interactifs** et exercices pratiques
- 📈 **Simulateur de portefeuille** virtuel
- 📖 **Glossaire** de 80+ termes financiers

---

## 🗂️ Modules disponibles

| Module | Contenu |
|--------|---------|
| 🏠 Tableau de bord | Vue d'ensemble des marchés, progression étudiant |
| 📊 Actions & Marchés | Cours, valorisation (DDM, PER), risque |
| 💼 Obligations | Prix, duration, courbe des taux |
| 🔄 Produits Dérivés | Options (Black-Scholes), futures, swaps |
| 🏦 Fonds d'investissement | OPCVM, ETF, Private Equity, portefeuille |
| 💱 Forex & Crypto | Taux de change, crypto, arbitrage |
| 🏗️ Marchés Monétaires | Bons du Trésor, BCE, taux directeurs |

---

## 🚀 Déploiement rapide

### Option A — Streamlit Cloud (recommandé, gratuit)

**1. Forker ce dépôt sur GitHub**
```
https://github.com/VOTRE_NOM/finlearn
```

**2. Aller sur [share.streamlit.io](https://share.streamlit.io)**
- Se connecter avec GitHub
- "New app" → sélectionner le repo → fichier `app.py`
- Cliquer "Deploy !"

**3. Configurer les secrets (Settings → Secrets)**
```toml
[auth]
allow_all_university_emails = true

[cas]
url = "https://cas.votre-universite.fr"
service = "https://votre-app.streamlit.app"
```

### Option B — Lancement local

```bash
# 1. Cloner
git clone https://github.com/VOTRE_NOM/finlearn.git
cd finlearn

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Dépendances
pip install -r requirements.txt

# 4. Lancer
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`

---

## 🔐 Authentification ENT

### Comptes de démonstration (accès immédiat)

| Email | Mot de passe | Rôle |
|-------|-------------|------|
| `etudiant@demo.finlearn.edu` | `demo2025` | Étudiant |
| `prof@demo.finlearn.edu` | `prof2025` | Enseignant |
| `admin@demo.finlearn.edu` | `admin2025` | Admin |

### Connexion avec ENT réel (CAS)

Configurez l'URL de votre serveur CAS dans `.streamlit/secrets.toml` :
```toml
[cas]
url = "https://cas.cyu.fr"          # CY Cergy
# url = "https://cas.univ-paris1.fr" # Paris 1
# url = "https://sso.hec.edu"         # HEC
```

### Mode ouvert (emails universitaires)

Activez `allow_all_university_emails = true` dans les secrets pour accepter tous les emails en `.fr` ou `.edu` sans vérification CAS.

---

## 📁 Structure du projet

```
finlearn/
├── app.py                      # Point d'entrée principal
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
├── .gitignore                  # Fichiers ignorés par Git
│
├── .streamlit/
│   ├── config.toml             # Thème et configuration
│   └── secrets.toml            # Secrets (ne pas committer !)
│
├── utils/
│   ├── auth.py                 # Authentification ENT / CAS
│   ├── styles.py               # CSS global
│   └── market_data.py          # Données Yahoo Finance
│
└── pages/
    ├── dashboard.py            # Tableau de bord
    ├── actions.py              # Module Actions
    ├── obligations.py          # Module Obligations
    ├── derives.py              # Module Dérivés
    ├── fonds.py                # Module Fonds
    ├── forex.py                # Module Forex & Crypto
    ├── monetaire.py            # Module Marché Monétaire
    ├── quiz.py                 # Quiz interactifs
    ├── simulateur.py           # Simulateur de portefeuille
    └── glossaire.py            # Glossaire financier
```

---

## ⚙️ Configuration avancée

### Variables d'environnement / Secrets Streamlit Cloud

```toml
# .streamlit/secrets.toml

[auth]
allow_all_university_emails = true   # true = mode ouvert, false = CAS uniquement

[cas]
url = ""           # URL du serveur CAS de votre université
service = ""       # URL de votre app Streamlit Cloud

ANTHROPIC_API_KEY = ""   # Optionnel : pour fonctionnalités IA futures
```

### Ajouter une université partenaire

Dans `utils/auth.py`, ajoutez le domaine à `DOMAINES_AUTORISÉS` :
```python
DOMAINES_AUTORISÉS = [
    "cyu.fr",
    "votre-universite.fr",  # ← Ajouter ici
    ...
]
```

---

## 📊 Sources de données

- **Yahoo Finance** via `yfinance` : cours actions, indices, forex, crypto
- **Données calculées** : obligations, options (Black-Scholes), simulations
- Mise à jour automatique avec cache Streamlit (60s pour les cours, 5min pour l'historique)

> ⚠️ Données à des fins **éducatives uniquement**. Non destinées au conseil en investissement.

---

## 🤝 Contribution

1. Forker le projet
2. Créer une branche (`git checkout -b feature/nouveau-module`)
3. Committer (`git commit -m 'Ajout module XYZ'`)
4. Pousser (`git push origin feature/nouveau-module`)
5. Ouvrir une Pull Request

---

## 📄 Licence

MIT — Libre d'utilisation pour l'enseignement académique.

---

## 👨‍💻 Auteur

Développé pour **CY Cergy Paris Université** · Département Économie-Finance  
Contact : [support@finlearn.edu](mailto:support@finlearn.edu)
