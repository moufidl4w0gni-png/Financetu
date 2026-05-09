"""Module Académique — Fonds d'Investissement"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from utils.market_data import get_history, calculer_sharpe, calculer_var


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#b45309,#f59e0b);'>🏦</div>
        <div>
            <p class='page-title'>Fonds d'Investissement</p>
            <p class='page-subtitle'>OPCVM, ETF, Private Equity et gestion d'actifs</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📖 Cours", "📊 Comparateur de fonds", "🧮 Simulateur portefeuille", "🧪 Exercices"])

    with tabs[0]:
        st.markdown("## Les fonds d'investissement")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            Un **fonds d'investissement** mutualise l'épargne de plusieurs investisseurs pour
            l'investir collectivement dans des actifs financiers sous la gestion d'un professionnel.

            ### Types de fonds (OPCVM)
            | Type | Caractéristiques |
            |------|-----------------|
            | **SICAV** | Société d'Investissement à Capital Variable, personnalité morale |
            | **FCP** | Fonds Commun de Placement, copropriété sans personnalité |
            | **ETF / Tracker** | Réplique un indice, coté en continu comme une action |
            | **FCPE** | Épargne salariale (Plan d'Épargne Entreprise) |
            | **FIA** | Fonds d'Investissement Alternatif (Hedge Fund, PE...) |

            ### Frais des fonds
            - **Frais d'entrée** : 0 à 5% à la souscription
            - **Frais de gestion** : 0.1% (ETF) à 3%/an (gestion active)
            - **Commission de performance** : % de la surperformance vs indice
            - **TER** (Total Expense Ratio) : coût total annuel
            """)
        with col2:
            st.markdown("""
            ### ETF (Exchange-Traded Funds)
            - Réplique fidèlement un indice (CAC 40, S&P 500, MSCI World...)
            - **Réplication physique** : achète les titres de l'indice
            - **Réplication synthétique** : utilise des swaps
            - Frais très bas : 0.05% à 0.35%/an
            - Liquidité intraday comme une action

            ### Gestion active vs passive
            """)
            data_comp = pd.DataFrame({
                "Critère": ["Frais", "Performance nette", "Transparence", "Liquidité"],
                "Gestion active": ["1–3%/an", "Variable", "Partielle", "Bonne"],
                "Gestion passive (ETF)": ["0.05–0.3%/an", "≈ Indice", "Totale", "Excellente"],
            })
            st.dataframe(data_comp, hide_index=True, use_container_width=True)

            st.markdown("""
            ### Private Equity
            Investissement dans des **entreprises non cotées** :
            - **Venture Capital** : startups en phase de démarrage
            - **Growth Equity** : entreprises en croissance
            - **LBO** (Leveraged Buy-Out) : rachat avec effet de levier
            - **TRI** cible : 15% à 25%/an · Horizon 5–10 ans
            """)

    with tabs[1]:
        st.markdown("## 📊 Simulation de fonds")
        st.info("Simulation basée sur les indices réels via Yahoo Finance")

        FONDS_SIMULES = {
            "CAC 40 (Euronext)": "^FCHI",
            "S&P 500 (USA)": "^GSPC",
            "NASDAQ 100": "^IXIC",
            "Euro Stoxx 50": "^STOXX50E",
            "MSCI World (approx.)": "^GSPC",
        }

        fonds_selec = st.multiselect(
            "Sélectionnez les fonds à comparer",
            list(FONDS_SIMULES.keys()),
            default=["CAC 40 (Euronext)", "S&P 500 (USA)"]
        )
        periode_f = st.selectbox("Période", ["1 mois", "3 mois", "6 mois", "1 an"], index=3)
        periode_map = {"1 mois": "1mo", "3 mois": "3mo", "6 mois": "6mo", "1 an": "1y"}

        if fonds_selec:
            fig_perf = go.Figure()
            stats_rows = []
            colors = ["#60a5fa", "#10b981", "#f59e0b", "#a855f7", "#ef4444"]

            for i, fond in enumerate(fonds_selec):
                ticker = FONDS_SIMULES[fond]
                hist   = get_history(ticker, period=periode_map[periode_f])
                if not hist.empty:
                    perf_cum = (hist["Close"] / hist["Close"].iloc[0] - 1) * 100
                    returns  = hist["Close"].pct_change().dropna()
                    fig_perf.add_trace(go.Scatter(
                        x=hist.index, y=perf_cum,
                        name=fond, mode="lines",
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))
                    stats_rows.append({
                        "Fonds": fond,
                        "Performance": f"{perf_cum.iloc[-1]:+.1f}%",
                        "Volatilité": f"{returns.std()*np.sqrt(252)*100:.1f}%",
                        "Sharpe": f"{calculer_sharpe(returns):.2f}",
                        "VaR 95%": f"{calculer_var(returns)*100:.2f}%",
                        "Max Drawdown": f"{((hist['Close']/hist['Close'].cummax())-1).min()*100:.1f}%",
                    })

            fig_perf.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                height=350, yaxis_title="Performance (%)", xaxis_title="",
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
                margin=dict(l=0,r=0,t=10,b=0)
            )
            st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

            if stats_rows:
                st.dataframe(pd.DataFrame(stats_rows), hide_index=True, use_container_width=True)

    with tabs[2]:
        st.markdown("## 🧮 Simulateur de portefeuille")

        ACTIFS_PORTEF = {
            "Actions françaises (CAC 40)": "^FCHI",
            "Actions américaines (S&P 500)": "^GSPC",
            "Technologie (NASDAQ)": "^IXIC",
        }

        st.markdown("### Définissez votre allocation")
        poids = {}
        cols_p = st.columns(len(ACTIFS_PORTEF))
        for col, (nom, _) in zip(cols_p, ACTIFS_PORTEF.items()):
            with col:
                poids[nom] = st.slider(nom.split("(")[0].strip(), 0, 100, 33, 5, key=f"p_{nom}")

        total_poids = sum(poids.values())
        if total_poids != 100:
            st.warning(f"⚠️ La somme des poids = {total_poids}% (doit être 100%)")
        else:
            rendements_all = {}
            for nom, ticker in ACTIFS_PORTEF.items():
                hist = get_history(ticker, period="1y")
                if not hist.empty:
                    rendements_all[nom] = hist["Close"].pct_change().dropna()

            if rendements_all:
                df_ret = pd.DataFrame(rendements_all).dropna()
                portef_ret = sum(df_ret[nom] * (poids[nom]/100) for nom in df_ret.columns if nom in poids)
                perf_cum   = (1 + portef_ret).cumprod() - 1

                fig_port = go.Figure()
                fig_port.add_trace(go.Scatter(
                    x=perf_cum.index, y=perf_cum*100,
                    fill="tozeroy", mode="lines",
                    line=dict(color="#60a5fa", width=2),
                    fillcolor="rgba(96,165,250,0.08)"
                ))
                fig_port.update_layout(
                    template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                    height=280, yaxis_title="Performance cumulée (%)",
                    xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
                    margin=dict(l=0,r=0,t=10,b=0), title="Performance du portefeuille (1 an)"
                )
                st.plotly_chart(fig_port, use_container_width=True, config={"displayModeBar": False})

                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Rendement annualisé", f"{portef_ret.mean()*252*100:+.1f}%")
                c2.metric("Volatilité annualisée", f"{portef_ret.std()*np.sqrt(252)*100:.1f}%")
                c3.metric("Ratio de Sharpe", f"{calculer_sharpe(portef_ret):.2f}")
                c4.metric("VaR 95% (jour)", f"{calculer_var(portef_ret)*100:.2f}%")

                # Camembert allocation
                fig_pie = px.pie(
                    values=list(poids.values()),
                    names=list(poids.keys()),
                    color_discrete_sequence=["#60a5fa","#10b981","#f59e0b","#a855f7","#ef4444"]
                )
                fig_pie.update_layout(
                    template="plotly_dark", paper_bgcolor="#0f172a",
                    height=250, margin=dict(l=0,r=0,t=10,b=0),
                    showlegend=True, legend=dict(font=dict(size=11))
                )
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with tabs[3]:
        st.markdown("## 🧪 Exercice : VL d'un OPCVM")
        with st.expander("📋 Énoncé", expanded=True):
            st.markdown("""
            Un fonds détient :
            - 500 actions à **80 €**
            - 200 obligations à **950 €**
            - Trésorerie : **10 000 €**
            - Frais à payer : **5 000 €**
            - Nombre de parts : **1 000**

            **Calculez la Valeur Liquidative (VL) par part.**
            """)
        with st.form("ex_vl"):
            rep_vl = st.number_input("VL par part (€)", 0.0, 10000.0, 0.0, 0.5)
            valider_vl = st.form_submit_button("Valider", type="primary")
        if valider_vl:
            actif = 500*80 + 200*950 + 10000 - 5000
            vl = actif / 1000
            if abs(rep_vl - vl) < 1:
                st.success(f"✅ VL = (500×80 + 200×950 + 10000 − 5000) / 1000 = **{vl:.2f} €/part**")
            else:
                st.error(f"❌ VL = Actif Net / Nb parts = {actif:,.0f} / 1000 = **{vl:.2f} €/part**")
