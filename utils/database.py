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
    # Stocke tous les utilisateurs : étudiants ET professeurs
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            nom           TEXT NOT NULL,
            prenom        TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'etudiant',
            -- role = 'etudiant' | 'professeur' | 'admin'
            formation     TEXT,
            universite    TEXT,
            annee         TEXT,
            password_hash TEXT,
            -- Pour les profs qui se connectent avec un mot de passe local
            -- (en plus du CAS ENT)
            actif         INTEGER DEFAULT 1,
            -- 0 = compte désactivé par l'admin
            created_at    TEXT DEFAULT (datetime('now')),
            last_login    TEXT
        )
    """)

    # ── TABLE module_access ───────────────────────────────────
    # Définit quels modules sont débloqués pour chaque étudiant.
    # Un professeur peut bloquer/débloquer module par module.
    c.execute("""
        CREATE TABLE IF NOT EXISTS module_access (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id   INTEGER NOT NULL,
            module_key    TEXT NOT NULL,
            -- Exemple : 'actions', 'obligations', 'derives'...
            debloque      INTEGER DEFAULT 0,
            -- 0 = bloqué, 1 = débloqué
            debloque_par  INTEGER,
            -- ID du professeur qui a débloqué
            debloque_le   TEXT,
            -- Date/heure du déblocage
            FOREIGN KEY (etudiant_id) REFERENCES users(id),
            FOREIGN KEY (debloque_par) REFERENCES users(id),
            UNIQUE(etudiant_id, module_key)
            -- Un étudiant ne peut avoir qu'un enregistrement par module
        )
    """)

    # ── TABLE quiz_results ────────────────────────────────────
    # Stocke chaque tentative de quiz d'un étudiant.
    # Plusieurs tentatives possibles (on garde l'historique).
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id   INTEGER NOT NULL,
            module_key    TEXT NOT NULL,
            -- Module concerné ('actions', 'quiz', etc.)
            score         REAL NOT NULL,
            -- Score obtenu (ex: 14.5)
            score_max     REAL NOT NULL,
            -- Score maximum possible (ex: 20)
            nb_questions  INTEGER,
            nb_correctes  INTEGER,
            theme         TEXT,
            -- Thème spécifique si filtre appliqué
            note_prof     REAL,
            -- Note corrigée/ajustée par le professeur (optionnel)
            commentaire   TEXT,
            -- Commentaire du professeur sur ce résultat
            passe_le      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (etudiant_id) REFERENCES users(id)
        )
    """)

    # ── TABLE progression ─────────────────────────────────────
    # Suivi de la progression par module et par étudiant.
    # Mis à jour automatiquement quand l'étudiant visite un module.
    c.execute("""
        CREATE TABLE IF NOT EXISTS progression (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id   INTEGER NOT NULL,
            module_key    TEXT NOT NULL,
            pct_complete  REAL DEFAULT 0,
            -- Pourcentage de complétion (0 à 100)
            nb_visites    INTEGER DEFAULT 0,
            -- Nombre de fois que l'étudiant a visité ce module
            temps_passe   INTEGER DEFAULT 0,
            -- Temps cumulé en secondes (optionnel)
            derniere_visite TEXT,
            FOREIGN KEY (etudiant_id) REFERENCES users(id),
            UNIQUE(etudiant_id, module_key)
        )
    """)

    # ── TABLE notifications ───────────────────────────────────
    # Permet aux profs d'envoyer des messages aux étudiants
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            destinataire_id INTEGER,
            -- NULL = message pour tous les étudiants
            expediteur_id   INTEGER NOT NULL,
            message         TEXT NOT NULL,
            lu              INTEGER DEFAULT 0,
            cree_le         TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (destinataire_id) REFERENCES users(id),
            FOREIGN KEY (expediteur_id)   REFERENCES users(id)
        )
    """)

    conn.commit()

    # ── Insertion des données par défaut ──────────────────────
    _inserer_donnees_initiales(conn)

    conn.close()


def _inserer_donnees_initiales(conn):
    """
    Insère les comptes par défaut si la base est vide.
    Professeur démo et quelques étudiants de test.
    """
    c = conn.cursor()

    # Vérifie si des utilisateurs existent déjà
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        return  # Base déjà initialisée

    # Compte professeur par défaut
    # Mot de passe : prof2025
    hash_prof = hashlib.sha256("prof2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "prof@demo.finlearn.edu",
        "Martin", "Marie",
        "professeur",
        "Enseignant-Chercheur Finance",
        "CY Cergy Paris Université",
        hash_prof
    ))

    # Compte étudiant de démo
    hash_etu = hashlib.sha256("demo2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "etudiant@demo.finlearn.edu",
        "Dupont", "Alex",
        "etudiant",
        "L3 Éco-Finance",
        "CY Cergy Paris Université",
        hash_etu
    ))

    conn.commit()

    # Récupère l'ID de l'étudiant démo
    c.execute("SELECT id FROM users WHERE email = ?",
              ("etudiant@demo.finlearn.edu",))
    row = c.fetchone()
    if row:
        etu_id = row["id"]
        # Débloquer dashboard et glossaire par défaut
        for mod in MODULES:
            debloque = 1 if mod in MODULES_LIBRES else 0
            c.execute("""
                INSERT OR IGNORE INTO module_access
                (etudiant_id, module_key, debloque)
                VALUES (?, ?, ?)
            """, (etu_id, mod, debloque))
        conn.commit()


# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILISATEURS
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
    """
    Crée un nouvel utilisateur ou met à jour sa dernière connexion.
    Retourne l'ID de l'utilisateur.
    Appelé automatiquement à chaque connexion ENT réussie.
    """
    conn = get_connection()
    c = conn.cursor()

    email = email.lower()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Vérifie si l'utilisateur existe
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if row:
        # Mise à jour de la dernière connexion
        c.execute("""
            UPDATE users SET last_login = ?, nom = ?, prenom = ?
            WHERE email = ?
        """, (now, nom, prenom, email))
        user_id = row["id"]
    else:
        # Création d'un nouvel étudiant
        c.execute("""
            INSERT INTO users (email, nom, prenom, role, formation, universite, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email, nom, prenom, role, formation, universite, now))
        user_id = c.lastrowid

        # Débloquer les modules libres par défaut
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
    """Retourne la liste de tous les étudiants avec toutes les clés requises (y compris les IDs)."""
    from utils.auth import COMPTES_DEMO
    
    rows = []
    for email, infos in COMPTES_DEMO.items():
        if infos.get("role") == "etudiant":
            liste_modules = infos.get("modules_completes", [])
            nb_modules = len(liste_modules)
            id_etudiant = infos.get("numero_etudiant", "20240001")
            
            rows.append({
                # Clés d'affichage pour les tableaux st.dataframe
                "ID": id_etudiant,
                "Étudiant": f"{infos.get('prenom')} {infos.get('nom')}",
                "Formation": infos.get("formation", "L3"),
                "Score moyen": infos.get("score_moyen", 0.0),
                "Progression": f"{infos.get('progression', 0)}%",
                "Dernière connexion": infos.get("connexion_time", "Aucune"),
                
                # Clés techniques requises par les calculs du prof_dashboard
                "id": id_etudiant,  # 👈 Correction de la KeyError (Ligne 154)
                "score_moyen": infos.get("score_moyen", 0.0),
                "progression": infos.get("progression", 0),
                "modules_debloques": nb_modules,
                "email": email,
                "prenom": infos.get("prenom", ""),
                "nom": infos.get("nom", "")
            })
            
    return rows
# ─────────────────────────────────────────────────────────────
# FONCTIONS ACCÈS MODULES
# ─────────────────────────────────────────────────────────────

def get_module_access(etudiant_id: int) -> dict:
    """
    Retourne un dict {module_key: True/False} pour un étudiant.
    Exemple : {'actions': True, 'obligations': False, ...}
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT module_key, debloque FROM module_access
        WHERE etudiant_id = ?
    """, (etudiant_id,))
    rows = c.fetchall()
    conn.close()

    # Construit le dictionnaire
    access = {mod: (mod in MODULES_LIBRES) for mod in MODULES}
    for row in rows:
        access[row["module_key"]] = bool(row["debloque"])
    return access


def set_module_access(etudiant_id: int, module_key: str,
                      debloque: bool, prof_id: int):
    """
    Débloquer ou bloquer un module pour un étudiant.
    Enregistre qui a fait l'action et quand.
    """
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO module_access (etudiant_id, module_key, debloque, debloque_par, debloque_le)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(etudiant_id, module_key)
        DO UPDATE SET
            debloque     = excluded.debloque,
            debloque_par = excluded.debloque_par,
            debloque_le  = excluded.debloque_le
    """, (etudiant_id, module_key, int(debloque), prof_id, now))

    conn.commit()
    conn.close()


def set_all_modules_access(etudiant_id: int, debloque: bool, prof_id: int):
    """Débloquer ou bloquer TOUS les modules d'un étudiant en une fois."""
    for mod in MODULES:
        if mod not in MODULES_LIBRES:  # Ne jamais bloquer les modules libres
            set_module_access(etudiant_id, mod, debloque, prof_id)


def can_access_module(etudiant_id: int, module_key: str) -> bool:
    """Vérifie si un étudiant peut accéder à un module donné."""
    if module_key in MODULES_LIBRES:
        return True
    access = get_module_access(etudiant_id)
    return access.get(module_key, False)


# ─────────────────────────────────────────────────────────────
# FONCTIONS PROGRESSION
# ─────────────────────────────────────────────────────────────

def update_progression(etudiant_id: int, module_key: str, pct: float = None):
    """
    Met à jour la progression d'un étudiant sur un module.
    Incrémente le nombre de visites automatiquement.
    """
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Récupère la progression actuelle
    c.execute("""
        SELECT pct_complete, nb_visites FROM progression
        WHERE etudiant_id = ? AND module_key = ?
    """, (etudiant_id, module_key))
    row = c.fetchone()

    if row:
        new_pct = max(row["pct_complete"], pct or 0)  # Ne jamais reculer
        new_visites = row["nb_visites"] + 1
        c.execute("""
            UPDATE progression
            SET pct_complete = ?, nb_visites = ?, derniere_visite = ?
            WHERE etudiant_id = ? AND module_key = ?
        """, (new_pct, new_visites, now, etudiant_id, module_key))
    else:
        c.execute("""
            INSERT INTO progression (etudiant_id, module_key, pct_complete, nb_visites, derniere_visite)
            VALUES (?, ?, ?, 1, ?)
        """, (etudiant_id, module_key, pct or 0, now))

    conn.commit()
    conn.close()


def get_progression_etudiant(etudiant_id: int) -> dict:
    """Retourne la progression complète d'un étudiant par module."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT module_key, pct_complete, nb_visites, derniere_visite
        FROM progression WHERE etudiant_id = ?
    """, (etudiant_id,))
    rows = c.fetchall()
    conn.close()
    return {row["module_key"]: dict(row) for row in rows}


def get_progression_globale(etudiant_id: int) -> float:
    """Retourne le pourcentage global de progression d'un étudiant (0-100)."""
    prog = get_progression_etudiant(etudiant_id)
    if not prog:
        return 0.0
    total = sum(v["pct_complete"] for v in prog.values())
    return round(total / len(MODULES), 1)


# ─────────────────────────────────────────────────────────────
# FONCTIONS QUIZ & SCORES
# ─────────────────────────────────────────────────────────────

def save_quiz_result(etudiant_id: int, module_key: str,
                     score: float, score_max: float,
                     nb_questions: int, nb_correctes: int,
                     theme: str = ""):
    """
    Enregistre le résultat d'un quiz.
    Met aussi à jour la progression du module.
    """
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO quiz_results
        (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme))

    conn.commit()
    conn.close()

    # Met à jour la progression automatiquement
    pct = (score / score_max) * 100 if score_max > 0 else 0
    update_progression(etudiant_id, module_key, pct)


def get_quiz_results_etudiant(etudiant_id: int) -> list:
    """Retourne tous les résultats de quiz d'un étudiant."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM quiz_results
        WHERE etudiant_id = ?
        ORDER BY passe_le DESC
    """, (etudiant_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_quiz_results_all() -> list:
    """Retourne tous les résultats de quiz (vue professeur)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT qr.*,
               u.nom, u.prenom, u.email, u.formation
        FROM quiz_results qr
        JOIN users u ON qr.etudiant_id = u.id
        ORDER BY qr.passe_le DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_note_prof(result_id: int, note: float, commentaire: str = ""):
    """Le professeur ajoute/modifie une note ou un commentaire sur un résultat."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE quiz_results
        SET note_prof = ?, commentaire = ?
        WHERE id = ?
    """, (note, commentaire, result_id))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# FONCTIONS NOTIFICATIONS
# ─────────────────────────────────────────────────────────────

def send_notification(expediteur_id: int, message: str,
                      destinataire_id: int = None):
    """
    Envoie une notification.
    Si destinataire_id est None, le message est envoyé à tous.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO notifications (expediteur_id, destinataire_id, message)
        VALUES (?, ?, ?)
    """, (expediteur_id, destinataire_id, message))
    conn.commit()
    conn.close()


def get_notifications(user_id: int) -> list:
    """Retourne les notifications non lues pour un utilisateur."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT n.*, u.prenom || ' ' || u.nom as expediteur
        FROM notifications n
        JOIN users u ON n.expediteur_id = u.id
        WHERE (n.destinataire_id = ? OR n.destinataire_id IS NULL)
          AND n.lu = 0
        ORDER BY n.cree_le DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notification_read(notif_id: int):
    """Marque une notification comme lue."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE notifications SET lu = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
