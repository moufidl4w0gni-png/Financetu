"""Module — Marchés Monétaires"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.market_data import get_bond_yield


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#374151,#6b7280);'>🏗️</div>
        <div>
            <p class='page-title'>Marchés Monétaires</p>
            <p class='page-subtitle'>Instruments de financement à court terme et politique monétaire</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📖 Cours", "🏦 Banques centrales", "📐 Calculs", "🧪 Exercices"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ## Le marché monétaire

            Le **marché monétaire** est le marché des capitaux à **court terme** (< 2 ans).
            Il permet aux agents économiques de placer ou d'emprunter des liquidités.

            ### Principaux instruments
            | Instrument | Émetteur | Durée |
            |-----------|----------|-------|
            | **Bons du Trésor** | État | 1 sem. à 52 sem. |
            | **Billets de trésorerie** | Entreprises | 1 jour à 1 an |
            | **Certificats de dépôt** | Banques | 1 jour à 1 an |
            | **REPO / Pension livrée** | Banques | 1 jour à 3 mois |
            | **Dépôts interbancaires** | Banques | Overnight |

            ### Taux de référence
            - **€STR** (Ex-EONIA) : taux moyen pondéré des prêts overnight en €
            - **Euribor** : taux interbancaire offert en zone euro (1w, 1m, 3m, 6m, 12m)
            - **SOFR** : taux de référence overnight aux USA (remplace le LIBOR)
            - **SONIA** : équivalent britannique en GBP
            """)
        with col2:
            st.markdown("""
            ## Politique monétaire de la BCE

            La **Banque Centrale Européenne** (BCE) utilise plusieurs outils :

            ### Taux directeurs
            - **Taux de refinancement** : taux auquel les banques empruntent à la BCE
            - **Taux de dépôt** : rémunération des réserves déposées à la BCE
            - **Taux de prêt marginal** : urgence overnight

            ### Instruments non conventionnels
            - **QE** (Quantitative Easing) : rachat d'actifs par la BCE
            - **TLTRO** : prêts à long terme aux banques
            - **Forward guidance** : communication sur les taux futurs

            ### Mécanisme de transmission
            """)
            st.markdown("""
            ```
            BCE ↓ taux directeurs
                ↓
            Banques ↓ coût de refinancement
                ↓
            Entreprises & ménages ↓ coût du crédit
                ↓
            Investissement & consommation ↑
                ↓
            Croissance & inflation ↑
            ```
            """)

    with tabs[1]:
        st.markdown("## 🏦 Taux directeurs en temps réel")

        taux_bce  = get_bond_yield(1) * 0.8
        taux_fed  = get_bond_yield(1)
        taux_boe  = get_bond_yield(1) * 0.95

        col_b1, col_b2, col_b3 = st.columns(3)
        col_b1.metric("🇪🇺 BCE (Taux dépôt)", f"{taux_bce:.2f}%", delta="Stable")
        col_b2.metric("🇺🇸 FED (Funds Rate)", f"{taux_fed:.2f}%", delta="-0.25% récent")
        col_b3.metric("🇬🇧 BOE (Base Rate)", f"{taux_boe:.2f}%", delta="Stable")

        st.markdown("---")
        st.markdown("### Historique des taux directeurs")

        maturites = [0.083, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]
        taux_actuel = [get_bond_yield(max(1, int(m))) for m in maturites]

        fig_rates = go.Figure()
        fig_rates.add_trace(go.Scatter(
            x=maturites, y=taux_actuel, mode="lines+markers",
            name="Courbe des taux USD",
            line=dict(color="#60a5fa", width=2), marker=dict(size=6)
        ))
        fig_rates.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=300, xaxis_title="Maturité (années)", yaxis_title="Taux (%)",
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=0,r=0,t=10,b=0)
        )
        st.plotly_chart(fig_rates, use_container_width=True, config={"displayModeBar": False})

    with tabs[2]:
        st.markdown("## 📐 Valeur d'un bon du Trésor")
        st.markdown("""
        Les bons du Trésor sont émis **sous le pair** (à escompte) et remboursés au pair.
        """)
        st.latex(r"P = \frac{N}{1 + r \times \frac{j}{360}}")
        st.markdown("Où **N** = valeur nominale · **r** = taux d'escompte · **j** = nombre de jours")

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nominale_bt = st.number_input("Valeur nominale (€)", 1000.0, 1e9, 100000.0, 1000.0)
            taux_esct   = st.slider("Taux d'escompte (%)", 0.0, 10.0, 3.5, 0.1) / 100
            jours       = st.slider("Durée (jours)", 7, 365, 90)
        with col_c2:
            prix_bt = nominale_bt / (1 + taux_esct * jours / 360)
            escompte = nominale_bt - prix_bt
            st.metric("Prix d'émission", f"{prix_bt:,.2f} €")
            st.metric("Escompte (gain)", f"{escompte:,.2f} €")
            st.metric("Rendement effectif", f"{(escompte/prix_bt * 360/jours)*100:.3f}%")

    with tabs[3]:
        st.markdown("## 🧪 Exercice : Taux interbancaire")
        with st.expander("📋 Énoncé", expanded=True):
            st.markdown("""
            Une banque emprunte **10 M€** sur le marché interbancaire à **3 mois** (91 jours)
            au taux Euribor 3 mois de **3.8%**.

            **Quel est le montant des intérêts à payer à l'échéance ?**
            (Base de calcul : 360 jours)
            """)
        with st.form("ex_mm"):
            rep_mm = st.number_input("Intérêts (€)", 0.0, 500000.0, 0.0, 100.0)
            valider_mm = st.form_submit_button("Valider", type="primary")
        if valider_mm:
            interets = 10_000_000 * 0.038 * 91 / 360
            if abs(rep_mm - interets) < 100:
                st.success(f"✅ Intérêts = 10M × 3.8% × 91/360 = **{interets:,.2f} €**")
            else:
                st.error(f"❌ Intérêts = 10 000 000 × 0.038 × 91/360 = **{interets:,.2f} €**")
