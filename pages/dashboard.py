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


def render():
    user = get_user_info()

    # ── En-tête ────────────────────────────────────────────────
    now = datetime.now()
    st.markdown(f"""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#1d4ed8,#7c3aed);'>🏠</div>
        <div>
            <p class='page-title'>Bonjour, {user.get('prenom', 'Étudiant')} 👋</p>
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
                delta_color = "normal" if q["pct"] >= 0 else "inverse"
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
        st.markdown("### 🎓 Ma progression académique")
        modules = [
            ("📊 Actions & Marchés",      "actions",     user.get("progression", 0) >= 20),
            ("💼 Obligations",            "obligations", user.get("progression", 0) >= 40),
            ("🔄 Produits Dérivés",       "derives",     user.get("progression", 0) >= 60),
            ("🏦 Fonds d'investissement", "fonds",       user.get("progression", 0) >= 70),
            ("💱 Forex & Crypto",         "forex",       user.get("progression", 0) >= 85),
            ("🏗️ Marchés Monétaires",    "monetaire",   user.get("progression", 0) >= 100),
        ]
        prog = user.get("progression", 0)
        st.progress(prog / 100, text=f"**{prog}%** du programme complété")
        st.markdown("<br>", unsafe_allow_html=True)
        for label, key, done in modules:
            badge = "<span class='module-badge-done'>✓ Complété</span>" if done else "<span class='module-badge-todo'>À faire</span>"
            st.markdown(f"""
            <div style='display:flex;align-items:center;justify-content:space-between;
                        padding:10px 14px;background:#1e293b;border-radius:8px;
                        margin-bottom:6px;border:1px solid {"#10b981" if done else "#334155"}'>
                <span style='font-size:14px;color:#e2e8f0'>{label}</span>
                {badge}
            </div>
            """, unsafe_allow_html=True)

    with col_stats:
        st.markdown("### 📈 Mes statistiques")
        score = user.get("score_moyen", 0)
        nb_modules = len(user.get("modules_completes", []))

        st.metric("Score moyen", f"{score:.1f}/20", delta=f"+{score-10:.1f} vs moyenne")
        st.metric("Modules complétés", f"{nb_modules}/6")
        st.metric("Connexions", "3 cette semaine", delta="🔥 Régulier")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏆 Badges obtenus")
        badges = []
        if score >= 10: badges.append("🥉 Débutant")
        if score >= 14: badges.append("🥈 Confirmé")
        if score >= 17: badges.append("🥇 Expert")
        if nb_modules >= 3: badges.append("📚 Studieux")
        if nb_modules >= 6: badges.append("🎓 Diplômé")
        if not badges:
            badges = ["🎯 En cours..."]
        for b in badges:
            st.markdown(f"<span class='module-badge-done'>{b}</span> ", unsafe_allow_html=True)

    st.markdown("---")

    # ── Graphique marché principal ─────────────────────────────
    st.markdown("### 📊 Évolution des marchés")

    col_sel1, col_sel2, col_sel3 = st.columns([2, 2, 1])
    with col_sel1:
        marche_choisi = st.selectbox("Indice / Actif", list(INDICES.keys()) + list(ACTIONS_VEDETTES.keys()), index=0)
    with col_sel2:
        periode = st.selectbox("Période", ["1 semaine", "1 mois", "3 mois", "6 mois", "1 an"], index=2)
    with col_sel3:
        type_graph = st.selectbox("Type", ["Ligne", "Chandeliers"])

    periode_map = {"1 semaine": "5d", "1 mois": "1mo", "3 mois": "3mo", "6 mois": "6mo", "1 an": "1y"}
    all_tickers = {**INDICES, **ACTIONS_VEDETTES}
    ticker_sel  = all_tickers.get(marche_choisi, "^FCHI")

    hist = get_history(ticker_sel, period=periode_map[periode])

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
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#94a3b8"),
            height=320,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor="#1e293b", showgrid=True, zeroline=False),
            yaxis=dict(gridcolor="#1e293b", showgrid=True, zeroline=False),
            showlegend=False,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── Tableau marchés en temps réel ─────────────────────────
    col_tab1, col_tab2 = st.columns(2)

    with col_tab1:
        st.markdown("### 🇫🇷 Actions françaises")
        df_fr = get_multiple_quotes({k: v for k, v in ACTIONS_VEDETTES.items() if ".PA" in v or ".MI" in v})
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

    # ── Actualité pédagogique ──────────────────────────────────
    st.markdown("### 📰 Concept du jour")
    concepts = [
        {
            "titre": "La courbe des taux (yield curve)",
            "contenu": """La **courbe des taux** représente les rendements obligataires en fonction de leur maturité.
            Une courbe **normale** est croissante : les taux longs > taux courts.
            Une courbe **inversée** (taux courts > taux longs) est souvent annonciateur de récession.
            **Exemple :** Si le taux US à 2 ans est à 4.8% et le taux à 10 ans à 4.2%, la courbe est inversée.""",
            "formule": "Spread = Taux 10 ans − Taux 2 ans",
            "couleur": "#7c3aed",
        },
    ]
    c = concepts[datetime.now().day % len(concepts)]
    st.markdown(f"""
    <div class='fin-card' style='border-color:{c["couleur"]}'>
        <div class='fin-card-header'>
            <div class='fin-card-icon' style='background:rgba(124,58,237,0.15)'>💡</div>
            <div class='fin-card-title'>{c["titre"]}</div>
        </div>
        <div class='fin-card-desc'>{c["contenu"]}</div>
        <div style='margin-top:12px;background:#0f172a;padding:10px 14px;border-radius:8px;
                    font-family:JetBrains Mono,monospace;font-size:13px;color:#60a5fa'>
            📐 {c["formule"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pied de page
    st.markdown(f"""
    <div style='text-align:center;font-size:11px;color:#475569;margin-top:24px;padding-top:16px;
                border-top:1px solid #1e293b'>
        Données fournies par Yahoo Finance · Mis à jour le {datetime.now().strftime('%d/%m/%Y à %H:%M')} ·
        À des fins éducatives uniquement — Non destiné à des conseils en investissement
    </div>
    """, unsafe_allow_html=True)
