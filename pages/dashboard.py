"""Tableau de bord principal — FinLearn"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from utils.market_data import (
    get_quote, get_history, get_multiple_quotes,
    INDICES, ACTIONS_VEDETTES, FOREX_PAIRS, CRYPTOS
)
from utils.auth import get_user_info
from utils.database import (
    get_module_access, get_notifications, count_notifications_non_lues,
    marquer_notification_lue, marquer_toutes_lues,
    get_user_db_id, create_or_update_user, init_db,
)


def _get_db_id(user: dict) -> int | None:
    """
    Retourne l'id SQLite de l'utilisateur connecté.
    Crée l'entrée en base si elle n'existe pas encore (premier login via ENT/démo).
    """
    db_id = user.get("db_id")
    if db_id:
        return db_id

    email = user.get("email", "")
    if not email:
        return None

    db_id = get_user_db_id(email)
    if not db_id:
        db_id = create_or_update_user(
            email=email,
            nom=user.get("nom", ""),
            prenom=user.get("prenom", ""),
            role=user.get("role", "etudiant"),
            formation=user.get("formation", ""),
            universite=user.get("universite", ""),
        )
    # Stocke dans la session pour ne pas refaire la requête à chaque rerun
    st.session_state.user["db_id"] = db_id
    return db_id


def _render_notifications(db_id: int):
    """
    Panneau de notifications dans la sidebar.
    Affiché uniquement si l'utilisateur a un id SQLite.
    """
    nb_non_lues = count_notifications_non_lues(db_id)

    with st.sidebar:
        st.markdown("---")
        label = (f"🔔 Notifications **({nb_non_lues} nouvelle{'s' if nb_non_lues > 1 else ''})**"
                 if nb_non_lues else "🔔 Notifications")
        with st.expander(label, expanded=(nb_non_lues > 0)):
            notifs = get_notifications(db_id)
            if not notifs:
                st.caption("Aucune notification pour l'instant.")
            else:
                if nb_non_lues:
                    if st.button("✅ Tout marquer comme lu", key="mark_all_read"):
                        marquer_toutes_lues(db_id)
                        st.rerun()

                for n in notifs:
                    is_new = not n["lu"]
                    border_color = "#7c3aed" if is_new else "#334155"
                    bg_color     = "#1e1b4b" if is_new else "#1e293b"
                    badge        = " 🆕" if is_new else ""
                    date_str     = (n.get("cree_le") or "")[:16]

                    st.markdown(f"""
                    <div style='padding:10px 12px;background:{bg_color};
                                border-left:3px solid {border_color};
                                border-radius:6px;margin-bottom:8px;'>
                        <div style='font-size:11px;color:#94a3b8;margin-bottom:4px;'>
                            {n.get('expediteur_nom','Professeur')} · {date_str}{badge}
                        </div>
                        <div style='font-size:13px;color:#e2e8f0;'>{n['message']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if is_new:
                        if st.button("Marquer lu", key=f"notif_lu_{n['id']}",
                                     use_container_width=True):
                            marquer_notification_lue(n["id"])
                            st.rerun()


def render():
    # S'assure que la BDD est initialisée
    init_db()

    user   = get_user_info()
    db_id  = _get_db_id(user)

    # Accès modules depuis SQLite (source de vérité unique)
    access = get_module_access(db_id) if db_id else {m: (m in ["dashboard","glossaire","quiz"]) for m in ["dashboard","actions","obligations","derives","fonds","forex","monetaire","quiz","simulateur","glossaire"]}

    # ── Notifications dans la sidebar ─────────────────────────
    if db_id:
        _render_notifications(db_id)

    # ── En-tête ────────────────────────────────────────────────
    now = datetime.now()
    nb_notifs = count_notifications_non_lues(db_id) if db_id else 0
    notif_badge = f" 🔔{nb_notifs}" if nb_notifs else ""

    st.markdown(f"""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#1d4ed8,#7c3aed);'>🏠</div>
        <div>
            <p class='page-title'>Bonjour, {user.get('prenom', 'Étudiant')} 👋{notif_badge}</p>
            <p class='page-subtitle'>
                {now.strftime('%A %d %B %Y')} · {now.strftime('%H:%M')} ·
                Marchés {'ouverts 🟢' if 9 <= now.hour < 18 else 'fermés 🔴'}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bannière ticker temps réel ─────────────────────────────
    with st.container():
        cols = st.columns(len(INDICES))
        for col, (name, ticker) in zip(cols, INDICES.items()):
            q = get_quote(ticker)
            with col:
                st.metric(
                    label=name,
                    value=f"{q['price']:,.0f}",
                    delta=f"{q['pct']:+.2f}%",
                    delta_color="normal" if q["pct"] >= 0 else "inverse"
                )

    st.markdown("---")

    # ── Progression étudiant ───────────────────────────────────
    col_prog, col_stats = st.columns([1.5, 1])

    with col_prog:
        st.markdown("### 🎓 Mes modules")

        modules_info = [
            ("📊 Actions & Marchés",       "actions"),
            ("💼 Obligations",             "obligations"),
            ("🔄 Produits Dérivés",        "derives"),
            ("🏦 Fonds d'investissement",  "fonds"),
            ("💱 Forex & Crypto",          "forex"),
            ("🏗️ Marchés Monétaires",     "monetaire"),
        ]

        modules_completes = user.get("modules_completes", [])
        nb_total    = len(modules_info)
        nb_debloques = sum(1 for _, key in modules_info if access.get(key))
        nb_completes = sum(1 for _, key in modules_info if key in modules_completes)
        prog = round(nb_completes / nb_total * 100) if nb_total else 0

        st.progress(prog / 100, text=f"**{prog}%** du programme complété")
        st.markdown("<br>", unsafe_allow_html=True)

        for label, key in modules_info:
            debloque  = access.get(key, False)
            complete  = key in modules_completes

            if complete:
                status_html = "<span class='module-badge-done'>✓ Complété</span>"
                border      = "#10b981"
            elif debloque:
                status_html = "<span style='background:#1d4ed8;color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;'>🔓 Disponible</span>"
                border      = "#1d4ed8"
            else:
                status_html = "<span style='background:#374151;color:#9ca3af;padding:2px 8px;border-radius:12px;font-size:11px;'>🔒 Verrouillé</span>"
                border      = "#334155"

            # Bouton cliquable si débloqué
            if debloque:
                col_label, col_badge, col_btn = st.columns([3, 2, 1])
                with col_label:
                    st.markdown(f"<div style='padding:8px 0;font-size:14px;color:#e2e8f0'>{label}</div>", unsafe_allow_html=True)
                with col_badge:
                    st.markdown(f"<div style='padding:8px 0'>{status_html}</div>", unsafe_allow_html=True)
                with col_btn:
                    module_key_map = {
                        "actions": "actions", "obligations": "obligations",
                        "derives": "derives", "fonds": "fonds",
                        "forex": "forex", "monetaire": "monetaire",
                    }
                    if st.button("→", key=f"goto_{key}", use_container_width=True):
                        st.session_state.page = module_key_map[key]
                        st.rerun()
            else:
                st.markdown(f"""
                <div style='display:flex;align-items:center;justify-content:space-between;
                            padding:10px 14px;background:#1e293b;border-radius:8px;
                            margin-bottom:6px;border:1px solid {border};opacity:0.6'>
                    <span style='font-size:14px;color:#e2e8f0'>{label}</span>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)

    with col_stats:
        st.markdown("### 📈 Mes statistiques")
        score       = user.get("score_moyen", 0)
        nb_completes_count = len(modules_completes)

        st.metric("Score moyen",        f"{score:.1f}/20",
                  delta=f"{score-10:+.1f} vs moyenne")
        st.metric("Modules complétés",  f"{nb_completes_count}/6")
        st.metric("Modules disponibles", f"{nb_debloques}/6")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏆 Badges obtenus")
        badges = []
        if score >= 10:              badges.append("🥉 Débutant")
        if score >= 14:              badges.append("🥈 Confirmé")
        if score >= 17:              badges.append("🥇 Expert")
        if nb_completes_count >= 3:  badges.append("📚 Studieux")
        if nb_completes_count >= 6:  badges.append("🎓 Diplômé")
        if not badges:               badges = ["🎯 En cours..."]
        for b in badges:
            st.markdown(f"<span class='module-badge-done'>{b}</span> ",
                        unsafe_allow_html=True)

    st.markdown("---")

    # ── Graphique marché principal ─────────────────────────────
    st.markdown("### 📊 Évolution des marchés")

    col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])
    with col_sel1:
        marche_choisi = st.selectbox("Indice / Actif",
                                     list(INDICES.keys()) + list(ACTIONS_VEDETTES.keys()),
                                     index=0)
    with col_sel2:
        periode = st.selectbox("Période",
                               ["1 semaine", "1 mois", "3 mois", "6 mois", "1 an"],
                               index=2)
    with col_sel3:
        type_graph = st.selectbox("Type", ["Ligne", "Chandeliers"])

    periode_map = {"1 semaine": "5d", "1 mois": "1mo", "3 mois": "3mo",
                   "6 mois": "6mo", "1 an": "1y"}
    all_tickers = {**INDICES, **ACTIONS_VEDETTES}
    ticker_sel  = all_tickers.get(marche_choisi, "^FCHI")
    hist        = get_history(ticker_sel, period=periode_map[periode])

    if not hist.empty:
        fig = go.Figure()
        color_line = "#10b981" if hist["Close"].iloc[-1] >= hist["Close"].iloc[0] else "#ef4444"

        if type_graph == "Ligne":
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"],
                mode="lines",
                line=dict(color=color_line, width=2),
                fill="tozeroy",
                fillcolor=f"rgba({int(color_line[1:3],16)},{int(color_line[3:5],16)},{int(color_line[5:7],16)},0.08)",
                name=marche_choisi,
            ))
        else:
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"], high=hist["High"],
                low=hist["Low"],   close=hist["Close"],
                increasing_line_color="#10b981",
                decreasing_line_color="#ef4444",
                name=marche_choisi,
            ))

        fig.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#94a3b8"),
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="#1e293b", showgrid=True, zeroline=False),
            yaxis=dict(gridcolor="#1e293b", showgrid=True, zeroline=False),
            showlegend=False, hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── Tableau marchés en temps réel ─────────────────────────
    col_tab1, col_tab2 = st.columns(2)

    with col_tab1:
        st.markdown("### 🇫🇷 Actions françaises")
        df_fr = get_multiple_quotes(
            {k: v for k, v in ACTIONS_VEDETTES.items() if ".PA" in v or ".MI" in v}
        )
        st.dataframe(
            df_fr.style.map(
                lambda v: "color:#10b981" if isinstance(v, (int, float)) and v > 0 else "color:#ef4444",
                subset=["Variation", "Var. (%)"]
            ),
            use_container_width=True, hide_index=True
        )

    with col_tab2:
        st.markdown("### 🌍 Indices mondiaux")
        df_idx = get_multiple_quotes(INDICES)
        st.dataframe(
            df_idx.style.map(
                lambda v: "color:#10b981" if isinstance(v, (int, float)) and v > 0 else "color:#ef4444",
                subset=["Variation", "Var. (%)"]
            ),
            use_container_width=True, hide_index=True
        )

    st.markdown("---")

    # ── Concept du jour ────────────────────────────────────────
    st.markdown("### 📰 Concept du jour")
    concepts = [
        {
            "titre":   "La courbe des taux (yield curve)",
            "contenu": """La **courbe des taux** représente les rendements obligataires en fonction de leur maturité.
            Une courbe **normale** est croissante : les taux longs > taux courts.
            Une courbe **inversée** (taux courts > taux longs) est souvent annonciateur de récession.
            **Exemple :** Si le taux US à 2 ans est à 4.8% et le taux à 10 ans à 4.2%, la courbe est inversée.""",
            "formule": "Spread = Taux 10 ans − Taux 2 ans",
            "couleur": "#7c3aed",
        },
    ]
    concept = concepts[now.day % len(concepts)]
    st.markdown(f"""
    <div class='fin-card' style='border-color:{concept["couleur"]}'>
        <div class='fin-card-header'>
            <div class='fin-card-icon' style='background:rgba(124,58,237,0.15)'>💡</div>
            <div class='fin-card-title'>{concept["titre"]}</div>
        </div>
        <div class='fin-card-desc'>{concept["contenu"]}</div>
        <div style='margin-top:12px;background:#0f172a;padding:10px 14px;border-radius:8px;
                    font-family:JetBrains Mono,monospace;font-size:13px;color:#60a5fa'>
            📐 {concept["formule"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center;font-size:11px;color:#475569;margin-top:24px;
                padding-top:16px;border-top:1px solid #1e293b'>
        Données fournies par Yahoo Finance · Mis à jour le {now.strftime('%d/%m/%Y à %H:%M')} ·
        À des fins éducatives uniquement — Non destiné à des conseils en investissement
    </div>
    """, unsafe_allow_html=True)
