"""
pages/prof_dashboard.py
========================
Interface complète pour les professeurs.
Accessible uniquement aux utilisateurs avec role = 'professeur' ou 'admin'.

Fonctionnalités :
- Vue globale de tous les étudiants
- Gestion des accès aux modules (débloquer/bloquer)
- Suivi de la progression par étudiant
- Consultation et notation des résultats de quiz
- Envoi de notifications aux étudiants
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from utils.database import (
    get_all_etudiants,
    get_module_access,
    set_module_access,
    set_all_modules_access,
    get_progression_etudiant,
    get_progression_globale,
    get_quiz_results_all,
    get_quiz_results_etudiant,
    add_note_prof,
    send_notification,
    get_notifications,
    MODULES,
    MODULES_LIBRES,
)
from utils.auth import get_user_info

# ─────────────────────────────────────────────────────────────
# LABELS LISIBLES POUR LES MODULES
# ─────────────────────────────────────────────────────────────
MODULE_LABELS = {
    "dashboard":   "🏠 Tableau de bord",
    "actions":     "📊 Actions & Marchés",
    "obligations": "💼 Obligations",
    "derives":     "🔄 Produits Dérivés",
    "fonds":       "🏦 Fonds d'investissement",
    "forex":       "💱 Forex & Crypto",
    "monetaire":   "🏗️ Marchés Monétaires",
    "quiz":        "📝 Quiz interactifs",
    "simulateur":  "📈 Simulateur marché",
    "glossaire":   "📖 Glossaire",
}


def render():
    """Point d'entrée de la page professeur."""
    user = get_user_info()

    # ── Vérification du rôle ──────────────────────────────────
    # Seuls les professeurs et admins peuvent accéder à cette page
    if user.get("role") not in ("professeur", "admin"):
        st.error("🔒 Accès réservé aux professeurs et administrateurs.")
        st.stop()

    # ── En-tête de la page ────────────────────────────────────
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#7c3aed,#a855f7);'>👨‍🏫</div>
        <div>
            <p class='page-title'>Espace Professeur</p>
            <p class='page-subtitle'>
                Bienvenue, {user.get('prenom', '')} {user.get('nom', '')} ·
                {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Onglets principaux ────────────────────────────────────
    tabs = st.tabs([
        "📊 Vue globale",
        "🎓 Gestion des étudiants",
        "🔓 Accès aux modules",
        "📝 Notes & Résultats",
        "🔔 Notifications",
    ])

    # ════════════════════════════════════════════════════════
    # ONGLET 1 — VUE GLOBALE
    # ════════════════════════════════════════════════════════
    with tabs[0]:
        _render_vue_globale(user)

    # ════════════════════════════════════════════════════════
    # ONGLET 2 — GESTION DES ÉTUDIANTS (fiche individuelle)
    # ════════════════════════════════════════════════════════
    with tabs[1]:
        _render_fiche_etudiant(user)

    # ════════════════════════════════════════════════════════
    # ONGLET 3 — GESTION DES ACCÈS AUX MODULES
    # ════════════════════════════════════════════════════════
    with tabs[2]:
        _render_gestion_acces(user)

    # ════════════════════════════════════════════════════════
    # ONGLET 4 — NOTES ET RÉSULTATS
    # ════════════════════════════════════════════════════════
    with tabs[3]:
        _render_notes_resultats(user)

    # ════════════════════════════════════════════════════════
    # ONGLET 5 — NOTIFICATIONS
    # ════════════════════════════════════════════════════════
    with tabs[4]:
        _render_notifications(user)


# ─────────────────────────────────────────────────────────────
# VUE GLOBALE
# ─────────────────────────────────────────────────────────────

def _render_vue_globale(user):
    """Tableau de bord résumé de toute la classe."""
    st.markdown("## 📊 Vue d'ensemble de la classe")

    etudiants = get_all_etudiants()

    if not etudiants:
        st.info("📭 Aucun étudiant inscrit pour l'instant. "
                "Les étudiants apparaîtront ici dès leur première connexion.")
        return

    # ── Métriques globales ────────────────────────────────────
    nb_etu = len(etudiants)
    scores = [e["score_moyen"] for e in etudiants if e["score_moyen"] is not None]
    score_moy_classe = round(sum(scores) / len(scores), 1) if scores else 0
    nb_actifs = sum(1 for e in etudiants if e.get("last_login"))
    mods_moy  = round(sum(e["modules_debloques"] for e in etudiants) / nb_etu, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Étudiants inscrits",    nb_etu)
    c2.metric("📈 Score moyen classe",    f"{score_moy_classe}/20")
    c3.metric("✅ Étudiants connectés",   nb_actifs)
    c4.metric("📦 Modules débloqués moy", f"{mods_moy}/{len(MODULES)}")

    st.markdown("---")

    # ── Tableau récapitulatif de tous les étudiants ───────────
    st.markdown("### 📋 Liste des étudiants")

    rows = []
    for e in etudiants:
        prog_globale = get_progression_globale(e["id"])
        rows.append({
            "Nom":          e["nom"],
            "Prénom":       e["prenom"],
            "Formation":    e.get("formation", "N/A"),
            "Modules ✅":   f"{e['modules_debloques']}/{len(MODULES)}",
            "Progression":  f"{prog_globale:.0f}%",
            "Score moyen":  f"{e['score_moyen']:.1f}/20" if e["score_moyen"] else "—",
            "Dernière co.": e.get("last_login", "Jamais")[:16] if e.get("last_login") else "Jamais",
        })

    df = pd.DataFrame(rows)

    # Coloration conditionnelle du score
    def colorier_score(val):
        try:
            note = float(val.split("/")[0])
            if note >= 14:
                return "background-color:#1B4332;color:#D4EDDA"
            elif note >= 10:
                return "background-color:#856404;color:#FFF3CD"
            else:
                return "background-color:#721c24;color:#F8D7DA"
        except Exception:
            return ""

    st.dataframe(
        df.style.map(colorier_score, subset=["Score moyen"]),
        use_container_width=True, hide_index=True
    )

    # ── Graphiques de distribution ────────────────────────────
    if scores:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_hist = px.histogram(
                scores, nbins=10,
                title="Distribution des scores (/20)",
                labels={"value": "Score moyen (/20)", "count": "Nb étudiants"},
                color_discrete_sequence=["#7c3aed"]
            )
            fig_hist.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a", height=260,
                margin=dict(l=0, r=0, t=30, b=0), showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True,
                            config={"displayModeBar": False})

        with col_g2:
            # Répartition modules débloqués
            mods_count = [e["modules_debloques"] for e in etudiants]
            fig_bar = px.bar(
                x=[f"Étudiant {i+1}" for i in range(len(mods_count))],
                y=mods_count,
                title="Modules débloqués par étudiant",
                labels={"x": "", "y": "Nb modules"},
                color=mods_count,
                color_continuous_scale="Viridis"
            )
            fig_bar.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a",
                plot_bgcolor="#0f172a", height=260,
                margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True,
                            config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────
# FICHE ÉTUDIANT INDIVIDUELLE
# ─────────────────────────────────────────────────────────────

def _render_fiche_etudiant(user):
    """Vue détaillée d'un étudiant en particulier."""
    st.markdown("## 🎓 Fiche étudiant")

    etudiants = get_all_etudiants()
    if not etudiants:
        st.info("Aucun étudiant inscrit.")
        return

    # Sélection de l'étudiant
    options = {f"{e['prenom']} {e['nom']} — {e.get('formation','N/A')}": e
               for e in etudiants}
    choix = st.selectbox("Sélectionner un étudiant", list(options.keys()))
    etu = options[choix]

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(f"""
        **Nom complet :** {etu['prenom']} {etu['nom']}
        **Email :** {etu['email']}
        **Formation :** {etu.get('formation', 'N/A')}
        **Université :** {etu.get('universite', 'N/A')}
        """)
    with col_info2:
        prog = get_progression_globale(etu["id"])
        score = etu.get("score_moyen")
        st.metric("Progression globale", f"{prog:.0f}%")
        st.metric("Score moyen", f"{score:.1f}/20" if score else "—")
        st.metric("Dernière connexion",
                  etu.get("last_login", "Jamais")[:16] if etu.get("last_login") else "Jamais")

    st.markdown("---")

    # ── Progression par module ────────────────────────────────
    st.markdown("### 📈 Progression par module")
    prog_detail = get_progression_etudiant(etu["id"])
    access      = get_module_access(etu["id"])

    rows_prog = []
    for mod in MODULES:
        info = prog_detail.get(mod, {})
        rows_prog.append({
            "Module":         MODULE_LABELS.get(mod, mod),
            "Accès":          "✅ Débloqué" if access.get(mod) else "🔒 Bloqué",
            "Progression":    f"{info.get('pct_complete', 0):.0f}%",
            "Nb visites":     info.get("nb_visites", 0),
            "Dernière visite": (info.get("derniere_visite", "—") or "—")[:16],
        })

    df_prog = pd.DataFrame(rows_prog)

    def colorier_acces(val):
        if "Débloqué" in str(val):
            return "color:#10b981;font-weight:600"
        return "color:#ef4444;font-weight:600"

    st.dataframe(
        df_prog.style.map(colorier_acces, subset=["Accès"]),
        use_container_width=True, hide_index=True
    )

    # ── Résultats de quiz de cet étudiant ─────────────────────
    st.markdown("### 📝 Résultats aux quiz")
    resultats = get_quiz_results_etudiant(etu["id"])

    if not resultats:
        st.info("Cet étudiant n'a pas encore passé de quiz.")
    else:
        rows_quiz = []
        for res in resultats:
            note_sur_20 = (res["score"] / res["score_max"] * 20) if res["score_max"] else 0
            rows_quiz.append({
                "ID":          res["id"],
                "Module":      MODULE_LABELS.get(res["module_key"], res["module_key"]),
                "Thème":       res.get("theme") or "Général",
                "Score":       f"{res['score']:.1f}/{res['score_max']:.0f}",
                "Note /20":    f"{note_sur_20:.1f}",
                "Correct.":    f"{res.get('nb_correctes',0)}/{res.get('nb_questions',0)}",
                "Note prof":   f"{res['note_prof']:.1f}" if res.get("note_prof") else "—",
                "Commentaire": res.get("commentaire") or "—",
                "Date":        (res.get("passe_le") or "—")[:16],
            })

        df_quiz = pd.DataFrame(rows_quiz)
        st.dataframe(df_quiz.drop(columns=["ID"]),
                     use_container_width=True, hide_index=True)

        # Permet au prof de noter directement depuis cette vue
        st.markdown("#### ✏️ Ajouter/modifier une note")
        result_ids = {f"#{r['ID']} — {r['Module']} ({r['Date']})": r["ID"]
                      for r in rows_quiz}
        choix_res = st.selectbox("Résultat à noter", list(result_ids.keys()),
                                  key="noter_ici")
        col_n1, col_n2 = st.columns([1, 2])
        with col_n1:
            note_nouvelle = st.number_input("Note /20", 0.0, 20.0, 10.0, 0.5,
                                             key="note_val_fiche")
        with col_n2:
            comment_nouveau = st.text_input("Commentaire (optionnel)",
                                             key="comment_val_fiche")
        if st.button("💾 Enregistrer la note", key="save_note_fiche",
                     type="primary"):
            add_note_prof(result_ids[choix_res], note_nouvelle, comment_nouveau)
            st.success(f"✅ Note {note_nouvelle}/20 enregistrée !")
            st.rerun()


# ─────────────────────────────────────────────────────────────
# GESTION DES ACCÈS AUX MODULES
# ─────────────────────────────────────────────────────────────

def _render_gestion_acces(user):
    """
    Interface principale pour débloquer/bloquer les modules.
    Le professeur peut agir étudiant par étudiant ou en masse.
    """
    st.markdown("## 🔓 Gestion des accès aux modules")
    st.info(
        "💡 **Comment ça marche :** Par défaut, seuls le Tableau de bord et le Glossaire "
        "sont accessibles. Cochez les cases pour débloquer un module pour un étudiant. "
        "Les modules verrouillés affichent un message d'accès refusé à l'étudiant."
    )

    etudiants = get_all_etudiants()
    if not etudiants:
        st.warning("Aucun étudiant inscrit.")
        return

    prof_id = user.get("db_id", 1)  # ID du prof dans la base

    # ── Mode de gestion ───────────────────────────────────────
    mode = st.radio(
        "Mode de gestion",
        ["Par étudiant", "Vue globale (tous les étudiants)", "Actions groupées"],
        horizontal=True
    )

    # ────────────────────────────────────────────────────────
    # MODE 1 : Par étudiant — tableau de cases à cocher
    # ────────────────────────────────────────────────────────
    if mode == "Par étudiant":
        options_etu = {f"{e['prenom']} {e['nom']}": e for e in etudiants}
        etu_choisi  = st.selectbox("Étudiant", list(options_etu.keys()),
                                    key="etu_acces_sel")
        etu = options_etu[etu_choisi]
        access = get_module_access(etu["id"])

        st.markdown(f"### Modules de **{etu['prenom']} {etu['nom']}**")

        col_debloquer, col_bloquer = st.columns(2)
        with col_debloquer:
            if st.button("✅ Tout débloquer", use_container_width=True):
                set_all_modules_access(etu["id"], True, prof_id)
                st.success("Tous les modules débloqués !")
                st.rerun()
        with col_bloquer:
            if st.button("🔒 Tout bloquer", use_container_width=True):
                set_all_modules_access(etu["id"], False, prof_id)
                st.warning("Tous les modules bloqués !")
                st.rerun()

        st.markdown("---")

        # Affiche chaque module avec une case à cocher
        changements = {}
        for mod in MODULES:
            est_libre = mod in MODULES_LIBRES
            label     = MODULE_LABELS.get(mod, mod)

            if est_libre:
                # Module libre = toujours coché, désactivé
                st.checkbox(
                    f"{label} *(accès libre)*",
                    value=True,
                    disabled=True,
                    key=f"access_{etu['id']}_{mod}_disabled"
                )
            else:
                actuel = access.get(mod, False)
                nouveau = st.checkbox(
                    label,
                    value=actuel,
                    key=f"access_{etu['id']}_{mod}"
                )
                if nouveau != actuel:
                    changements[mod] = nouveau

        if changements:
            if st.button(f"💾 Enregistrer {len(changements)} changement(s)",
                         type="primary", use_container_width=True):
                for mod, val in changements.items():
                    set_module_access(etu["id"], mod, val, prof_id)
                    action = "débloqué" if val else "bloqué"
                    # Notifie l'étudiant
                    msg = (f"Le module **{MODULE_LABELS.get(mod, mod)}** "
                           f"vient d'être **{action}** par votre professeur.")
                    send_notification(prof_id, msg, etu["id"])
                st.success(f"✅ {len(changements)} modification(s) enregistrée(s) !")
                st.rerun()

    # ────────────────────────────────────────────────────────
    # MODE 2 : Vue globale — tableau croisé
    # ────────────────────────────────────────────────────────
    elif mode == "Vue globale (tous les étudiants)":
        st.markdown("### 🗂️ Tableau d'accès global")
        st.caption("🟢 = Débloqué · 🔴 = Bloqué · ⚪ = Accès libre")

        # Construction du tableau croisé
        data = {"Étudiant": []}
        for mod in MODULES:
            data[MODULE_LABELS.get(mod, mod)] = []

        for e in etudiants:
            data["Étudiant"].append(f"{e['prenom']} {e['nom']}")
            access = get_module_access(e["id"])
            for mod in MODULES:
                if mod in MODULES_LIBRES:
                    data[MODULE_LABELS.get(mod, mod)].append("⚪")
                elif access.get(mod):
                    data[MODULE_LABELS.get(mod, mod)].append("🟢")
                else:
                    data[MODULE_LABELS.get(mod, mod)].append("🔴")

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    # ────────────────────────────────────────────────────────
    # MODE 3 : Actions groupées — débloquer un module pour tous
    # ────────────────────────────────────────────────────────
    else:
        st.markdown("### ⚡ Actions groupées")
        st.markdown("Débloquez ou bloquez un module pour **tous les étudiants** en même temps.")

        mod_choisi = st.selectbox(
            "Module à gérer",
            [mod for mod in MODULES if mod not in MODULES_LIBRES],
            format_func=lambda m: MODULE_LABELS.get(m, m)
        )

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button(f"✅ Débloquer pour tous",
                         use_container_width=True, type="primary"):
                for e in etudiants:
                    set_module_access(e["id"], mod_choisi, True, prof_id)
                    send_notification(
                        prof_id,
                        f"Le module **{MODULE_LABELS.get(mod_choisi, mod_choisi)}** "
                        f"est maintenant accessible !",
                        e["id"]
                    )
                st.success(f"✅ Module **{MODULE_LABELS.get(mod_choisi)}** "
                           f"débloqué pour {len(etudiants)} étudiant(s) !")
                st.rerun()

        with col_a2:
            if st.button(f"🔒 Bloquer pour tous",
                         use_container_width=True):
                for e in etudiants:
                    set_module_access(e["id"], mod_choisi, False, prof_id)
                st.warning(f"🔒 Module bloqué pour tous les étudiants.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### Débloquer tout le programme pour un étudiant spécifique")
        options_etu2 = {f"{e['prenom']} {e['nom']}": e for e in etudiants}
        etu2 = st.selectbox("Étudiant", list(options_etu2.keys()), key="etu_groupe")
        if st.button("✅ Débloquer tout le programme", type="primary"):
            set_all_modules_access(options_etu2[etu2]["id"], True, prof_id)
            st.success(f"Programme complet débloqué pour {etu2} !")
            st.rerun()


# ─────────────────────────────────────────────────────────────
# NOTES ET RÉSULTATS
# ─────────────────────────────────────────────────────────────

def _render_notes_resultats(user):
    """Consultation et notation de tous les quiz passés par les étudiants."""
    st.markdown("## 📝 Notes et résultats")

    tous_resultats = get_quiz_results_all()

    if not tous_resultats:
        st.info("📭 Aucun résultat de quiz pour l'instant.")
        return

    # ── Filtres ────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        etudiants_noms = ["Tous"] + sorted(set(
            f"{r['prenom']} {r['nom']}" for r in tous_resultats
        ))
        filtre_etu = st.selectbox("Filtrer par étudiant", etudiants_noms)
    with col_f2:
        modules_dispo = ["Tous"] + sorted(set(r["module_key"] for r in tous_resultats))
        filtre_mod = st.selectbox("Filtrer par module",
                                   modules_dispo,
                                   format_func=lambda m: MODULE_LABELS.get(m, m)
                                              if m != "Tous" else "Tous")
    with col_f3:
        filtre_non_notes = st.checkbox("Afficher uniquement les non-notés", value=False)

    # Applique les filtres
    resultats = tous_resultats
    if filtre_etu != "Tous":
        resultats = [r for r in resultats
                     if f"{r['prenom']} {r['nom']}" == filtre_etu]
    if filtre_mod != "Tous":
        resultats = [r for r in resultats if r["module_key"] == filtre_mod]
    if filtre_non_notes:
        resultats = [r for r in resultats if not r.get("note_prof")]

    st.markdown(f"**{len(resultats)} résultat(s) affiché(s)**")

    # ── Tableau des résultats ─────────────────────────────────
    if not resultats:
        st.info("Aucun résultat ne correspond aux filtres.")
        return

    rows = []
    for res in resultats:
        note_sur_20 = (res["score"] / res["score_max"] * 20) if res["score_max"] else 0
        rows.append({
            "ID":          res["id"],
            "Étudiant":    f"{res['prenom']} {res['nom']}",
            "Module":      MODULE_LABELS.get(res["module_key"], res["module_key"]),
            "Score auto":  f"{res['score']:.1f}/{res['score_max']:.0f} ({note_sur_20:.1f}/20)",
            "Réponses":    f"{res.get('nb_correctes',0)}/{res.get('nb_questions',0)}",
            "Note prof":   f"✅ {res['note_prof']:.1f}/20" if res.get("note_prof") else "⏳ En attente",
            "Commentaire": res.get("commentaire") or "—",
            "Date":        (res.get("passe_le") or "—")[:16],
        })

    df_r = pd.DataFrame(rows)

    def colorier_note(val):
        if "✅" in str(val):
            return "color:#10b981"
        if "⏳" in str(val):
            return "color:#f59e0b"
        return ""

    st.dataframe(
        df_r.drop(columns=["ID"]).style.map(colorier_note, subset=["Note prof"]),
        use_container_width=True, hide_index=True
    )

    st.markdown("---")

    # ── Formulaire de notation ─────────────────────────────────
    st.markdown("### ✏️ Noter un résultat")

    result_options = {
        f"#{r['ID']} — {r['Étudiant']} · {r['Module']} · {r['Date']}": r["ID"]
        for r in rows
    }
    choix_res = st.selectbox("Résultat à noter", list(result_options.keys()))

    col_note1, col_note2 = st.columns([1, 2])
    with col_note1:
        note_val = st.number_input(
            "Note attribuée (/20)", min_value=0.0, max_value=20.0,
            value=10.0, step=0.5, key="note_input_main"
        )
    with col_note2:
        commentaire_val = st.text_area(
            "Commentaire pour l'étudiant",
            placeholder="Ex : Bonne maîtrise des options, revoir la duration...",
            height=80,
            key="comment_input_main"
        )

    if st.button("💾 Enregistrer la note", type="primary", use_container_width=True):
        result_id = result_options[choix_res]
        add_note_prof(result_id, note_val, commentaire_val)
        st.success(f"✅ Note {note_val}/20 enregistrée avec succès !")

        # Notifie l'étudiant
        # Retrouve l'étudiant concerné
        res_concerne = next((r for r in resultats if r["id"] == result_id), None)
        if res_concerne:
            msg = (f"Votre résultat sur **{MODULE_LABELS.get(res_concerne['module_key'], '')}** "
                   f"a été noté **{note_val}/20** par votre professeur."
                   + (f"\n💬 *{commentaire_val}*" if commentaire_val else ""))
            send_notification(
                user.get("db_id", 1),
                msg,
                res_concerne["etudiant_id"]
            )
        st.rerun()

    # ── Statistiques rapides ───────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Statistiques des résultats")

    notes_auto = [(r["score"] / r["score_max"] * 20) for r in resultats if r["score_max"]]
    notes_prof = [r["note_prof"] for r in resultats if r.get("note_prof")]

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Total résultats",  len(resultats))
    col_s2.metric("Moy. score auto",  f"{sum(notes_auto)/len(notes_auto):.1f}/20"
                                        if notes_auto else "—")
    col_s3.metric("Moy. note prof",   f"{sum(notes_prof)/len(notes_prof):.1f}/20"
                                        if notes_prof else "—")
    col_s4.metric("En attente",       sum(1 for r in resultats if not r.get("note_prof")))


# ─────────────────────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────────────────────

def _render_notifications(user):
    """Interface d'envoi de notifications aux étudiants."""
    st.markdown("## 🔔 Notifications & Messages")

    etudiants = get_all_etudiants()
    prof_id   = user.get("db_id", 1)

    # ── Formulaire d'envoi ─────────────────────────────────────
    st.markdown("### ✉️ Envoyer un message")

    destinataires = {"Tous les étudiants": None}
    for e in etudiants:
        destinataires[f"{e['prenom']} {e['nom']}"] = e["id"]

    dest_choix = st.selectbox("Destinataire", list(destinataires.keys()))
    message    = st.text_area(
        "Message",
        placeholder="Ex : Le module Obligations est maintenant débloqué. "
                    "Pensez à compléter le quiz avant vendredi.",
        height=100
    )

    if st.button("📤 Envoyer le message", type="primary"):
        if message.strip():
            dest_id = destinataires[dest_choix]
            send_notification(prof_id, message, dest_id)
            nb = len(etudiants) if dest_id is None else 1
            st.success(f"✅ Message envoyé à {dest_choix} ({nb} destinataire(s)) !")
            st.rerun()
        else:
            st.error("Veuillez écrire un message.")

    st.markdown("---")

    # ── Templates de messages rapides ─────────────────────────
    st.markdown("### ⚡ Messages rapides")
    templates = [
        "📚 Nouveau module débloqué ! Connectez-vous pour y accéder.",
        "📝 Pensez à compléter les quiz avant la prochaine séance.",
        "🎯 Bravo pour vos résultats ! Continuez comme ça.",
        "⚠️ Certains modules nécessitent d'être repassés. Revoyez le cours.",
        "📅 Rappel : La session de révision est prévue jeudi prochain.",
    ]
    for tpl in templates:
        col_tpl1, col_tpl2 = st.columns([4, 1])
        with col_tpl1:
            st.markdown(f"*{tpl}*")
        with col_tpl2:
            if st.button("Envoyer à tous", key=f"tpl_{tpl[:20]}"):
                send_notification(prof_id, tpl, None)
                st.success("✅ Envoyé à tous !")
                st.rerun()

    st.markdown("---")

    # ── Notifications des profs non lues ──────────────────────
    st.markdown("### 📬 Mes notifications")
    notifs = get_notifications(prof_id)
    if not notifs:
        st.info("📭 Aucune notification en attente.")
    else:
        for n in notifs:
            with st.expander(f"🔔 {n['expediteur']} — {n['cree_le'][:16]}"):
                st.write(n["message"])
