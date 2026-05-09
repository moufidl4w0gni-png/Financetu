"""
Système d'authentification ENT
================================
Supporte :
- Authentification CAS (protocole standard ENT français)
- Mode démonstration (pour tests sans ENT réel)
- Validation des emails universitaires
"""

import streamlit as st
import re
import hashlib
import requests
from datetime import datetime

# Domaines universitaires autorisés
DOMAINES_AUTORISÉS = [
    "cyu.fr", "u-cergy.fr",
    "dauphine.eu", "dauphine.psl.eu",
    "univ-paris1.fr",
    "hec.edu",
    "sciencespo.fr",
    "univ-lyon1.fr", "univ-lyon2.fr", "univ-lyon3.fr",
    "univ-paris-saclay.fr",
    "sorbonne-universite.fr",
    "univ-bordeaux.fr",
    "univ-lille.fr",
    "univ-nantes.fr",
    "univ-rennes1.fr",
    # Mode démo
    "demo.finlearn.edu",
    "etudiant.fr",
    "etu.univ.fr",
]

# Comptes de démonstration (pour tests / présentation)
COMPTES_DEMO = {
    "etudiant@demo.finlearn.edu": {
        "password_hash": hashlib.sha256("demo2025".encode()).hexdigest(),
        "prenom": "Alex",
        "nom": "Dupont",
        "formation": "L3 Éco-Finance",
        "annee": "2024-2025",
        "universite": "CY Cergy Paris Université",
        "numero_etudiant": "20240001",
        "email": "etudiant@demo.finlearn.edu",
        "role": "etudiant",
        "progression": 35,
        "modules_completes": ["actions", "obligations"],
        "score_moyen": 14.5,
    },
    "prof@demo.finlearn.edu": {
        "password_hash": hashlib.sha256("prof2025".encode()).hexdigest(),
        "prenom": "Marie",
        "nom": "Martin",
        "formation": "Enseignant-Chercheur",
        "annee": "2024-2025",
        "universite": "CY Cergy Paris Université",
        "numero_etudiant": "E00001",
        "email": "prof@demo.finlearn.edu",
        "role": "enseignant",
        "progression": 100,
        "modules_completes": ["actions", "obligations", "derives", "fonds", "forex", "monetaire"],
        "score_moyen": 18.0,
    },
    "admin@demo.finlearn.edu": {
        "password_hash": hashlib.sha256("admin2025".encode()).hexdigest(),
        "prenom": "Jean",
        "nom": "Admin",
        "formation": "Administrateur",
        "annee": "2024-2025",
        "universite": "FinLearn",
        "numero_etudiant": "A00001",
        "email": "admin@demo.finlearn.edu",
        "role": "admin",
        "progression": 100,
        "modules_completes": [],
        "score_moyen": 20.0,
    }
}


def valider_format_identifiant(identifiant: str) -> tuple[bool, str]:
    """Valide le format de l'identifiant ENT."""
    identifiant = identifiant.strip().lower()

    # Email universitaire
    if "@" in identifiant:
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, identifiant):
            return False, "Format d'email invalide."
        domaine = identifiant.split("@")[1]
        # Accepte tous les domaines en .fr ou .edu ou ceux listés
        if not (domaine.endswith(".fr") or domaine.endswith(".edu") or
                domaine in DOMAINES_AUTORISÉS):
            return False, (f"Le domaine '@{domaine}' n'est pas reconnu. "
                           "Utilisez votre email universitaire ou le compte démo.")
        return True, identifiant

    # Numéro étudiant (8-10 chiffres)
    if re.match(r'^\d{7,12}$', identifiant):
        return True, identifiant

    return False, "Identifiant non reconnu. Utilisez votre email universitaire ou numéro étudiant."


def verifier_connexion_demo(identifiant: str, mot_de_passe: str):
    """Vérifie les comptes de démonstration."""
    id_lower = identifiant.lower()
    if id_lower in COMPTES_DEMO:
        compte = COMPTES_DEMO[id_lower]
        hash_fourni = hashlib.sha256(mot_de_passe.encode()).hexdigest()
        if hash_fourni == compte["password_hash"]:
            user_data = {k: v for k, v in compte.items() if k != "password_hash"}
            user_data["connexion_time"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            return True, user_data, "Connexion réussie"
    return False, None, None


def verifier_connexion_cas(identifiant: str, mot_de_passe: str, url_cas: str = None):
    """
    Authentification via protocole CAS (Central Authentication Service).
    Utilisé par la majorité des ENT français.

    En production, configurez l'URL CAS de votre université dans les secrets Streamlit :
    [cas]
    url = "https://cas.votre-universite.fr"
    service = "https://votre-app.streamlit.app"
    """
    try:
        cas_url = url_cas or st.secrets.get("cas", {}).get("url", "")
        if not cas_url:
            return False, None, "URL CAS non configurée"

        # Étape 1 : Demande de ticket CAS
        login_url = f"{cas_url}/login"
        session = requests.Session()

        # Récupération du formulaire
        r = session.get(login_url, timeout=10)
        if r.status_code != 200:
            return False, None, "Service ENT inaccessible"

        # Extraction du token CSRF si présent
        lt_match = re.search(r'name="lt" value="([^"]+)"', r.text)
        execution_match = re.search(r'name="execution" value="([^"]+)"', r.text)

        payload = {
            "username": identifiant,
            "password": mot_de_passe,
            "_eventId": "submit",
            "submit": "LOGIN",
        }
        if lt_match:
            payload["lt"] = lt_match.group(1)
        if execution_match:
            payload["execution"] = execution_match.group(1)

        # Étape 2 : Soumission des credentials
        r2 = session.post(login_url, data=payload, allow_redirects=True, timeout=10)

        if "ticket=" in r2.url or "ST-" in r2.text:
            # Succès — construction du profil depuis CAS
            user_data = {
                "prenom": "Étudiant",
                "nom": identifiant.split("@")[0].replace(".", " ").title() if "@" in identifiant else "ENT",
                "email": identifiant if "@" in identifiant else f"{identifiant}@ent.univ.fr",
                "formation": "Via ENT",
                "annee": "2024-2025",
                "universite": "Université partenaire",
                "role": "etudiant",
                "progression": 0,
                "modules_completes": [],
                "score_moyen": 0,
                "connexion_time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            return True, user_data, "Connexion ENT réussie"

        if "invalid.credentials" in r2.text.lower() or "bad.credentials" in r2.text.lower():
            return False, None, "Identifiant ou mot de passe incorrect."

        return False, None, "Connexion ENT échouée. Vérifiez vos identifiants."

    except requests.exceptions.ConnectionError:
        return False, None, "Impossible de joindre le serveur ENT. Vérifiez votre connexion."
    except requests.exceptions.Timeout:
        return False, None, "Le serveur ENT ne répond pas. Réessayez dans quelques instants."
    except Exception as e:
        return False, None, f"Erreur de connexion : {str(e)[:80]}"


def verifier_connexion(identifiant: str, mot_de_passe: str) -> tuple:
    """
    Point d'entrée principal de l'authentification.
    Essaie dans l'ordre :
    1. Comptes de démonstration
    2. Authentification CAS ENT
    3. Validation basique (si ENT indisponible)
    """
    if not identifiant or not mot_de_passe:
        return False, None, "Veuillez remplir tous les champs."

    # Validation du format
    valide, identifiant_clean = valider_format_identifiant(identifiant)
    if not valide:
        return False, None, identifiant_clean  # identifiant_clean contient le message d'erreur

    # 1. Vérification comptes démo
    succes, user_data, message = verifier_connexion_demo(identifiant_clean, mot_de_passe)
    if succes:
        return True, user_data, message

    # 2. Tentative CAS ENT
    try:
        cas_url = st.secrets.get("cas", {}).get("url", "")
        if cas_url:
            succes, user_data, message = verifier_connexion_cas(identifiant_clean, mot_de_passe, cas_url)
            if succes:
                return True, user_data, message
            if "incorrect" in message.lower() or "invalide" in message.lower():
                return False, None, message
    except Exception:
        pass

    # 3. Mode permissif (si ENT non configuré) — pour démo / développement
    try:
        allow_all = st.secrets.get("auth", {}).get("allow_all_university_emails", False)
    except Exception:
        allow_all = True  # En dev, on autorise tout

    if allow_all and "@" in identifiant_clean:
        domaine = identifiant_clean.split("@")[1]
        if domaine.endswith(".fr") or domaine.endswith(".edu"):
            nom_parts = identifiant_clean.split("@")[0].replace(".", " ").replace("-", " ")
            parts = nom_parts.split()
            user_data = {
                "prenom": parts[0].capitalize() if parts else "Étudiant",
                "nom": parts[1].capitalize() if len(parts) > 1 else "Universitaire",
                "email": identifiant_clean,
                "formation": "Licence / Master",
                "annee": "2024-2025",
                "universite": f"Université ({domaine})",
                "role": "etudiant",
                "progression": 0,
                "modules_completes": [],
                "score_moyen": 0,
                "connexion_time": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            return True, user_data, "Connexion acceptée"

    return (
        False,
        None,
        "Identifiant ou mot de passe incorrect. "
        "Utilisez vos identifiants ENT ou le compte démo : "
        "etudiant@demo.finlearn.edu / demo2025"
    )


def deconnecter():
    """Déconnecte l'utilisateur et réinitialise la session."""
    for key in ["authenticated", "user", "page", "login_attempts"]:
        if key in st.session_state:
            del st.session_state[key]


def get_user_info():
    """Retourne les informations de l'utilisateur connecté."""
    return st.session_state.get("user", {})


def require_auth():
    """Décorateur : redirige vers login si non connecté."""
    if not st.session_state.get("authenticated", False):
        st.error("🔒 Accès non autorisé. Veuillez vous connecter.")
        st.stop()
