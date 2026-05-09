"""Simulateur de marché — FinLearn"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#065f46,#10b981);'>📈</div>
        <div>
            <p class='page-title'>Simulateur de Marché</p>
            <p class='page-subtitle'>Gérez un portefeuille virtuel et apprenez par la pratique</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Init portefeuille
    if "portef_cash" not in st.session_state:
        st.session_state.portef_cash = 10000.0
    if "portef_positions" not in st.session_state:
        st.session_state.portef_positions = {}
    if "portef_historique" not in st.session_state:
        st.session_state.portef_historique = []

    ACTIFS = {
        "Action A (Tech)":    {"prix": 150.0, "vol": 0.02, "mu": 0.0005},
        "Action B (Finance)": {"prix": 80.0,  "vol": 0.015,"mu": 0.0003},
        "Action C (Énergie)": {"prix": 45.0,  "vol": 0.025,"mu": 0.0004},
        "Obligation 5%":      {"prix": 1000.0,"vol": 0.003,"mu": 0.0001},
        "ETF Monde":          {"prix": 320.0, "vol": 0.012,"mu": 0.0004},
    }

    # Mise à jour des prix (simulation GBM)
    if "sim_prix" not in st.session_state:
        st.session_state.sim_prix = {k: v["prix"] for k, v in ACTIFS.items()}
    if "sim_historique_prix" not in st.session_state:
        st.session_state.sim_historique_prix = {k: [v["prix"]] for k, v in ACTIFS.items()}
    if "sim_jour" not in st.session_state:
        st.session_state.sim_jour = 0

    tabs = st.tabs(["💼 Mon Portefeuille", "🏪 Marché", "📊 Analyse", "ℹ️ Règles"])

    with tabs[0]:
        col_cash, col_val, col_total, col_pnl = st.columns(4)
        val_positions = sum(
            st.session_state.portef_positions.get(actif, 0) * st.session_state.sim_prix.get(actif, 0)
            for actif in ACTIFS
        )
        total = st.session_state.portef_cash + val_positions
        pnl   = total - 10000
        col_cash.metric("💵 Liquidités", f"{st.session_state.portef_cash:,.2f} €")
        col_val.metric("📦 Positions", f"{val_positions:,.2f} €")
        col_total.metric("💼 Valeur totale", f"{total:,.2f} €")
        col_pnl.metric("📈 P&L", f"{pnl:+,.2f} €", delta=f"{pnl/100:.2f}%")

        st.markdown("### Positions ouvertes")
        if not any(v > 0 for v in st.session_state.portef_positions.values()):
            st.info("Aucune position ouverte. Rendez-vous dans l'onglet **Marché** pour acheter.")
        else:
            rows = []
            for actif, qte in st.session_state.portef_positions.items():
                if qte > 0:
                    prix_act = st.session_state.sim_prix.get(actif, 0)
                    val      = qte * prix_act
                    prix_acq = ACTIFS[actif]["prix"]
                    pnl_pos  = (prix_act - prix_acq) / prix_acq * 100
                    rows.append({"Actif": actif, "Qté": qte, "Prix actuel": f"{prix_act:.2f}€",
                                 "Valeur": f"{val:.2f}€", "P&L (%)": f"{pnl_pos:+.1f}%"})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        # Historique des transactions
        if st.session_state.portef_historique:
            with st.expander("📋 Historique des transactions"):
                df_hist = pd.DataFrame(st.session_state.portef_historique)
                st.dataframe(df_hist, hide_index=True, use_container_width=True)

        if st.button("🔄 Simuler 1 journée de marché", type="primary", use_container_width=True):
            for actif, params in ACTIFS.items():
                vol = params["vol"]
                mu  = params["mu"]
                choc = np.random.normal(mu, vol)
                ancien = st.session_state.sim_prix[actif]
                nouveau = ancien * (1 + choc)
                nouveau = max(nouveau, 1.0)
                st.session_state.sim_prix[actif] = round(nouveau, 4)
                st.session_state.sim_historique_prix[actif].append(round(nouveau, 4))
            st.session_state.sim_jour += 1
            st.rerun()

        col_rst1, col_rst2 = st.columns([1, 3])
        with col_rst1:
            if st.button("♻️ Réinitialiser", use_container_width=True):
                st.session_state.portef_cash = 10000.0
                st.session_state.portef_positions = {}
                st.session_state.portef_historique = []
                st.session_state.sim_prix = {k: v["prix"] for k, v in ACTIFS.items()}
                st.session_state.sim_historique_prix = {k: [v["prix"]] for k, v in ACTIFS.items()}
                st.session_state.sim_jour = 0
                st.rerun()

    with tabs[1]:
        st.markdown(f"### 🏪 Marché — Jour {st.session_state.sim_jour}")
        for actif, params in ACTIFS.items():
            prix_act = st.session_state.sim_prix.get(actif, params["prix"])
            variation = (prix_act - params["prix"]) / params["prix"] * 100
            col_a, col_b, col_c, col_d, col_e = st.columns([2.5, 1, 1, 1, 1])
            with col_a:
                color = "#10b981" if variation >= 0 else "#ef4444"
                st.markdown(f"**{actif}** — "
                            f"<span style='color:{color}'>{prix_act:.2f} € ({variation:+.1f}%)</span>",
                            unsafe_allow_html=True)
            with col_b:
                qte_a = st.number_input("Qté", 1, 1000, 1, key=f"qte_{actif}", label_visibility="collapsed")
            with col_c:
                if st.button("🟢 Acheter", key=f"buy_{actif}", use_container_width=True):
                    cout = qte_a * prix_act
                    if cout <= st.session_state.portef_cash:
                        st.session_state.portef_cash -= cout
                        st.session_state.portef_positions[actif] = \
                            st.session_state.portef_positions.get(actif, 0) + qte_a
                        st.session_state.portef_historique.append({
                            "Jour": st.session_state.sim_jour, "Type": "ACHAT",
                            "Actif": actif, "Qté": qte_a,
                            "Prix": prix_act, "Total": f"-{cout:.2f}€"
                        })
                        st.success(f"✅ Acheté {qte_a}x {actif} à {prix_act:.2f}€")
                        st.rerun()
                    else:
                        st.error("❌ Liquidités insuffisantes")
            with col_d:
                if st.button("🔴 Vendre", key=f"sell_{actif}", use_container_width=True):
                    dispo = st.session_state.portef_positions.get(actif, 0)
                    if dispo >= qte_a:
                        recette = qte_a * prix_act
                        st.session_state.portef_cash += recette
                        st.session_state.portef_positions[actif] -= qte_a
                        st.session_state.portef_historique.append({
                            "Jour": st.session_state.sim_jour, "Type": "VENTE",
                            "Actif": actif, "Qté": qte_a,
                            "Prix": prix_act, "Total": f"+{recette:.2f}€"
                        })
                        st.success(f"✅ Vendu {qte_a}x {actif} à {prix_act:.2f}€")
                        st.rerun()
                    else:
                        st.error(f"❌ Vous n'avez que {dispo} titres")

    with tabs[2]:
        st.markdown("### 📊 Évolution des prix")
        fig_sim = go.Figure()
        colors = ["#60a5fa","#10b981","#f59e0b","#a855f7","#ef4444"]
        for i, (actif, hist) in enumerate(st.session_state.sim_historique_prix.items()):
            if len(hist) > 1:
                perf = [(p / hist[0] - 1) * 100 for p in hist]
                fig_sim.add_trace(go.Scatter(
                    y=perf, mode="lines", name=actif,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        fig_sim.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=350, xaxis_title="Jours simulés", yaxis_title="Performance (%)",
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
            legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=0,r=0,t=10,b=0)
        )
        st.plotly_chart(fig_sim, use_container_width=True, config={"displayModeBar": False})

    with tabs[3]:
        st.markdown("""
        ### Règles du simulateur
        - Vous démarrez avec **10 000 €** de liquidités virtuelles
        - Achetez et vendez les actifs disponibles au prix du marché simulé
        - Cliquez sur **Simuler 1 journée** pour faire avancer le temps
        - Les prix suivent un mouvement brownien géométrique (GBM) réaliste
        - Objectif : maximiser votre P&L (gain/perte)

        ### Concepts appris
        - Gestion de portefeuille et allocation d'actifs
        - Effet de la diversification sur le risque
        - Calcul du P&L (Profit and Loss)
        - Lecture des cours et variations de marché
        """)
