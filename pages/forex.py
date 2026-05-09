"""Module Académique — Forex & Crypto"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.market_data import get_quote, get_history, FOREX_PAIRS, CRYPTOS


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#0f766e,#14b8a6);'>💱</div>
        <div>
            <p class='page-title'>Forex & Cryptomonnaies</p>
            <p class='page-subtitle'>Marchés des changes, parités et actifs numériques</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📖 Forex", "💹 Taux de change en direct", "₿ Crypto", "🧪 Exercices"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ## Le marché des changes (Forex)

            Le **Forex** (Foreign Exchange) est le marché sur lequel s'échangent les devises mondiales.
            C'est le **plus grand marché financier au monde** : plus de **7 500 milliards $ / jour**.

            ### Caractéristiques
            - Marché **OTC** (de gré à gré), ouvert 24h/24, 5j/7
            - Acteurs : banques centrales, banques commerciales, hedge funds, entreprises, particuliers
            - Cotation en **paires** : EUR/USD, GBP/JPY...
            - Très forte **liquidité**, spreads très faibles pour les paires majeures

            ### Structure d'une cotation
            **EUR/USD = 1.0850**
            - EUR = devise de **base** (1 unité)
            - USD = devise de **cotation** (prix en $)
            - 1 EUR s'échange contre 1.0850 USD

            ### Types de paires
            | Catégorie | Exemples |
            |-----------|----------|
            | **Majeures** | EUR/USD, GBP/USD, USD/JPY |
            | **Mineures** | EUR/GBP, EUR/CHF, AUD/NZD |
            | **Exotiques** | USD/TRY, EUR/PLN, USD/ZAR |
            """)
        with col2:
            st.markdown("""
            ## Déterminants des taux de change

            ### Facteurs fondamentaux
            - **Différentiel de taux d'intérêt** : taux élevé → monnaie forte
            - **Inflation** : inflation élevée → dépréciation
            - **Balance commerciale** : excédent → appréciation
            - **Croissance économique** : PIB élevé → attractivité

            ### Théories majeures
            """)
            st.latex(r"\text{PPA : } S = \frac{P_{domestique}}{P_{étranger}}")
            st.latex(r"\text{Parité couverte : } F = S \cdot \frac{(1+r_d)}{(1+r_f)}")
            st.markdown("""
            - **PPA** (Parité des Pouvoirs d'Achat) : égalisation des prix par le taux de change
            - **Parité des taux d'intérêt** : différentiel de taux reflété dans le cours à terme

            ### Le pip
            Le **pip** (Price Interest Point) est la plus petite variation de cours.
            - EUR/USD : 1 pip = 0.0001
            - USD/JPY : 1 pip = 0.01

            **Valeur d'un pip** = (pip / cours) × taille du lot
            """)

    with tabs[1]:
        st.markdown("## 💹 Taux de change en temps réel")
        col_m = st.columns(len(FOREX_PAIRS))
        for col, (pair, ticker) in zip(col_m, FOREX_PAIRS.items()):
            q = get_quote(ticker)
            with col:
                st.metric(pair, f"{q['price']:.4f}", f"{q['pct']:+.3f}%")

        st.markdown("---")
        pair_sel = st.selectbox("Paire à analyser", list(FOREX_PAIRS.keys()))
        periode_fx = st.selectbox("Période", ["1 semaine","1 mois","3 mois","6 mois","1 an"], index=2, key="fx_per")
        periode_map = {"1 semaine":"5d","1 mois":"1mo","3 mois":"3mo","6 mois":"6mo","1 an":"1y"}

        hist_fx = get_history(FOREX_PAIRS[pair_sel], period=periode_map[periode_fx])
        if not hist_fx.empty:
            color_fx = "#10b981" if hist_fx["Close"].iloc[-1] >= hist_fx["Close"].iloc[0] else "#ef4444"
            fig_fx = go.Figure()
            fig_fx.add_trace(go.Scatter(
                x=hist_fx.index, y=hist_fx["Close"],
                mode="lines", line=dict(color=color_fx, width=2),
                fill="tozeroy", fillcolor=f"rgba({'16,185,129' if color_fx=='#10b981' else '239,68,68'},0.08)",
                name=pair_sel
            ))
            fig_fx.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                height=300, xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
                margin=dict(l=0,r=0,t=10,b=0)
            )
            st.plotly_chart(fig_fx, use_container_width=True, config={"displayModeBar": False})

        st.markdown("---")
        st.markdown("### 🧮 Convertisseur de devises")
        col_conv1, col_conv2, col_conv3 = st.columns(3)
        with col_conv1:
            montant = st.number_input("Montant", 0.0, 1e9, 1000.0, 1.0)
        with col_conv2:
            from_curr = st.selectbox("De", ["EUR","USD","GBP","JPY","CHF"], index=0)
        with col_conv3:
            to_curr = st.selectbox("Vers", ["USD","EUR","GBP","JPY","CHF"], index=0)

        if from_curr != to_curr:
            pair_conv = f"{from_curr}{to_curr}=X"
            q_conv = get_quote(pair_conv)
            result = montant * q_conv["price"]
            st.success(f"**{montant:,.2f} {from_curr}** = **{result:,.4f} {to_curr}** "
                       f"(taux : {q_conv['price']:.4f})")

    with tabs[2]:
        st.markdown("## ₿ Cryptomonnaies")
        col_cr = st.columns(len(CRYPTOS))
        for col, (name, ticker) in zip(col_cr, CRYPTOS.items()):
            q = get_quote(ticker)
            with col:
                st.metric(name, f"${q['price']:,.0f}", f"{q['pct']:+.2f}%")

        crypto_sel = st.selectbox("Crypto à analyser", list(CRYPTOS.keys()))
        hist_cr = get_history(CRYPTOS[crypto_sel], period="1y")

        if not hist_cr.empty:
            fig_cr = go.Figure(go.Candlestick(
                x=hist_cr.index,
                open=hist_cr["Open"], high=hist_cr["High"],
                low=hist_cr["Low"],   close=hist_cr["Close"],
                increasing_line_color="#10b981",
                decreasing_line_color="#ef4444",
            ))
            fig_cr.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                height=320, title=f"{crypto_sel} — 1 an (USD)",
                xaxis=dict(gridcolor="#1e293b", rangeslider=dict(visible=False)),
                yaxis=dict(gridcolor="#1e293b"),
                margin=dict(l=0,r=0,t=30,b=0)
            )
            st.plotly_chart(fig_cr, use_container_width=True, config={"displayModeBar": False})

        with st.expander("📚 Les fondamentaux des cryptos"):
            st.markdown("""
            ### Blockchain et décentralisation
            - **Blockchain** : registre distribué, immuable, transparent
            - **Consensus** : Proof of Work (Bitcoin) vs Proof of Stake (Ethereum)
            - **DeFi** : Finance décentralisée, protocoles sans intermédiaire
            - **NFT** : Tokens non fongibles, preuve de propriété numérique

            ### Risques spécifiques aux cryptos
            - Très haute **volatilité** (Bitcoin peut varier de ±20% en une journée)
            - Risque **réglementaire** : évolution de la législation
            - Risque **technologique** : bugs, hacks de protocoles
            - Risque de **liquidité** : pour les altcoins mineurs
            - **Pas de valeur intrinsèque** garantie comme les actifs traditionnels
            """)

    with tabs[3]:
        st.markdown("## 🧪 Exercice : Arbitrage de change")
        with st.expander("📋 Énoncé", expanded=True):
            st.markdown("""
            Les taux suivants sont cotés :
            - EUR/USD = **1.10**
            - EUR/GBP = **0.86**
            - GBP/USD = **1.30**

            **Y a-t-il une opportunité d'arbitrage triangulaire ?**

            Partez de **1 000 €** : convertissez en £, puis en $, puis revenez en €.
            """)
        with st.form("ex_arb"):
            rep_arb = st.radio("Y a-t-il un arbitrage ?", ["Oui, gain possible", "Non, pas d'arbitrage"])
            rep_gain = st.number_input("Si oui, gain pour 1 000 € de départ (€)", 0.0, 1000.0, 0.0, 0.1)
            valider_arb = st.form_submit_button("Valider", type="primary")
        if valider_arb:
            livres = 1000 * 0.86
            dollars = livres * 1.30
            retour = dollars / 1.10
            gain = retour - 1000
            if rep_arb == "Oui, gain possible" and abs(rep_gain - gain) < 2:
                st.success(f"✅ Bravo ! 1000€ → {livres:.2f}£ → {dollars:.2f}$ → {retour:.2f}€ — Gain = **{gain:.2f}€**")
            else:
                st.error(f"❌ Il y a un arbitrage de {gain:.2f}€ pour 1000€ de départ.\n"
                         f"1000€ × 0.86 = {livres:.2f}£ × 1.30 = {dollars:.2f}$ / 1.10 = {retour:.2f}€")
