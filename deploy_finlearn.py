"""
deploy_finlearn.py
==================
Script de déploiement automatique de FinLearn sur GitHub + Streamlit Cloud.

Usage :
    python deploy_finlearn.py

Prérequis :
    - Git installé (https://git-scm.com)
    - pip install requests
    - Un compte GitHub avec un token (https://github.com/settings/tokens/new)
"""

import os
import sys
import re
import time
import subprocess
import webbrowser
from pathlib import Path

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests


# ─── Helpers ──────────────────────────────────────────────────
def ok(msg):   print(f"  ✅ {msg}")
def warn(msg): print(f"  ⚠️  {msg}")
def err(msg):  print(f"  ❌ {msg}"); sys.exit(1)
def step(msg): print(f"\n{'─'*56}\n  {msg}\n{'─'*56}")

def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       shell=isinstance(cmd, str))
    if check and r.returncode != 0:
        print(f"  STDOUT: {r.stdout[:300]}")
        print(f"  STDERR: {r.stderr[:300]}")
        err(f"Commande échouée : {cmd}")
    return r

def ask(prompt, default=None, secret=False):
    display = f"  {prompt}{f' [{default}]' if default else ''} : "
    if secret:
        import getpass
        val = getpass.getpass(display).strip()
    else:
        val = input(display).strip()
    return val or default or ""


# ─── Étape 1 : Vérifications ──────────────────────────────────
def check_prerequisites():
    step("ÉTAPE 1 — Vérifications")

    # Git
    r = run("git --version", check=False)
    if r.returncode != 0:
        print("\n  Git n'est pas installé.")
        webbrowser.open("https://git-scm.com/downloads")
        err("Installez Git puis relancez ce script.")
    ok(f"Git : {r.stdout.strip()}")

    # Python / pip
    r2 = run(f'"{sys.executable}" -m pip --version', check=False)
    ok(f"Python : {sys.version.split()[0]}")


# ─── Étape 2 : Collecte des infos ─────────────────────────────
def collect_info():
    step("ÉTAPE 2 — Configuration")

    print("""
  Pour créer votre token GitHub :
  1. Allez sur https://github.com/settings/tokens/new
  2. Donnez un nom (ex: finlearn-deploy)
  3. Cochez : repo (toutes les sous-cases)
  4. Cliquez "Generate token" et copiez-le
    """)

    token   = ask("Token GitHub (ghp_...)", secret=True)
    if not token:
        err("Token manquant.")

    repo_raw = ask("Nom du dépôt GitHub", default="finlearn-platform")
    repo     = re.sub(r'[^a-zA-Z0-9\-_.]', '-', repo_raw.strip()).strip('-') or "finlearn-platform"

    default_dir = str(Path.home() / "Desktop" / repo)
    projet_dir  = Path(ask("Dossier local du projet", default=default_dir))

    return token, repo, projet_dir


# ─── Étape 3 : Copier les fichiers ───────────────────────────
def copy_project(projet_dir: Path):
    step("ÉTAPE 3 — Préparation du projet")

    # Dossier source = même dossier que ce script
    src = Path(__file__).parent

    # Si on lance depuis le dossier finlearn directement
    if (src / "app.py").exists():
        source_dir = src
    else:
        # Cherche le dossier finlearn à côté
        candidates = list(src.glob("finlearn")) + list((src.parent).glob("finlearn"))
        if candidates:
            source_dir = candidates[0]
        else:
            source_dir = src

    if projet_dir.resolve() != source_dir.resolve():
        import shutil
        if projet_dir.exists():
            warn(f"Le dossier {projet_dir} existe déjà — les fichiers seront mis à jour.")
        projet_dir.mkdir(parents=True, exist_ok=True)

        # Copier tous les fichiers sauf .git et __pycache__
        for item in source_dir.rglob("*"):
            if any(p in str(item) for p in [".git", "__pycache__", ".pyc"]):
                continue
            dest = projet_dir / item.relative_to(source_dir)
            if item.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                shutil.copy2(item, dest)
        ok(f"Fichiers copiés vers {projet_dir}")
    else:
        ok(f"Utilisation du dossier courant : {projet_dir}")

    return projet_dir


# ─── Étape 4 : Git init ───────────────────────────────────────
def init_git(projet_dir: Path):
    step("ÉTAPE 4 — Initialisation Git")

    git_dir = projet_dir / ".git"
    if git_dir.exists():
        warn("Dépôt Git déjà initialisé.")
    else:
        run("git init", cwd=projet_dir)
        ok("Dépôt Git initialisé")

    # Config user si absente
    r_email = run("git config user.email", cwd=projet_dir, check=False)
    if not r_email.stdout.strip():
        email = ask("Votre email Git")
        name  = ask("Votre nom Git", default="FinLearn Dev")
        run(f'git config user.email "{email}"', cwd=projet_dir)
        run(f'git config user.name "{name}"',  cwd=projet_dir)

    # .gitignore — s'assurer que secrets.toml est dedans
    gitignore = projet_dir / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if "secrets.toml" not in content:
            with open(gitignore, "a") as f:
                f.write("\n.streamlit/secrets.toml\n")
    ok(".gitignore vérifié")

    # Supprimer secrets.toml du suivi Git s'il a été ajouté par erreur
    run("git rm --cached .streamlit/secrets.toml", cwd=projet_dir, check=False)

    run("git add .", cwd=projet_dir)
    r_commit = run('git commit -m "Initial commit — FinLearn Platform"', cwd=projet_dir, check=False)
    if r_commit.returncode == 0:
        ok("Premier commit créé")
    else:
        warn("Commit déjà existant ou rien à committer")


# ─── Étape 5 : Créer repo GitHub ──────────────────────────────
def create_github_repo(token: str, repo: str):
    step("ÉTAPE 5 — Création du dépôt GitHub")

    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    # Vérifie le token
    r = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    if r.status_code != 200:
        err(f"Token GitHub invalide (HTTP {r.status_code}). Vérifiez votre token.")
    user = r.json()["login"]
    ok(f"Connecté en tant que : {user}")

    # Vérifie si le repo existe
    r_check = requests.get(f"https://api.github.com/repos/{user}/{repo}",
                           headers=headers, timeout=10)
    if r_check.status_code == 200:
        warn(f"Le dépôt '{repo}' existe déjà — utilisation.")
        d = r_check.json()
        return user, d["clone_url"], d["html_url"]

    # Crée le repo
    payload = {
        "name":        repo,
        "description": "FinLearn — Plateforme académique d'apprentissage des instruments financiers",
        "private":     False,
        "auto_init":   False,
    }
    r_create = requests.post("https://api.github.com/user/repos",
                             headers=headers, json=payload, timeout=15)
    if r_create.status_code not in (200, 201):
        err(f"Impossible de créer le dépôt : {r_create.json().get('message','Erreur inconnue')}")

    d = r_create.json()
    ok(f"Dépôt créé : {d['html_url']}")
    return user, d["clone_url"], d["html_url"]


# ─── Étape 6 : Push sur GitHub ────────────────────────────────
def push_github(projet_dir: Path, token: str, user: str, repo: str, clone_url: str):
    step("ÉTAPE 6 — Push sur GitHub")

    url_auth = clone_url.replace("https://", f"https://{user}:{token}@")
    run("git remote remove origin", cwd=projet_dir, check=False)
    run(f"git remote add origin {url_auth}", cwd=projet_dir)
    ok("Remote origin configuré")

    run("git branch -M main", cwd=projet_dir, check=False)
    r_push = run("git push -u origin main", cwd=projet_dir, check=False)
    if r_push.returncode != 0:
        r_push2 = run("git push -u origin main --force", cwd=projet_dir, check=False)
        if r_push2.returncode != 0:
            err(f"Échec du push : {r_push2.stderr[:300]}")

    # Sécurité : retirer le token de la remote
    run(f"git remote set-url origin https://github.com/{user}/{repo}.git", cwd=projet_dir)
    ok("Code poussé sur GitHub ✓")


# ─── Étape 7 : Ouvrir Streamlit Cloud ────────────────────────
def open_streamlit_cloud(user: str, repo: str):
    step("ÉTAPE 7 — Déploiement Streamlit Cloud")

    deploy_url = (f"https://share.streamlit.io/deploy?"
                  f"repository={user}/{repo}&branch=main&mainModule=app.py")
    app_url    = f"https://{repo}.streamlit.app"

    print(f"""
  📋 INSTRUCTIONS FINALES :

  Une fenêtre va s'ouvrir dans votre navigateur.

  1. Connectez-vous avec votre compte GitHub
  2. Vérifiez :
     • Repository : {user}/{repo}
     • Branch     : main
     • Main file  : app.py
  3. Cliquez "Deploy !"
  4. Attendez 2-3 minutes → votre site est en ligne !

  🌐 URL prévue : {app_url}

  🔧 Pour configurer l'ENT (après déploiement) :
     Settings → Secrets → Collez :

     [auth]
     allow_all_university_emails = true

     [cas]
     url = "https://cas.votre-universite.fr"
     service = "{app_url}"

  👤 Comptes démo disponibles immédiatement :
     etudiant@demo.finlearn.edu / demo2025
     prof@demo.finlearn.edu / prof2025
    """)

    time.sleep(2)
    webbrowser.open(deploy_url)
    ok("Navigateur ouvert sur Streamlit Cloud")


# ─── MAIN ─────────────────────────────────────────────────────
def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║   DÉPLOIEMENT AUTOMATIQUE — FinLearn Platform           ║
║   GitHub + Streamlit Cloud                              ║
╚══════════════════════════════════════════════════════════╝

  Ce script va :
  1. Vérifier Git et Python
  2. Configurer votre dépôt GitHub
  3. Pousser le code sur GitHub
  4. Ouvrir Streamlit Cloud pour finaliser
""")
    input("  Appuyez sur Entrée pour commencer...")

    try:
        check_prerequisites()
        token, repo, projet_dir = collect_info()
        projet_dir = copy_project(projet_dir)
        init_git(projet_dir)
        user, clone_url, repo_url = create_github_repo(token, repo)
        push_github(projet_dir, token, user, repo, clone_url)
        open_streamlit_cloud(user, repo)

        print(f"""
{'═'*56}
  ✅ DÉPLOIEMENT RÉUSSI !

  📁 Projet local : {projet_dir.resolve()}
  🐙 GitHub       : https://github.com/{user}/{repo}
  🌐 Streamlit    : Finalisez dans votre navigateur
{'═'*56}
""")
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("\n\n  Déploiement annulé.")

    input("\n  Appuyez sur Entrée pour fermer...")


if __name__ == "__main__":
    main()
