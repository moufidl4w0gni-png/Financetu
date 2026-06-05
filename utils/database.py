"""
utils/database.py
==================
Base de données SQLite pour FinLearn.
Gère : utilisateurs, accès aux modules, scores, progression, notifications.

Toutes les données sont persistées en SQLite — les changements du professeur
(accès modules, notifications) sont immédiatement visibles côté étudiant.
"""

import sqlite3
import os
import hashlib
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CHEMIN DE LA BASE DE DONNÉES
# Streamlit Cloud : /tmp/ est le seul dossier accessible en écriture
# ─────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("FINLEARN_DB", "/tmp/finlearn.db")

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
MODULES_LIBRES = ["dashboard", "glossaire", "quiz"]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # lectures/écritures simultanées
    return conn


def init_db():
    """Crée toutes les tables et insère les données initiales."""
    conn = get_connection()
    c = conn.cursor()

    # ── TABLE users ───────────────────────────────────────────
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
            nb_questions  INTEGER DEFAULT 0,
            nb_correctes  INTEGER DEFAULT 0,
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
            expediteur_nom  TEXT DEFAULT 'Professeur',
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
    """Insère les comptes démo par défaut si la base est vide."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] > 0:
        return

    # Professeur démo
    hash_prof = hashlib.sha256("prof2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("prof@demo.finlearn.edu", "Martin", "Marie", "professeur",
          "Enseignant-Chercheur Finance", "CY Cergy Paris Université", hash_prof))

    # Étudiant démo
    hash_etu = hashlib.sha256("demo2025".encode()).hexdigest()
    c.execute("""
        INSERT OR IGNORE INTO users
        (email, nom, prenom, role, formation, universite, password_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("etudiant@demo.finlearn.edu", "Dupont", "Alex", "etudiant",
          "L3 Éco-Finance", "CY Cergy Paris Université", hash_etu))

    conn.commit()

    # Accès modules pour l'étudiant démo
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

        # Résultats de quiz démo
        c.execute("""
            INSERT OR IGNORE INTO quiz_results
            (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme, passe_le)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (etu_id, "actions", 14.0, 20.0, 10, 7, "Marchés boursiers", "2025-03-12 10:30"))
        c.execute("""
            INSERT OR IGNORE INTO quiz_results
            (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme, passe_le)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (etu_id, "obligations", 15.0, 20.0, 10, 8, "Taux d'intérêt", "2025-03-18 14:15"))

        conn.commit()


# ─────────────────────────────────────────────────────────────
# UTILISATEURS
# ─────────────────────────────────────────────────────────────

def get_user_by_email(email: str) -> dict | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND actif = 1", (email.lower(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_or_update_user(email: str, nom: str, prenom: str,
                          role: str = "etudiant", formation: str = "",
                          universite: str = "") -> int:
    """Crée ou met à jour un utilisateur. Retourne son id SQLite."""
    conn = get_connection()
    c = conn.cursor()
    email = email.lower()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if row:
        c.execute("UPDATE users SET last_login=?, nom=?, prenom=? WHERE email=?",
                  (now, nom, prenom, email))
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


def get_user_db_id(email: str) -> int | None:
    """Retourne l'id SQLite d'un utilisateur par son email."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
    row = c.fetchone()
    conn.close()
    return row["id"] if row else None


# ─────────────────────────────────────────────────────────────
# ÉTUDIANTS (vue prof)
# ─────────────────────────────────────────────────────────────

def get_all_etudiants() -> list:
    """Retourne tous les étudiants avec leur progression et score moyen."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.email, u.nom, u.prenom, u.formation, u.universite, u.last_login
        FROM users u
        WHERE u.role = 'etudiant' AND u.actif = 1
        ORDER BY u.nom, u.prenom
    """)
    users = [dict(r) for r in c.fetchall()]

    result = []
    for u in users:
        etu_id = u["id"]

        # Score moyen
        c.execute("""
            SELECT AVG(score / score_max * 20) as moy
            FROM quiz_results WHERE etudiant_id = ? AND score_max > 0
        """, (etu_id,))
        row_score = c.fetchone()
        score_moy = round(row_score["moy"], 1) if row_score and row_score["moy"] else 0.0

        # Modules débloqués (hors libres)
        c.execute("""
            SELECT COUNT(*) as nb FROM module_access
            WHERE etudiant_id = ? AND debloque = 1 AND module_key NOT IN ({})
        """.format(",".join("?" * len(MODULES_LIBRES))), (etu_id, *MODULES_LIBRES))
        nb_debloques = c.fetchone()["nb"]

        # Progression globale
        c.execute("""
            SELECT AVG(pct_complete) as pct FROM progression WHERE etudiant_id = ?
        """, (etu_id,))
        row_prog = c.fetchone()
        prog = round(row_prog["pct"], 0) if row_prog and row_prog["pct"] else 0.0

        result.append({
            "id":               etu_id,
            "email":            u["email"],
            "prenom":           u["prenom"],
            "nom":              u["nom"],
            "formation":        u.get("formation") or "N/A",
            "universite":       u.get("universite") or "N/A",
            "last_login":       u.get("last_login"),
            "score_moyen":      score_moy,
            "modules_debloques": nb_debloques,
            "progression":      prog,
            # Colonnes affichage tableau
            "ID":               etu_id,
            "Étudiant":         f"{u['prenom']} {u['nom']}",
            "Formation":        u.get("formation") or "N/A",
            "Score moyen":      score_moy,
            "Progression":      f"{prog:.0f}%",
            "Dernière connexion": (u.get("last_login") or "Jamais")[:16],
        })

    conn.close()
    return result


# ─────────────────────────────────────────────────────────────
# ACCÈS AUX MODULES  ← persisté en SQLite
# ─────────────────────────────────────────────────────────────

def get_module_access(etudiant_id: int) -> dict:
    """
    Retourne {module_key: bool} pour un étudiant.
    Les modules libres sont toujours True.
    """
    conn = get_connection()
    c = conn.cursor()

    # S'assure que toutes les lignes existent
    for mod in MODULES:
        debloque = 1 if mod in MODULES_LIBRES else 0
        c.execute("""
            INSERT OR IGNORE INTO module_access (etudiant_id, module_key, debloque)
            VALUES (?, ?, ?)
        """, (etudiant_id, mod, debloque))
    conn.commit()

    c.execute("SELECT module_key, debloque FROM module_access WHERE etudiant_id = ?",
              (etudiant_id,))
    rows = c.fetchall()
    conn.close()

    access = {}
    for r in rows:
        access[r["module_key"]] = bool(r["debloque"])
    # Forcer les modules libres
    for mod in MODULES_LIBRES:
        access[mod] = True
    return access


def set_module_access(etudiant_id: int, module_key: str, debloque: bool,
                      prof_id: int = None):
    """Modifie l'accès d'un étudiant à un module (persisté en SQLite)."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO module_access (etudiant_id, module_key, debloque, debloque_par, debloque_le)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(etudiant_id, module_key)
        DO UPDATE SET debloque=excluded.debloque,
                      debloque_par=excluded.debloque_par,
                      debloque_le=excluded.debloque_le
    """, (etudiant_id, module_key, int(debloque), prof_id, now))
    conn.commit()
    conn.close()


def set_all_modules_access(etudiant_id: int, debloque: bool, prof_id: int = None):
    """Bloque ou débloque tous les modules pour un étudiant (persisté)."""
    for mod in MODULES:
        val = True if mod in MODULES_LIBRES else debloque
        set_module_access(etudiant_id, mod, val, prof_id)


# ─────────────────────────────────────────────────────────────
# PROGRESSION
# ─────────────────────────────────────────────────────────────

def get_progression_etudiant(etudiant_id: int) -> dict:
    """Retourne la progression par module pour un étudiant."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM progression WHERE etudiant_id = ?", (etudiant_id,))
    rows = c.fetchall()
    conn.close()

    result = {mod: {"pct_complete": 0.0, "nb_visites": 0,
                    "temps_passe": 0, "derniere_visite": None}
              for mod in MODULES}
    for r in rows:
        result[r["module_key"]] = {
            "pct_complete":     r["pct_complete"],
            "nb_visites":       r["nb_visites"],
            "temps_passe":      r["temps_passe"],
            "derniere_visite":  r["derniere_visite"],
        }
    return result


def get_progression_globale(etudiant_id: int) -> float:
    """Retourne le % de progression globale d'un étudiant."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT AVG(pct_complete) as pct FROM progression WHERE etudiant_id = ?",
              (etudiant_id,))
    row = c.fetchone()
    conn.close()
    return round(row["pct"], 1) if row and row["pct"] else 0.0


def update_progression(etudiant_id: int, module_key: str,
                       pct_complete: float, temps_passe: int = 0):
    """Met à jour la progression d'un étudiant sur un module."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO progression (etudiant_id, module_key, pct_complete, nb_visites,
                                 temps_passe, derniere_visite)
        VALUES (?, ?, ?, 1, ?, ?)
        ON CONFLICT(etudiant_id, module_key)
        DO UPDATE SET pct_complete    = MAX(pct_complete, excluded.pct_complete),
                      nb_visites      = nb_visites + 1,
                      temps_passe     = temps_passe + excluded.temps_passe,
                      derniere_visite = excluded.derniere_visite
    """, (etudiant_id, module_key, pct_complete, temps_passe, now))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# QUIZ RESULTS
# ─────────────────────────────────────────────────────────────

def get_quiz_results_all() -> list:
    """Retourne tous les résultats de quiz avec infos étudiant."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT qr.*, u.prenom, u.nom
        FROM quiz_results qr
        JOIN users u ON u.id = qr.etudiant_id
        ORDER BY qr.passe_le DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_quiz_results_etudiant(etudiant_id: int) -> list:
    """Retourne les résultats de quiz d'un étudiant."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT qr.*, u.prenom, u.nom
        FROM quiz_results qr
        JOIN users u ON u.id = qr.etudiant_id
        WHERE qr.etudiant_id = ?
        ORDER BY qr.passe_le DESC
    """, (etudiant_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_quiz_result(etudiant_id: int, module_key: str, score: float,
                    score_max: float, nb_questions: int = 0,
                    nb_correctes: int = 0, theme: str = "") -> int:
    """Enregistre un résultat de quiz."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO quiz_results
        (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (etudiant_id, module_key, score, score_max, nb_questions, nb_correctes, theme))
    result_id = c.lastrowid
    conn.commit()
    conn.close()
    return result_id


def add_note_prof(result_id: int, note: float, commentaire: str = ""):
    """Attribue une note professeur à un résultat de quiz."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE quiz_results SET note_prof=?, commentaire=? WHERE id=?
    """, (note, commentaire, result_id))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────
# NOTIFICATIONS  ← persistées en SQLite, visibles côté étudiant
# ─────────────────────────────────────────────────────────────

def send_notification(expediteur_id: int, message: str,
                      destinataire_id: int = None, expediteur_nom: str = "Professeur"):
    """
    Envoie une notification.
    destinataire_id=None → envoi à TOUS les étudiants.
    """
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if destinataire_id is None:
        # Récupère tous les étudiants actifs
        c.execute("SELECT id FROM users WHERE role='etudiant' AND actif=1")
        dest_ids = [r["id"] for r in c.fetchall()]
    else:
        dest_ids = [destinataire_id]

    for dest_id in dest_ids:
        c.execute("""
            INSERT INTO notifications
            (destinataire_id, expediteur_id, expediteur_nom, message, cree_le)
            VALUES (?, ?, ?, ?, ?)
        """, (dest_id, expediteur_id, expediteur_nom, message, now))

    conn.commit()
    conn.close()


def get_notifications(user_id: int, non_lues_seulement: bool = False) -> list:
    """Retourne les notifications d'un utilisateur (les plus récentes en premier)."""
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT * FROM notifications
        WHERE destinataire_id = ?
        {}
        ORDER BY cree_le DESC
        LIMIT 50
    """.format("AND lu = 0" if non_lues_seulement else "")
    c.execute(query, (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def marquer_notification_lue(notif_id: int):
    """Marque une notification comme lue."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE notifications SET lu=1 WHERE id=?", (notif_id,))
    conn.commit()
    conn.close()


def marquer_toutes_lues(user_id: int):
    """Marque toutes les notifications d'un utilisateur comme lues."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE notifications SET lu=1 WHERE destinataire_id=?", (user_id,))
    conn.commit()
    conn.close()


def count_notifications_non_lues(user_id: int) -> int:
    """Retourne le nombre de notifications non lues."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as nb FROM notifications WHERE destinataire_id=? AND lu=0",
              (user_id,))
    row = c.fetchone()
    conn.close()
    return row["nb"] if row else 0
