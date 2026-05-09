"""Module Académique — Actions & Marchés Actions"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.market_data import (
    get_quote, get_history, get_info, get_multiple_quotes,
    ACTIONS_VEDETTES, calculer_var, calculer_sharpe, format_price
)


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#059669,#10b981);'>📊</div>
        <div>
            <p class='page-title'>Actions & Marchés financiers</p>
            <p class='page-subtitle'>Comprendre les actions, la valorisation et l'analyse boursière</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "📖 Cours", "📈 Analyse en direct", "🔢 Valorisation",
        "⚖️ Risque & Performance", "🧪 Exercices"
    ])

    # ════════════════════════════════════════════════════════
    # ONGLET 1 — COURS THÉORIQUE
    # ════════════════════════════════════════════════════════
    with tabs[0]:
        st.markdown("## Qu'est-ce qu'une action ?")
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            Une **action** (ou *share* en anglais) est un **titre de propriété** représentant une fraction
            du capital d'une société. En achetant une action, vous devenez **actionnaire**, c'est-à-dire
            copropriétaire de l'entreprise.

            ### Droits de l'actionnaire
            - **Droit au dividende** : participation aux bénéfices distribués
            - **Droit de vote** : participation aux Assemblées Générales
            - **Droit à l'information** : accès aux comptes et rapports annuels
            - **Droit préférentiel de souscription** : priorité lors d'augmentations de capital
            - **Boni de liquidation** : part de l'actif en cas de dissolution (dernier rang)

            ### Types d'actions
            | Type | Description |
            |------|-------------|
            | **Action ordinaire** | Droits standards (vote + dividende) |
            | **Action à droit de vote double** | Fidélité récompensée (≥ 2 ans) |
            | **Action de préférence** | Dividende prioritaire, vote limité |
            | **Action sans droit de vote** | Dividende majoré, pas de vote |
            """)

        with col2:
            st.markdown("""
            <div class='fin-card' style='border-color:#10b981'>
                <div class='fin-card-header'>
                    <div class='fin-card-icon' style='background:rgba(16,185,129,0.15)'>💡</div>
                    <div class='fin-card-title'>Points clés</div>
                </div>
                <div class='fin-card-desc'>
                    <b>Rendement total =</b><br>
                    Plus-value + Dividende<br><br>
                    <b>Rendement =</b><br>
                    (P₁ − P₀ + D) / P₀<br><br>
                    <b>Capitalisation =</b><br>
                    Nb actions × Cours
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.info("📌 **À retenir** : Une action ne garantit aucun rendement. C'est un actif risqué dont la valeur fluctue selon les marchés.")

        st.divider()
        st.markdown("## Les marchés actions")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""
            **🏪 Marché primaire**
            - Émission de nouvelles actions
            - Introduction en Bourse (IPO)
            - Augmentation de capital
            - L'entreprise reçoit les fonds
            """)
        with col_b:
            st.markdown("""
            **🔄 Marché secondaire**
            - Échange d'actions existantes
            - Euronext, NYSE, LSE...
            - Fixation du prix par l'offre/demande
            - L'entreprise ne reçoit pas les fonds
            """)
        with col_c:
            st.markdown("""
            **⚡ Marchés dérivés actions**
            - Options sur actions
            - Futures sur indices
            - ETF (trackers)
            - Warrants, turbos
            """)

        st.divider()
        st.markdown("## Comment se forme le prix d'une action ?")
        st.markdown("""
        Le cours d'une action est déterminé par la **confrontation des ordres d'achat et de vente**
        sur le carnet d'ordres (*order book*).

        **Facteurs influençant le cours :**
        - Résultats financiers (bénéfices, chiffre d'affaires)
        - Perspectives de croissance et guidances
        - Dividendes versés
        - Taux d'intérêt (effet d'actualisation)
        - Sentiment de marché et psychologie des investisseurs
        - Événements macroéconomiques (inflation, récession)
        - Événements spécifiques (fusions-acquisitions, scandales)
        """)
        with st.expander("📐 Formule du modèle de Gordon-Shapiro (dividendes constants)"):
            st.latex(r"P_0 = \frac{D_1}{r - g}")
            st.markdown("""
            Où :
            - **P₀** = Prix actuel de l'action
            - **D₁** = Dividende attendu l'an prochain
            - **r** = Taux de rendement exigé par l'actionnaire
            - **g** = Taux de croissance perpétuel des dividendes
            """)

    # ════════════════════════════════════════════════════════
    # ONGLET 2 — ANALYSE EN DIRECT
    # ════════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown("## 📈 Analyse d'actions en temps réel")

        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            action_choisie = st.selectbox("Choisissez une action", list(ACTIONS_VEDETTES.keys()))
        with col_s2:
            periode = st.selectbox("Période d'analyse", ["1 semaine", "1 mois", "3 mois", "6 mois", "1 an"])
        with col_s3:
            st.markdown("<br>", unsafe_allow_html=True)
            rafraichir = st.button("🔄 Actualiser", use_container_width=True)

        ticker = ACTIONS_VEDETTES[action_choisie]
        quote  = get_quote(ticker)
        info   = get_info(ticker)
        periode_map = {"1 semaine":"5d","1 mois":"1mo","3 mois":"3mo","6 mois":"6mo","1 an":"1y"}
        hist   = get_history(ticker, period=periode_map[periode])

        # Métriques principales
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Cours actuel", f"{quote['price']:.2f} €", f"{quote['pct']:+.2f}%")
        col_m2.metric("Variation jour", f"{quote['change']:+.2f} €")
        col_m3.metric("Cours veille", f"{quote['prev']:.2f} €")
        if info.get("market_cap"):
            col_m4.metric("Capitalisation", format_price(info["market_cap"]))
        else:
            col_m4.metric("Mise à jour", quote["updated"])

        # Graphique principal avec moyennes mobiles
        if not hist.empty:
            fig = go.Figure()
            color = "#10b981" if quote["pct"] >= 0 else "#ef4444"

            # Prix
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"],
                name="Cours",
                line=dict(color=color, width=2),
            ))

            # Moyennes mobiles
            if len(hist) >= 20:
                mm20 = hist["Close"].rolling(20).mean()
                fig.add_trace(go.Scatter(x=hist.index, y=mm20, name="MM20", line=dict(color="#60a5fa", width=1, dash="dot")))
            if len(hist) >= 50:
                mm50 = hist["Close"].rolling(50).mean()
                fig.add_trace(go.Scatter(x=hist.index, y=mm50, name="MM50", line=dict(color="#f59e0b", width=1, dash="dot")))

            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                height=350, margin=dict(l=0,r=0,t=10,b=0),
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
                xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Volume
            fig_vol = go.Figure(go.Bar(
                x=hist.index, y=hist["Volume"],
                marker_color=[color if c >= o else "#ef4444" for c, o in zip(hist["Close"], hist["Open"])],
                name="Volume",
            ))
            fig_vol.update_layout(
                template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                height=120, margin=dict(l=0,r=0,t=5,b=0),
                xaxis=dict(gridcolor="#1e293b", showticklabels=False),
                yaxis=dict(gridcolor="#1e293b"),
                showlegend=False,
            )
            st.plotly_chart(fig_vol, use_container_width=True, config={"displayModeBar": False})

        # Fondamentaux
        if info:
            st.markdown("#### 📋 Données fondamentales")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("PER (P/E)", f"{info.get('pe_ratio', 'N/A')}" if info.get("pe_ratio") else "N/A")
            c2.metric("Dividende", f"{info.get('dividend', 0)*100:.1f}%" if info.get("dividend") else "N/A")
            c3.metric("Beta", f"{info.get('beta', 'N/A')}" if info.get("beta") else "N/A")
            c4.metric("Secteur", info.get("sector", "N/A"))

    # ════════════════════════════════════════════════════════
    # ONGLET 3 — VALORISATION
    # ════════════════════════════════════════════════════════
    with tabs[2]:
        st.markdown("## 🔢 Méthodes de valorisation")

        methode = st.radio("Méthode", [
            "Modèle de Gordon-Shapiro (DDM)",
            "Price-Earnings Ratio (PER)",
            "Valeur d'entreprise (EV/EBITDA)"
        ], horizontal=True)

        if methode == "Modèle de Gordon-Shapiro (DDM)":
            st.markdown("### Dividende Discount Model (DDM)")
            st.latex(r"P_0 = \frac{D_1}{r - g} = \frac{D_0 \times (1+g)}{r - g}")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                d0  = st.number_input("Dernier dividende versé D₀ (€)", 0.0, 100.0, 3.0, 0.1)
                g   = st.slider("Taux de croissance g (%)", 0.0, 10.0, 3.0, 0.1) / 100
                r   = st.slider("Taux de rendement exigé r (%)", 1.0, 20.0, 8.0, 0.1) / 100
            with col_v2:
                if r <= g:
                    st.error("⚠️ Le taux r doit être supérieur à g pour que le modèle soit valide.")
                else:
                    d1 = d0 * (1 + g)
                    p0 = d1 / (r - g)
                    st.metric("D₁ (prochain dividende)", f"{d1:.2f} €")
                    st.metric("Prix théorique P₀", f"{p0:.2f} €")
                    st.markdown(f"""
                    **Interprétation :**
                    - Si le cours actuel est **inférieur** à {p0:.2f} € → action **sous-évaluée** ✅
                    - Si le cours actuel est **supérieur** à {p0:.2f} € → action **surévaluée** ⚠️
                    """)

        elif methode == "Price-Earnings Ratio (PER)":
            st.markdown("### Price-Earnings Ratio")
            st.latex(r"PER = \frac{Cours}{BPA} \quad \Leftrightarrow \quad Valeur = BPA \times PER_{sectoriel}")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                bpa       = st.number_input("Bénéfice Par Action (BPA) prévu (€)", 0.1, 50.0, 5.0, 0.1)
                per_sect  = st.number_input("PER sectoriel de référence", 5.0, 50.0, 15.0, 0.5)
                cours_act = st.number_input("Cours actuel (€)", 1.0, 5000.0, 75.0, 1.0)
            with col_v2:
                valeur_per = bpa * per_sect
                per_act    = cours_act / bpa
                st.metric("Valeur théorique", f"{valeur_per:.2f} €")
                st.metric("PER actuel de l'action", f"{per_act:.1f}x")
                st.metric("PER sectoriel", f"{per_sect:.1f}x")
                ecart = (cours_act / valeur_per - 1) * 100
                if ecart > 10:
                    st.warning(f"⚠️ Action surévaluée de {ecart:.1f}% vs le secteur")
                elif ecart < -10:
                    st.success(f"✅ Action sous-évaluée de {abs(ecart):.1f}% vs le secteur")
                else:
                    st.info(f"ℹ️ Action correctement valorisée ({ecart:+.1f}%)")

        else:
            st.markdown("### Valeur d'entreprise (EV/EBITDA)")
            st.latex(r"EV = \text{Capitalisation} + \text{Dette nette} \quad;\quad EV/EBITDA = \frac{EV}{EBITDA}")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                capi    = st.number_input("Capitalisation boursière (M€)", 0.0, 1e6, 5000.0, 100.0)
                dette   = st.number_input("Dette nette (M€)", 0.0, 1e5, 1000.0, 100.0)
                ebitda  = st.number_input("EBITDA (M€)", 0.1, 1e5, 800.0, 10.0)
                ev_sect = st.number_input("Multiple EV/EBITDA sectoriel", 1.0, 50.0, 8.0, 0.5)
            with col_v2:
                ev  = capi + dette
                mul = ev / ebitda
                val = ev_sect * ebitda - dette
                nb_actions = st.number_input("Nombre d'actions (millions)", 0.1, 1e4, 100.0, 1.0)
                val_par_action = val / nb_actions
                st.metric("Valeur d'entreprise (EV)", f"{ev:.0f} M€")
                st.metric("Multiple EV/EBITDA actuel", f"{mul:.1f}x")
                st.metric("Valeur par action", f"{val_par_action:.2f} €")

    # ════════════════════════════════════════════════════════
    # ONGLET 4 — RISQUE & PERFORMANCE
    # ════════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown("## ⚖️ Analyse Risque / Rendement")

        action_r = st.selectbox("Action à analyser", list(ACTIONS_VEDETTES.keys()), key="risk_action")
        ticker_r = ACTIONS_VEDETTES[action_r]
        hist_r   = get_history(ticker_r, period="1y")

        if not hist_r.empty and len(hist_r) > 20:
            returns = hist_r["Close"].pct_change().dropna()

            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            ret_annuel = returns.mean() * 252 * 100
            vol_annuel = returns.std() * np.sqrt(252) * 100
            sharpe     = calculer_sharpe(returns)
            var_95     = calculer_var(returns, 0.95) * 100

            col_r1.metric("Rendement annualisé", f"{ret_annuel:.1f}%")
            col_r2.metric("Volatilité annualisée", f"{vol_annuel:.1f}%")
            col_r3.metric("Ratio de Sharpe", f"{sharpe:.2f}")
            col_r4.metric("VaR 95% (journalière)", f"{var_95:.2f}%")

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_hist = px.histogram(returns * 100, nbins=50,
                    title="Distribution des rendements journaliers (%)",
                    labels={"value": "Rendement (%)"},
                    color_discrete_sequence=["#2563eb"])
                fig_hist.add_vline(x=var_95, line_dash="dash", line_color="#ef4444",
                                   annotation_text=f"VaR 95%: {var_95:.2f}%")
                fig_hist.update_layout(template="plotly_dark", paper_bgcolor="#0f172a",
                    plot_bgcolor="#0f172a", height=280, showlegend=False,
                    margin=dict(l=0,r=0,t=30,b=0))
                st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar":False})

            with col_g2:
                cumul = (1 + returns).cumprod() - 1
                fig_cumul = go.Figure(go.Scatter(
                    x=cumul.index, y=cumul * 100,
                    fill="tozeroy",
                    line=dict(color="#10b981" if cumul.iloc[-1] >= 0 else "#ef4444", width=2),
                    name="Rendement cumulé",
                ))
                fig_cumul.update_layout(
                    template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a",
                    height=280, title="Performance cumulée (%)",
                    margin=dict(l=0,r=0,t=30,b=0),
                    xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b"),
                )
                st.plotly_chart(fig_cumul, use_container_width=True, config={"displayModeBar":False})

            with st.expander("📚 Comprendre ces indicateurs"):
                st.markdown("""
                **Volatilité (σ)** : Mesure l'amplitude des fluctuations. Plus elle est élevée, plus le risque est grand.

                **Ratio de Sharpe** : Rendement excédentaire par unité de risque.
                - > 1 : Bon · > 2 : Très bon · < 0 : Mauvais

                **VaR 95% journalière** : Perte maximale attendue avec 95% de probabilité sur une journée.
                *Ex : VaR 95% = −2% signifie qu'il y a 5% de chances de perdre plus de 2% en une journée.*
                """)

    # ════════════════════════════════════════════════════════
    # ONGLET 5 — EXERCICES
    # ════════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown("## 🧪 Exercices pratiques")

        exercice = st.radio("Choisissez un exercice", [
            "Calcul de rendement",
            "Valorisation DDM",
            "Analyse PER",
        ], horizontal=True)

        if exercice == "Calcul de rendement":
            st.markdown("### Exercice : Calcul du rendement total")
            with st.expander("📋 Énoncé", expanded=True):
                st.markdown("""
                Vous achetez une action **TotalEnergies** à **60 €**. Un an plus tard, le cours est à **65 €**
                et la société a versé un dividende de **3 €** par action.

                **Calculez le rendement total de votre investissement.**
                """)
            with st.form("ex_rendement"):
                rep = st.number_input("Rendement total (%)", -100.0, 200.0, 0.0, 0.1)
                soumettre = st.form_submit_button("Valider", type="primary")
            if soumettre:
                correct = round((65 - 60 + 3) / 60 * 100, 2)
                if abs(rep - correct) < 0.5:
                    st.success(f"✅ Bravo ! Rendement = (65 − 60 + 3) / 60 = **{correct}%**")
                else:
                    st.error(f"❌ Réponse incorrecte. La bonne réponse est **{correct}%**")
                    st.markdown("**Formule :** Rendement = (P₁ − P₀ + D) / P₀ × 100")

        elif exercice == "Valorisation DDM":
            st.markdown("### Exercice : Modèle Gordon-Shapiro")
            with st.expander("📋 Énoncé", expanded=True):
                st.markdown("""
                Une entreprise verse un dividende de **2 € par action**. Ce dividende devrait croître
                de **4% par an** indéfiniment. Les actionnaires exigent un rendement de **9%**.

                **Quelle est la valeur théorique de l'action ?**
                """)
            with st.form("ex_ddm"):
                rep_ddm = st.number_input("Valeur théorique (€)", 0.0, 1000.0, 0.0, 0.5)
                soumettre_ddm = st.form_submit_button("Valider", type="primary")
            if soumettre_ddm:
                d1 = 2 * 1.04
                val = d1 / (0.09 - 0.04)
                if abs(rep_ddm - val) < 1:
                    st.success(f"✅ Excellent ! P₀ = D₁ / (r − g) = {d1:.2f} / (9% − 4%) = **{val:.2f} €**")
                else:
                    st.error(f"❌ Incorrect. P₀ = {d1:.2f} / 0.05 = **{val:.2f} €**")

        else:
            st.markdown("### Exercice : Analyse comparative PER")
            with st.expander("📋 Énoncé", expanded=True):
                st.markdown("""
                **Société A** : Cours = 120 €, BPA = 8 €  
                **Société B** : Cours = 80 €, BPA = 6 €  
                Le PER sectoriel moyen est de **14x**.

                **Quelle société est la mieux valorisée par rapport au secteur ?**
                """)
            with st.form("ex_per"):
                rep_per = st.radio("Votre réponse", ["Société A", "Société B", "Identiques"])
                soumettre_per = st.form_submit_button("Valider", type="primary")
            if soumettre_per:
                per_a = 120 / 8
                per_b = 80 / 6
                if rep_per == "Société B":
                    st.success(f"✅ Correct ! PER A = {per_a:.1f}x, PER B = {per_b:.1f}x. "
                               f"La société B est plus proche du PER sectoriel ({14}x).")
                else:
                    st.error(f"❌ PER A = {per_a:.1f}x (> {14}x), PER B = {per_b:.1f}x (≈ {14}x). "
                             "La société B est mieux valorisée.")
