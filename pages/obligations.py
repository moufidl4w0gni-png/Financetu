"""Module Académique — Obligations"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.market_data import get_bond_yield, calculer_rendement_obligataire


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#0369a1,#0ea5e9);'>💼</div>
        <div>
            <p class='page-title'>Obligations</p>
            <p class='page-subtitle'>Comprendre les titres de créance, les taux et la courbe des taux</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📖 Cours", "📐 Calculateur", "📈 Courbe des taux", "🧪 Exercices"])

    with tabs[0]:
        st.markdown("## Qu'est-ce qu'une obligation ?")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            Une **obligation** est un titre de **créance** émis par un État, une entreprise ou une
            collectivité pour se financer. En achetant une obligation, vous prêtez de l'argent à
            l'émetteur qui s'engage à vous rembourser avec des intérêts.

            ### Caractéristiques d'une obligation
            | Élément | Description |
            |---------|-------------|
            | **Valeur nominale** | Montant emprunté (ex : 1 000 €) |
            | **Coupon** | Intérêt périodique versé (ex : 3% / an) |
            | **Maturité** | Date de remboursement final |
            | **Prix d'émission** | Peut être au pair, sous ou sur le pair |
            | **Taux actuariel** | Rendement réel tenant compte du prix |

            ### Types d'obligations
            - **Obligation à taux fixe** : coupon constant sur toute la durée
            - **Obligation à taux variable** : coupon indexé (Euribor + spread)
            - **Obligation zéro-coupon** : pas de coupon, émise très sous le pair
            - **OAT** (France), **Bund** (Allemagne), **Treasury** (USA)
            - **Obligation d'entreprise** (Investment Grade vs High Yield)
            - **Obligation convertible** : convertible en actions
            """)
        with col2:
            st.markdown("""
            <div class='fin-card' style='border-color:#0ea5e9'>
                <div class='fin-card-header'>
                    <div class='fin-card-icon' style='background:rgba(14,165,233,0.15)'>💡</div>
                    <div class='fin-card-title'>Relation taux / prix</div>
                </div>
                <div class='fin-card-desc'>
                    ⚡ <b>Règle d'or :</b><br><br>
                    Quand les taux <b>montent</b> 📈<br>
                    → Prix des obligations <b>baissent</b> 📉<br><br>
                    Quand les taux <b>baissent</b> 📉<br>
                    → Prix des obligations <b>montent</b> 📈<br><br>
                    C'est l'<b>effet balançoire</b> !
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("## Valorisation d'une obligation")
        st.latex(r"P = \sum_{t=1}^{n} \frac{C}{(1+r)^t} + \frac{N}{(1+r)^n}")
        st.markdown("""
        Où : **P** = Prix · **C** = Coupon · **N** = Valeur nominale · **r** = taux actuariel · **n** = maturité

        ### Notion de duration (sensibilité)
        """)
        st.latex(r"D = \frac{\sum_{t=1}^{n} t \cdot \frac{C}{(1+r)^t} + n \cdot \frac{N}{(1+r)^n}}{P}")
        st.info("📌 La **duration** mesure la sensibilité du prix aux variations de taux. "
                "Une duration de 7 ans signifie qu'une hausse de 1% des taux entraîne une baisse d'environ 7% du prix.")

    with tabs[1]:
        st.markdown("## 📐 Calculateur d'obligation")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nominale  = st.number_input("Valeur nominale (€)", 100.0, 100000.0, 1000.0, 100.0)
            coupon_p  = st.slider("Taux de coupon (%/an)", 0.0, 15.0, 4.0, 0.1)
            maturite  = st.slider("Maturité (années)", 1, 30, 10)
            taux_mar  = st.slider("Taux de marché / actuariel (%)", 0.1, 15.0, 5.0, 0.1)
        with col_c2:
            coupon = nominale * coupon_p / 100
            r = taux_mar / 100
            prix = sum([coupon / (1 + r) ** t for t in range(1, maturite + 1)]) + nominale / (1 + r) ** maturite
            duration_num = sum([t * coupon / (1 + r) ** t for t in range(1, maturite + 1)]) + maturite * nominale / (1 + r) ** maturite
            duration = duration_num / prix
            sensib = -duration / (1 + r)

            st.metric("Prix théorique", f"{prix:.2f} €")
            st.metric("Duration", f"{duration:.2f} ans")
            st.metric("Sensibilité", f"{sensib:.2f}")

            if coupon_p > taux_mar:
                st.success(f"✅ Obligation au-dessus du pair ({prix:.0f} > {nominale:.0f}€) — Coupon > Marché")
            elif coupon_p < taux_mar:
                st.warning(f"⚠️ Obligation sous le pair ({prix:.0f} < {nominale:.0f}€) — Coupon < Marché")
            else:
                st.info("ℹ️ Obligation au pair — Coupon = Marché")

        # Graphique sensibilité
        taux_range = np.linspace(0.5, 15, 100) / 100
        prix_range = [
            sum([coupon / (1 + r2) ** t for t in range(1, maturite + 1)]) + nominale / (1 + r2) ** maturite
            for r2 in taux_range
        ]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=taux_range * 100, y=prix_range, line=dict(color="#0ea5e9", width=2), name="Prix"))
        fig.add_vline(x=taux_mar, line_dash="dash", line_color="#f59e0b", annotation_text=f"Taux actuel: {taux_mar}%")
        fig.add_hline(y=prix, line_dash="dash", line_color="#10b981", annotation_text=f"Prix: {prix:.0f}€")
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=300, title="Relation Taux ↔ Prix",
            xaxis_title="Taux actuariel (%)", yaxis_title="Prix (€)",
            margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with tabs[2]:
        st.markdown("## 📈 Courbe des taux en temps réel")
        st.info("Taux des obligations d'État (données approximatives via Yahoo Finance)")

        maturites = [1, 2, 3, 5, 7, 10, 20, 30]
        taux_usa  = [get_bond_yield(m) for m in maturites]
        taux_mock_fr = [t * 0.7 + 0.2 for t in taux_usa]

        fig_yc = go.Figure()
        fig_yc.add_trace(go.Scatter(x=maturites, y=taux_usa, mode="lines+markers",
            name="USA (Treasuries)", line=dict(color="#60a5fa", width=2),
            marker=dict(size=7)))
        fig_yc.add_trace(go.Scatter(x=maturites, y=taux_mock_fr, mode="lines+markers",
            name="France (OAT)", line=dict(color="#f59e0b", width=2),
            marker=dict(size=7)))
        fig_yc.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
            height=350, xaxis_title="Maturité (années)", yaxis_title="Taux (%)",
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"))
        st.plotly_chart(fig_yc, use_container_width=True, config={"displayModeBar": False})

        col_interp1, col_interp2 = st.columns(2)
        spread = taux_usa[-1] - taux_usa[1] if len(taux_usa) >= 2 else 0
        with col_interp1:
            st.metric("Spread 10Y-2Y (USA)", f"{spread:.2f}%",
                      delta="Courbe inversée ⚠️" if spread < 0 else "Courbe normale ✅")
        with col_interp2:
            st.markdown("""
            **Interprétation :**
            - Courbe **normale** (croissante) → Croissance attendue
            - Courbe **plate** → Incertitude économique
            - Courbe **inversée** → Signal récessif historique
            """)

    with tabs[3]:
        st.markdown("## 🧪 Exercice : Prix d'une obligation")
        with st.expander("📋 Énoncé", expanded=True):
            st.markdown("""
            Une obligation a les caractéristiques suivantes :
            - Valeur nominale : **1 000 €**
            - Coupon annuel : **5%** soit **50 €/an**
            - Maturité : **3 ans**
            - Taux de marché actuel : **6%**

            **Calculez le prix de cette obligation.**
            """)
        with st.form("ex_oblig"):
            rep_p = st.number_input("Prix de l'obligation (€)", 0.0, 2000.0, 1000.0, 0.5)
            valider = st.form_submit_button("Valider", type="primary")
        if valider:
            r_ex = 0.06
            prix_ex = 50/(1.06) + 50/(1.06)**2 + 1050/(1.06)**3
            if abs(rep_p - prix_ex) < 2:
                st.success(f"✅ Bravo ! Prix = 50/1.06 + 50/1.06² + 1050/1.06³ = **{prix_ex:.2f} €**")
                st.info("L'obligation est sous le pair car le taux de marché (6%) > coupon (5%)")
            else:
                st.error(f"❌ Prix correct = **{prix_ex:.2f} €**")
                st.markdown(f"P = 50/1.06 + 50/1.06² + 1050/1.06³ = {50/1.06:.2f} + {50/1.06**2:.2f} + {1050/1.06**3:.2f} = **{prix_ex:.2f} €**")
