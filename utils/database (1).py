"""
utils/database.py
==================
Base de données SQLite pour FinLearn.
Gère : utilisateurs, accès aux modules, scores, progression.

SQLite est intégré à Python — aucune installation externe requise.
Le fichier finlearn.db est créé automatiquement au premier lancement.
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CHEMIN DE LA BASE DE DONNÉES
# En local  : fichier finlearn.db dans le dossier du projet
# Streamlit Cloud : /tmp/finlearn.db (réinitialisé à chaque restart)
# ─────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("FINLEARN_DB", "finlearn.db")

# ─────────────────────────────────────────────────────────────
# LISTE DES MODULES DISPONIBLES
# ─────────────────────────────────────────────────────────────
MODULES = [
    "dashboard",
    "actions",
    "obligations",
    "derives",
    "fonds",
    "forex",
    "monetaire",
    "quiz",
    "simulateur",
    "glossaire",
]

# Modules toujours accessibles (même sans autorisation prof)
MODULES_LIBRES = ["dashboard", "glossaire" , "quiz"]


def get_connection():
    """
    Retourne une connexion SQLite.
    check_same_thread=False est nécessaire pour Streamlit
    qui utilise plusieurs threads.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


def init_db():
    """
    Initialise la base de données en créant toutes les tables
    si elles n'existent pas encore.
    Appelé au démarrage de l'application.
    """
    conn = get_connection()
    c = conn.cursor()

    # ── TABLE users ──────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            nom           TEXT NOT NULL,
            prenom        TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'etudiant',
            formation     TEXT,
            universite    TEXT,
            annee         TEXT,
            password_hash TEXT,
            actif         INTEGER DEFAULT 1,
            created_at    TEXT DEFAULT (datetime('now')),
            last_login    TEXT
        )
    """)

    # ── TABLE module_access ───────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS module_access (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id   INTEGER NOT NULL,
            module_key    TEXT NOT NULL,
            debloque      INTEGER DEFAULT 0,
            debloque_par  INTEGER,
            debloque_le   TEXT,
            FOREIGN KEY (etudiant_id) REFERENCES users(id),
            FOREIGN KEY (debloque_par) REFERENCES users(id),
            UNIQUE(etudiant_id, module_key)
        )
    """)

    # ── TABLE quiz_results ────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id   INTEGER NOT NULL,
            module_key    TEXT NOT NULL,
            score         REAL NOT NULL,
            score_max     REAL NOT NULL,
            nb_questions  INTEGER,
            nb_correctes  INTEGER,
            theme         TEXT,
            note_prof     REAL,
            commentaire   TEXT,
            passe_le      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (etudiant_id) REFERENCES users(id)
        )
    """)

    # ── TABLE progression ─────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS progression (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id     INTEGER NOT NULL,
            module_key      TEXT NOT NULL,
            pct_complete    REAL DEFAULT 0,
            nb_visites      INTEGER DEFAULT 0,
            temps_passe     INTEGER DEFAULT 0,
            derniere_visite TEXT,
            FOREIGN KEY (etudiant_id) REFERENCES users(id),
            UNIQUE(etudiant_id, module_key)
        )
    """)

    # ── TABLE notifications ───────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            destinataire_id INTEGER,
            expediteur_id   INTEGER NOT NULL,
            message         TEXT NOT NULL,
            lu              INTEGER DEFAULT 0,
            cree_le         TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (destinataire_id) REFERENCES users(id),
            FOREIGN KEY (expediteur_id)   REFERENCES users(id)
        )
    """)

    conn.commit()
    _inserer_donnees_initiales(conn)
    conn.close()


def _inserer_donnees_initiales(conn):
    """Insère les comptes par défaut si la base est vide."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        return

    hash_prof = hashlib.sha256("prof2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("prof@demo.finlearn.edu", "Martin", "Marie", "professeur", "Enseignant-Chercheur Finance", "CY Cergy Paris Université", hash_prof))

    hash_etu = hashlib.sha256("demo2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("etudiant@demo.finlearn.edu", "Dupont", "Alex", "etudiant", "L3 Éco-Finance", "CY Cergy Paris Université", hash_etu))

    conn.commit()

    c.execute("SELECT id FROM users WHERE email = ?", ("etudiant@demo.finlearn.edu",))
    row = c.fetchone()
    if row:
        etu_id = row["id"]
        for mod in MODULES:
            debloque = 1 if mod in MODULES_LIBRES else 0
            c.execute("""
                INSERT OR IGNORE INTO module_access (etudiant_id, module_key, debloque)
                VALUES (?, ?, ?)
            """, (etu_id, mod, debloque))
        conn.commit()


# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILISATEURS (MOCKÉES / SIMULÉES POUR LE MODE DÉMO)
# ─────────────────────────────────────────────────────────────

def get_user_by_email(email: str) -> dict | None:
    """Retourne un utilisateur par son email, ou None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND actif = 1", (email.lower(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_or_update_user(email: str, nom: str, prenom: str,
                          role: str = "etudiant", formation: str = "",
                          universite: str = "") -> int:
    """Crée un nouvel utilisateur ou met à jour sa dernière connexion."""
    conn = get_connection()
    c = conn.cursor()
    email = email.lower()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if row:
        c.execute("""
            UPDATE users SET last_login = ?, nom = ?, prenom = ?
            WHERE email = ?
        """, (now, nom, prenom, email))
        user_id = row["id"]
    else:
        c.execute("""
            INSERT INTO users (email, nom, prenom, role, formation, universite, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email, nom, prenom, role, formation, universite, now))
        user_id = c.lastrowid

        for mod in MODULES:
            debloque = 1 if mod in MODULES_LIBRES else 0
            c.execute("""
                INSERT OR IGNORE INTO module_access (etudiant_id, module_key, debloque)
                VALUES (?, ?, ?)
            """, (user_id, mod, debloque))

    conn.commit()
    conn.close()
    return user_id


def get_all_etudiants():
    """Retourne la liste complète des étudiants simulés (Requis par prof_dashboard)."""
    from utils.auth import COMPTES_DEMO
    
    rows = []
    for email, infos in COMPTES_DEMO.items():
        if infos.get("role") == "etudiant":
            liste_modules = infos.get("modules_completes", [])
            nb_modules = len(liste_modules)
            id_etudiant = infos.get("numero_etudiant", "20240001")
            
            rows.append({
                "ID": id_etudiant,
                "Étudiant": f"{infos.get('prenom')} {infos.get('nom')}",
                "Formation": infos.get("formation", "L3"),
                "Score moyen": infos.get("score_moyen", 0.0),
                "Progression": f"{infos.get('progression', 0)}%",
                "Dernière connexion": infos.get("connexion_time", "Aucune"),
                
                "id": id_etudiant,
                "score_moyen": infos.get("score_moyen", 0.0),
                "progression": infos.get("progression", 0),
                "modules_debloques": nb_modules,
                "email": email,
                "prenom": infos.get("prenom", ""),
                "nom": infos.get("nom", "")
            })
            
    return rows


# ─────────────────────────────────────────────────────────────
# FONCTIONS ACCÈS MODULES (MOCKÉES)
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
# STOCKAGE EN MÉMOIRE POUR LE MODE DÉMO
# (remplace la base SQLite pour les fonctions interactives)
# ─────────────────────────────────────────────────────────────
_module_access_store: dict = {}   # {etudiant_id: {module: bool}}
_quiz_results_store: list  = []   # liste de dicts résultats
_notifications_store: list = []   # liste de dicts notifications
_next_result_id: list      = [1]  # compteur auto-incrémenté


def _default_access(etudiant_id) -> dict:
    """Retourne les accès par défaut pour un étudiant."""
    access = {}
    for mod in MODULES:
        access[mod] = (mod in MODULES_LIBRES)
    return access


def get_module_access(etudiant_id) -> dict:
    """Retourne les permissions d'accès aux modules pour un étudiant."""
    etudiant_id = str(etudiant_id)
    if etudiant_id not in _module_access_store:
        _module_access_store[etudiant_id] = _default_access(etudiant_id)
    return _module_access_store[etudiant_id]


def set_module_access(etudiant_id, module_key: str, debloque: bool, prof_id=None):
    """Modifie l'accès d'un étudiant à un module."""
    etudiant_id = str(etudiant_id)
    if etudiant_id not in _module_access_store:
        _module_access_store[etudiant_id] = _default_access(etudiant_id)
    _module_access_store[etudiant_id][module_key] = debloque


def set_all_modules_access(etudiant_id, debloque: bool, prof_id=None):
    """Bloque ou débloque tous les modules pour un étudiant."""
    etudiant_id = str(etudiant_id)
    access = {}
    for mod in MODULES:
        # Les modules libres restent toujours accessibles
        access[mod] = True if mod in MODULES_LIBRES else debloque
    _module_access_store[etudiant_id] = access


# ─────────────────────────────────────────────────────────────
# PROGRESSION (MOCKÉE)
# ─────────────────────────────────────────────────────────────

def get_progression_etudiant(etudiant_id) -> dict:
    """Retourne la progression par module pour un étudiant."""
    from utils.auth import COMPTES_DEMO
    etudiant_id = str(etudiant_id)

    compte = None
    for infos in COMPTES_DEMO.values():
        if str(infos.get("numero_etudiant")) == etudiant_id:
            compte = infos
            break

    modules_completes = compte.get("modules_completes", []) if compte else []
    progression_globale = compte.get("progression", 0) if compte else 0

    result = {}
    for mod in MODULES:
        if mod in modules_completes:
            pct = 100.0
        elif mod in MODULES_LIBRES:
            pct = float(progression_globale) if progression_globale else 0.0
        else:
            pct = 0.0
        result[mod] = {
            "pct_complete":     pct,
            "nb_visites":       3 if mod in modules_completes else 0,
            "temps_passe":      1800 if mod in modules_completes else 0,
            "derniere_visite":  datetime.now().strftime("%Y-%m-%d %H:%M") if mod in modules_completes else None,
        }
    return result


def get_progression_globale(etudiant_id) -> float:
    """Retourne le pourcentage de progression globale d'un étudiant."""
    from utils.auth import COMPTES_DEMO
    etudiant_id = str(etudiant_id)

    for infos in COMPTES_DEMO.values():
        if str(infos.get("numero_etudiant")) == etudiant_id:
            return float(infos.get("progression", 0))
    return 0.0


# ─────────────────────────────────────────────────────────────
# QUIZ RESULTS (MOCKÉS)
# ─────────────────────────────────────────────────────────────

def _seed_quiz_results():
    """Insère des résultats de quiz démo si le store est vide."""
    if _quiz_results_store:
        return
    demo_results = [
        {
            "id":           1,
            "etudiant_id":  "20240001",
            "prenom":       "Alex",
            "nom":          "Dupont",
            "module_key":   "actions",
            "score":        14.0,
            "score_max":    20.0,
            "nb_questions": 10,
            "nb_correctes": 7,
            "theme":        "Marchés boursiers",
            "note_prof":    None,
            "commentaire":  None,
            "passe_le":     "2025-03-12 10:30",
        },
        {
            "id":           2,
            "etudiant_id":  "20240001",
            "prenom":       "Alex",
            "nom":          "Dupont",
            "module_key":   "obligations",
            "score":        15.0,
            "score_max":    20.0,
            "nb_questions": 10,
            "nb_correctes": 8,
            "theme":        "Taux d'intérêt",
            "note_prof":    None,
            "commentaire":  None,
            "passe_le":     "2025-03-18 14:15",
        },
    ]
    _quiz_results_store.extend(demo_results)
    _next_result_id[0] = 3


def get_quiz_results_all() -> list:
    """Retourne tous les résultats de quiz (tous étudiants confondus)."""
    _seed_quiz_results()
    return list(_quiz_results_store)


def get_quiz_results_etudiant(etudiant_id) -> list:
    """Retourne les résultats de quiz d'un étudiant spécifique."""
    _seed_quiz_results()
    return [r for r in _quiz_results_store
            if str(r["etudiant_id"]) == str(etudiant_id)]


def add_quiz_result(etudiant_id, module_key: str, score: float,
                    score_max: float, nb_questions: int = 0,
                    nb_correctes: int = 0, theme: str = "") -> int:
    """Enregistre un nouveau résultat de quiz."""
    _seed_quiz_results()
    from utils.auth import COMPTES_DEMO
    prenom, nom = "", ""
    for infos in COMPTES_DEMO.values():
        if str(infos.get("numero_etudiant")) == str(etudiant_id):
            prenom = infos.get("prenom", "")
            nom    = infos.get("nom", "")
            break

    result_id = _next_result_id[0]
    _next_result_id[0] += 1
    _quiz_results_store.append({
        "id":           result_id,
        "etudiant_id":  str(etudiant_id),
        "prenom":       prenom,
        "nom":          nom,
        "module_key":   module_key,
        "score":        score,
        "score_max":    score_max,
        "nb_questions": nb_questions,
        "nb_correctes": nb_correctes,
        "theme":        theme,
        "note_prof":    None,
        "commentaire":  None,
        "passe_le":     datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    return result_id


def add_note_prof(result_id: int, note: float, commentaire: str = ""):
    """Attribue une note professeur à un résultat de quiz."""
    _seed_quiz_results()
    for r in _quiz_results_store:
        if r["id"] == result_id:
            r["note_prof"]   = note
            r["commentaire"] = commentaire
            break


# ─────────────────────────────────────────────────────────────
# NOTIFICATIONS (MOCKÉES)
# ─────────────────────────────────────────────────────────────

def send_notification(expediteur_id, message: str, destinataire_id=None):
    """
    Enregistre une notification.
    destinataire_id=None → envoi à tous les étudiants.
    """
    from utils.auth import COMPTES_DEMO
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if destinataire_id is None:
        # Diffusion à tous
        for infos in COMPTES_DEMO.values():
            if infos.get("role") == "etudiant":
                _notifications_store.append({
                    "destinataire_id": infos.get("numero_etudiant"),
                    "expediteur_id":   str(expediteur_id),
                    "expediteur":      "Professeur",
                    "message":         message,
                    "lu":              False,
                    "cree_le":         now,
                })
    else:
        _notifications_store.append({
            "destinataire_id": str(destinataire_id),
            "expediteur_id":   str(expediteur_id),
            "expediteur":      "Professeur",
            "message":         message,
            "lu":              False,
            "cree_le":         now,
        })


def get_notifications(user_id) -> list:
    """Retourne les notifications non lues d'un utilisateur."""
    return [n for n in _notifications_store
            if str(n.get("destinataire_id")) == str(user_id) and not n["lu"]]
