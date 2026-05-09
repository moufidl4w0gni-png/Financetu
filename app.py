"""
FinLearn — Plateforme Académique d'Apprentissage des Instruments Financiers
============================================================================
Application principale — Authentification ENT + Navigation
"""

import streamlit as st
import time
from utils.auth import verifier_connexion, deconnecter, get_user_info
from utils.styles import inject_css

# ─────────────────────────────────────────────────────────────
# CONFIGURATION PAGE
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinLearn — Plateforme Financière",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "mailto:support@finlearn.edu",
        "Report a bug": "mailto:support@finlearn.edu",
        "About": "FinLearn v1.0 — Plateforme académique d'instruments financiers"
    }
)

inject_css()
st.markdown("""
    <style>
        /* Masque le menu de navigation natif de Streamlit */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────
# INITIALISATION SESSION
# ─────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

# ─────────────────────────────────────────────────────────────
# PAGE DE CONNEXION ENT
# ─────────────────────────────────────────────────────────────
def page_connexion():
    col_left, col_center, col_right = st.columns([1, 1.4, 1])

    with col_center:
        # Logo & titre
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">📈</div>
            <h1 class="login-title">FinLearn</h1>
            <p class="login-subtitle">Plateforme Académique des Instruments Financiers</p>
            <div class="login-badge">Accès réservé aux étudiants inscrits</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        st.markdown("### 🎓 Connexion via ENT universitaire")
        st.markdown(
            "<p style='color:#6b7280;font-size:13px;margin-bottom:20px;'>"
            "Utilisez vos identifiants ENT (Environnement Numérique de Travail) "
            "de votre université pour accéder à la plateforme.</p>",
            unsafe_allow_html=True
        )

        with st.form("login_form", clear_on_submit=False):
            identifiant = st.text_input(
                "Identifiant ENT",
                placeholder="prenom.nom@universite.fr  ou  numéro étudiant",
                help="Votre email universitaire ou numéro étudiant"
            )
            mot_de_passe = st.text_input(
                "Mot de passe ENT",
                type="password",
                placeholder="Votre mot de passe ENT",
                help="Le même mot de passe que votre ENT universitaire"
            )

            col_a, col_b = st.columns([1, 1])
            with col_a:
                souvenir = st.checkbox("Se souvenir de moi")
            with col_b:
                st.markdown(
                    "<a href='#' style='font-size:12px;color:#1a56db;float:right;'>Mot de passe oublié ?</a>",
                    unsafe_allow_html=True
                )

            st.markdown("<br>", unsafe_allow_html=True)
            connexion = st.form_submit_button(
                "🔐 Se connecter",
                use_container_width=True,
                type="primary"
            )

        if connexion:
            if not identifiant or not mot_de_passe:
                st.error("⚠️ Veuillez remplir tous les champs.")
            elif st.session_state.login_attempts >= 5:
                st.error("🔒 Trop de tentatives. Réessayez dans 10 minutes.")
            else:
                with st.spinner("Connexion à l'ENT en cours..."):
                    time.sleep(1.2)
                    succes, user_data, message = verifier_connexion(identifiant, mot_de_passe)

                if succes:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.login_attempts = 0
                    st.success(f"✅ Bienvenue, {user_data['prenom']} !")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    st.error(f"❌ {message}")
                    if st.session_state.login_attempts >= 3:
                        st.warning(
                            f"⚠️ {5 - st.session_state.login_attempts} tentative(s) restante(s) "
                            "avant le blocage temporaire."
                        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Infos universitaires
        st.markdown("""
        <div class='ent-info'>
            <p>🏫 <strong>Universités partenaires :</strong><br>
            CY Cergy Paris Université · Paris Dauphine · Paris 1 Panthéon-Sorbonne ·
            HEC Paris · Sciences Po · Et toute université disposant d'un ENT CAS</p>
            <p style='margin-top:8px;font-size:11px;color:#9ca3af;'>
            Vos données sont protégées conformément au RGPD.
            Aucun mot de passe n'est stocké sur nos serveurs.</p>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR — Navigation principale
# ─────────────────────────────────────────────────────────────
def sidebar_navigation():
    user = st.session_state.user

    with st.sidebar:
        # En-tête utilisateur
        st.markdown(f"""
        <div class='sidebar-header'>
            <div class='sidebar-avatar'>{user['prenom'][0]}{user['nom'][0]}</div>
            <div class='sidebar-user-info'>
                <div class='sidebar-name'>{user['prenom']} {user['nom']}</div>
                <div class='sidebar-role'>{user['formation']} · {user['annee']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
       

        # Progression
        progress = user.get("progression", 0)
        st.markdown("### 📊 Ma progression")
        st.progress(progress / 100, text=f"{progress}% du cours complété")

        st.markdown("---")

        # Déconnexion
        if st.button("🚪 Se déconnecter", use_container_width=True, type="secondary"):
            deconnecter()
            st.rerun()

        st.markdown("""
        <div style='text-align:center;font-size:10px;color:#9ca3af;margin-top:16px;'>
        FinLearn v1.0 · © 2025<br>
        Données en temps réel via Yahoo Finance
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ROUTEUR DE PAGES
# ─────────────────────────────────────────────────────────────
def router():
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    page = st.session_state.get("page", "dashboard")

    if page == "dashboard":
        from pages.dashboard import render
        render()
    elif page == "actions":
        from pages.actions import render
        render()
    elif page == "obligations":
        from pages.obligations import render
        render()
    elif page == "derives":
        from pages.derives import render
        render()
    elif page == "fonds":
        from pages.fonds import render
        render()
    elif page == "forex":
        from pages.forex import render
        render()
    elif page == "monetaire":
        from pages.monetaire import render
        render()
    elif page == "quiz":
        from pages.quiz import render
        render()
    elif page == "simulateur":
        from pages.simulateur import render
        render()
    elif page == "glossaire":
        from pages.glossaire import render
        render()
    else:
        from pages.dashboard import render
        render()


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE PRINCIPAL
# ─────────────────────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        page_connexion()
    else:
        sidebar_navigation()
        router()


if __name__ == "__main__":
    main()
