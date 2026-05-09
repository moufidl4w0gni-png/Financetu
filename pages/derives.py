"""Module Académique — Produits Dérivés"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.market_data import get_quote, get_history, black_scholes, ACTIONS_VEDETTES


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#7c3aed,#a855f7);'>🔄</div>
        <div>
            <p class='page-title'>Produits Dérivés</p>
            <p class='page-subtitle'>Options, futures, swaps et stratégies de couverture</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📖 Cours", "⚙️ Options — Black-Scholes", "📊 Profils de gain", "🔀 Futures & Swaps", "🧪 Exercices"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ## Qu'est-ce qu'un produit dérivé ?

            Un **produit dérivé** est un contrat financier dont la valeur dépend d'un **actif sous-jacent**
            (action, indice, taux, matière première, devise).

            ### Les 4 grandes familles
            | Produit | Définition |
            |---------|-----------|
            | **Option** | Droit (non obligation) d'acheter/vendre à un prix fixé |
            | **Future** | Obligation d'acheter/vendre à terme, sur marché organisé |
            | **Forward** | Idem future mais de gré à gré (OTC) |
            | **Swap** | Échange de flux financiers entre deux parties |

            ### Utilisations
            - **Couverture** (hedging) : se protéger contre un risque
            - **Spéculation** : parier sur l'évolution d'un actif avec effet de levier
            - **Arbitrage** : exploiter des différences de prix entre marchés
            """)
        with col2:
            st.markdown("""
            ## Les Options

            ### Call (option d'achat)
            - Donne le **droit d'acheter** l'actif au prix d'exercice K
            - L'acheteur paie une **prime** (premium)
            - Utile si on anticipe une **hausse**

            ### Put (option de vente)
            - Donne le **droit de vendre** l'actif au prix d'exercice K
            - L'acheteur paie une **prime**
            - Utile si on anticipe une **baisse**

            ### Les Greeks (sensibilités)
            | Greek | Mesure |
            |-------|--------|
            | **Delta (Δ)** | Sensibilité au prix du sous-jacent |
            | **Gamma (Γ)** | Variation du delta |
            | **Theta (Θ)** | Dépréciation temporelle |
            | **Vega (ν)** | Sensibilité à la volatilité |
            | **Rho (ρ)** | Sensibilité aux taux |
            """)

    with tabs[1]:
        st.markdown("## ⚙️ Calculateur Black-Scholes")
        st.latex(r"C = S \cdot N(d_1) - K e^{-rT} \cdot N(d_2)")
        st.latex(r"d_1 = \frac{\ln(S/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}} \quad;\quad d_2 = d_1 - \sigma\sqrt{T}")

        col_bs1, col_bs2 = st.columns(2)
        with col_bs1:
            st.markdown("#### Paramètres")
            S     = st.number_input("Prix du sous-jacent S (€)", 1.0, 10000.0, 100.0, 1.0)
            K     = st.number_input("Prix d'exercice K (€)", 1.0, 10000.0, 100.0, 1.0)
            T     = st.slider("Maturité T (en années)", 0.01, 5.0, 0.5, 0.01)
            r_bs  = st.slider("Taux sans risque r (%)", 0.0, 10.0, 3.0, 0.1) / 100
            sigma = st.slider("Volatilité implicite σ (%)", 1.0, 100.0, 20.0, 1.0) / 100
            opt_type = st.radio("Type d'option", ["call", "put"], horizontal=True)

        with col_bs2:
            st.markdown("#### Résultats")
            prix_option = black_scholes(S, K, T, r_bs, sigma, opt_type)
            d1 = (np.log(S/K) + (r_bs + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)

            from scipy.stats import norm
            if opt_type == "call":
                delta = norm.cdf(d1)
                theta = (-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) - r_bs*K*np.exp(-r_bs*T)*norm.cdf(d2)) / 365
            else:
                delta = norm.cdf(d1) - 1
                theta = (-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) + r_bs*K*np.exp(-r_bs*T)*norm.cdf(-d2)) / 365
            gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
            vega  = S*norm.pdf(d1)*np.sqrt(T) / 100

            st.metric("Prix de l'option", f"{prix_option:.4f} €")
            col_g1, col_g2 = st.columns(2)
            col_g1.metric("Delta (Δ)", f"{delta:.4f}")
            col_g2.metric("Gamma (Γ)", f"{gamma:.6f}")
            col_g1.metric("Theta (Θ)", f"{theta:.4f} €/jour")
            col_g2.metric("Vega (ν)", f"{vega:.4f} €/%vol")

            moneyness = "Dans la monnaie (ITM) ✅" if (opt_type=="call" and S>K) or (opt_type=="put" and S<K) else \
                        "Hors de la monnaie (OTM) ⚠️" if (opt_type=="call" and S<K) or (opt_type=="put" and S>K) else \
                        "À la monnaie (ATM) 🔵"
            st.info(f"**Moneyness :** {moneyness}")

        # Surface de volatilité
        strikes_range = np.linspace(S*0.7, S*1.3, 30)
        maturites_range = np.linspace(0.1, 2.0, 20)
        Z = np.array([[black_scholes(S, k, t, r_bs, sigma, opt_type)
                       for k in strikes_range] for t in maturites_range])
        fig_surf = go.Figure(go.Surface(
            z=Z, x=strikes_range, y=maturites_range,
            colorscale="Viridis", opacity=0.9
        ))
        fig_surf.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=350, title=f"Surface de prix — {opt_type.upper()}",
            scene=dict(
                xaxis_title="Strike (€)", yaxis_title="Maturité (ans)", zaxis_title="Prix (€)",
                bgcolor="#0f172a"
            ),
            margin=dict(l=0,r=0,t=40,b=0)
        )
        st.plotly_chart(fig_surf, use_container_width=True)

    with tabs[2]:
        st.markdown("## 📊 Profils de gain / perte à l'échéance")
        strategie = st.selectbox("Stratégie", [
            "Achat Call", "Vente Call", "Achat Put", "Vente Put",
            "Straddle (Call + Put)", "Bull Spread", "Bear Spread"
        ])
        S_strat = st.number_input("Prix du sous-jacent actuel (€)", 1.0, 5000.0, 100.0, 1.0, key="strat_S")
        K_strat = st.number_input("Prix d'exercice (€)", 1.0, 5000.0, 100.0, 1.0, key="strat_K")
        prime   = st.number_input("Prime payée (€)", 0.0, 100.0, 5.0, 0.1)

        prix_range = np.linspace(S_strat * 0.5, S_strat * 1.5, 200)

        if strategie == "Achat Call":
            gains = np.maximum(prix_range - K_strat, 0) - prime
            desc = "Profit illimité si hausse. Perte limitée à la prime."
        elif strategie == "Vente Call":
            gains = prime - np.maximum(prix_range - K_strat, 0)
            desc = "Gain limité à la prime. Perte illimitée si forte hausse."
        elif strategie == "Achat Put":
            gains = np.maximum(K_strat - prix_range, 0) - prime
            desc = "Profit si baisse. Perte limitée à la prime."
        elif strategie == "Vente Put":
            gains = prime - np.maximum(K_strat - prix_range, 0)
            desc = "Gain limité à la prime. Perte si forte baisse."
        elif strategie == "Straddle (Call + Put)":
            gains = np.maximum(prix_range - K_strat, 0) + np.maximum(K_strat - prix_range, 0) - 2*prime
            desc = "Profitable si forte variation dans un sens ou l'autre."
        elif strategie == "Bull Spread":
            K2 = K_strat * 1.1
            gains = np.maximum(prix_range - K_strat, 0) - np.maximum(prix_range - K2, 0) - prime
            desc = "Gain plafonné si hausse modérée. Risque limité."
        else:
            K2 = K_strat * 0.9
            gains = np.maximum(K_strat - prix_range, 0) - np.maximum(K2 - prix_range, 0) - prime
            desc = "Gain plafonné si baisse modérée. Risque limité."

        colors = ["#10b981" if g >= 0 else "#ef4444" for g in gains]
        fig_gain = go.Figure()
        fig_gain.add_trace(go.Scatter(
            x=prix_range, y=gains, mode="lines",
            line=dict(color="#60a5fa", width=2.5), fill="tozeroy",
            fillcolor="rgba(96,165,250,0.08)", name="Gain/Perte"
        ))
        fig_gain.add_hline(y=0, line_color="#475569", line_width=1)
        fig_gain.add_vline(x=K_strat, line_dash="dash", line_color="#f59e0b",
                           annotation_text=f"K={K_strat}€")
        fig_gain.update_layout(
            template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=320, xaxis_title="Prix sous-jacent à l'échéance (€)",
            yaxis_title="Gain / Perte (€)",
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
            margin=dict(l=0,r=0,t=10,b=0)
        )
        st.plotly_chart(fig_gain, use_container_width=True, config={"displayModeBar": False})
        st.info(f"📌 **{strategie}** : {desc}")

    with tabs[3]:
        st.markdown("## 🔀 Futures & Swaps")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("""
            ### Contrat Future
            - Obligation ferme d'acheter/vendre un actif à une **date future** et un **prix convenu**
            - Standardisé, négocié sur **marché organisé** (Eurex, CME...)
            - Règlement quotidien des gains/pertes (**marking to market**)
            - Nécessite un **dépôt de marge**

            **Prix d'un future (coût de portage) :**
            """)
            st.latex(r"F_0 = S_0 \cdot e^{(r-q)T}")
            st.markdown("Où **q** = rendement de dividende ou taux de commodité")

            st.markdown("### Calculateur de prix futur")
            S_fut = st.number_input("Prix spot S₀ (€)", 0.0, 100000.0, 100.0, 1.0)
            r_fut = st.slider("Taux sans risque (%)", 0.0, 10.0, 3.0, 0.1, key="r_fut") / 100
            q_fut = st.slider("Rendement dividende q (%)", 0.0, 10.0, 2.0, 0.1) / 100
            T_fut = st.slider("Maturité (mois)", 1, 24, 6) / 12
            F0    = S_fut * np.exp((r_fut - q_fut) * T_fut)
            st.metric("Prix futur théorique F₀", f"{F0:.2f} €")

        with col_f2:
            st.markdown("""
            ### Swap de taux d'intérêt (IRS)
            - Échange de **flux à taux fixe** contre **flux à taux variable**
            - Le plus répandu : **swap vanille** (fixed vs floating)
            - Utilisé pour gérer le risque de taux

            **Exemple :**
            - Entreprise A paie **taux fixe 3%** à B
            - Entreprise B paie **Euribor + 1%** à A
            - Si Euribor = 3% → B paie 4% → A reçoit net 1%

            ### Swap de devises (Cross-Currency Swap)
            Échange de flux dans **deux devises différentes**.
            Utilisé pour :
            - Financement en devise étrangère
            - Couverture du risque de change
            - Arbitrage de taux entre pays
            """)
            st.markdown("""
            <div class='fin-card' style='border-color:#a855f7'>
                <div class='fin-card-title'>⚡ Effet de levier des dérivés</div>
                <br>
                <div class='fin-card-desc'>
                    Un future sur CAC 40 vaut souvent <b>10€ × cours</b>.<br>
                    Si le CAC est à 7500 pts → valeur du contrat = <b>75 000 €</b><br>
                    Pour une marge de 3 750 € → levier de <b>20x</b><br><br>
                    ⚠️ L'effet de levier amplifie <b>aussi bien les gains que les pertes</b>.
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tabs[4]:
        st.markdown("## 🧪 Exercice : Payoff d'un Call")
        with st.expander("📋 Énoncé", expanded=True):
            st.markdown("""
            Vous achetez un **call** sur l'action BNP Paribas :
            - Prix d'exercice K = **60 €**
            - Prime payée = **3 €**
            - À l'échéance, le cours est de **68 €**

            **Quel est votre gain ou perte net ?**
            """)
        with st.form("ex_call"):
            rep_call = st.number_input("Gain / Perte (€)", -50.0, 100.0, 0.0, 0.5)
            valider_call = st.form_submit_button("Valider", type="primary")
        if valider_call:
            payoff = max(68 - 60, 0) - 3
            if abs(rep_call - payoff) < 0.1:
                st.success(f"✅ Correct ! Gain = max(68−60, 0) − 3 = 8 − 3 = **{payoff} €**")
            else:
                st.error(f"❌ Gain net = max(S−K,0) − prime = max(68−60,0) − 3 = **{payoff} €**")
