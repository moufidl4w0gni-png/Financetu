"""Glossaire Financier — FinLearn"""

import streamlit as st

GLOSSAIRE = {
    "A": [
        ("Action", "Titre de propriété représentant une fraction du capital d'une société. Confère des droits de vote et au dividende."),
        ("Actif sous-jacent", "Actif sur lequel porte un produit dérivé (action, indice, devise, matière première...)."),
        ("Arbitrage", "Stratégie consistant à exploiter des différences de prix pour un même actif sur différents marchés, sans risque théorique."),
        ("Asset Management", "Gestion d'actifs financiers pour le compte de tiers (particuliers, institutionnels)."),
        ("Aversion au risque", "Préférence d'un investisseur pour un rendement certain plutôt qu'un rendement incertain de même espérance."),
    ],
    "B": [
        ("Bêta (β)", "Mesure de la sensibilité d'un titre aux mouvements du marché. β=1 suit le marché, β>1 amplifie, β<1 amortit."),
        ("Bid-Ask Spread", "Écart entre le prix d'achat (bid) et le prix de vente (ask) d'un actif. Mesure le coût de transaction."),
        ("Black-Scholes", "Modèle mathématique de valorisation des options développé en 1973 par Fischer Black et Myron Scholes."),
        ("Bons du Trésor", "Titres de créance à court terme émis par l'État pour financer ses besoins de trésorerie."),
        ("BPA (Bénéfice Par Action)", "Bénéfice net divisé par le nombre d'actions en circulation. Indicateur clé de la rentabilité."),
    ],
    "C": [
        ("CAC 40", "Indice boursier des 40 plus grandes capitalisations de la Bourse de Paris (Euronext)."),
        ("Call", "Option d'achat donnant le droit (non l'obligation) d'acheter un actif à un prix fixé."),
        ("Capitalisation boursière", "Valeur de marché d'une entreprise = Nombre d'actions × Cours de l'action."),
        ("Contrat Future", "Engagement ferme d'acheter ou de vendre un actif à une date et un prix convenus, sur marché organisé."),
        ("Coupon", "Intérêt périodique versé par l'émetteur d'une obligation à son détenteur."),
        ("Courbe des taux", "Représentation graphique des rendements obligataires selon leur maturité."),
    ],
    "D": [
        ("Delta (Δ)", "Sensibilité du prix d'une option à la variation du prix du sous-jacent. Entre 0 et 1 pour un call."),
        ("Diversification", "Stratégie consistant à répartir les investissements pour réduire le risque spécifique."),
        ("Dividende", "Part du bénéfice distribuée par une société à ses actionnaires."),
        ("Duration", "Durée de vie moyenne pondérée des flux d'une obligation. Mesure sa sensibilité aux taux d'intérêt."),
    ],
    "E": [
        ("EBITDA", "Bénéfice avant intérêts, impôts, dépréciation et amortissement. Indicateur de la rentabilité opérationnelle."),
        ("Effet de levier", "Utilisation de l'endettement ou des dérivés pour amplifier les gains (et les pertes) potentiels."),
        ("ETF (Exchange-Traded Fund)", "Fonds indiciel coté en Bourse répliquant la performance d'un indice."),
        ("Euribor", "Euro Interbank Offered Rate. Taux interbancaire de référence en zone euro."),
        ("EV (Enterprise Value)", "Valeur d'entreprise = Capitalisation + Dette nette. Mesure la valeur totale de l'entreprise."),
    ],
    "F": [
        ("Forward", "Contrat à terme de gré à gré (OTC) engageant à acheter/vendre un actif à terme à un prix fixé."),
        ("Futures", "Contrats à terme standardisés négociés sur marchés organisés."),
        ("FCP (Fonds Commun de Placement)", "Type d'OPCVM sans personnalité morale, copropriété de valeurs mobilières."),
    ],
    "G": [
        ("Gamma (Γ)", "Variation du delta par rapport au prix du sous-jacent. Mesure la convexité d'une option."),
        ("Gordon-Shapiro", "Modèle de valorisation d'une action basé sur l'actualisation des dividendes futurs. P₀ = D₁/(r-g)."),
    ],
    "H": [
        ("Hedge Fund", "Fonds d'investissement alternatif utilisant des stratégies complexes pour générer des rendements absolus."),
        ("Hedging", "Couverture d'un risque financier par une position compensatoire sur les marchés dérivés."),
    ],
    "I": [
        ("Indice boursier", "Indicateur synthétique représentant la performance d'un panier d'actions (CAC40, S&P500...)."),
        ("IPO (Introduction en Bourse)", "Première cotation des actions d'une société sur un marché boursier réglementé."),
        ("IRS (Interest Rate Swap)", "Échange de flux à taux fixe contre flux à taux variable entre deux contreparties."),
    ],
    "L": [
        ("LBO (Leveraged Buy-Out)", "Rachat d'une entreprise financé majoritairement par emprunt."),
        ("Liquidité", "Facilité à acheter ou vendre un actif rapidement sans impact significatif sur son prix."),
        ("LIBOR", "London Interbank Offered Rate. Ancien taux de référence interbancaire (remplacé par SOFR/SONIA)."),
    ],
    "M": [
        ("Marché primaire", "Marché sur lequel sont émis de nouveaux titres financiers (actions, obligations)."),
        ("Marché secondaire", "Marché sur lequel s'échangent les titres déjà émis entre investisseurs."),
        ("Maturité", "Date à laquelle une obligation arrive à échéance et est remboursée."),
        ("Modèle de Black-Scholes", "Formule mathématique permettant de calculer le prix théorique d'une option européenne."),
    ],
    "O": [
        ("OAT (Obligation Assimilable du Trésor)", "Obligation d'État français à moyen et long terme."),
        ("OPCVM", "Organisme de Placement Collectif en Valeurs Mobilières. Catégorie regroupant SICAV et FCP."),
        ("Option", "Contrat donnant le droit (non l'obligation) d'acheter (call) ou de vendre (put) un actif à un prix fixé."),
        ("OTC (Over-The-Counter)", "Marché de gré à gré, entre deux contreparties directement, sans marché organisé."),
    ],
    "P": [
        ("PER (Price-Earnings Ratio)", "Ratio Cours/BPA. Indique combien de fois les bénéfices sont payés par le marché."),
        ("Pip", "Plus petite variation d'un taux de change. 0.0001 pour EUR/USD."),
        ("Portefeuille", "Ensemble des actifs financiers détenus par un investisseur."),
        ("PPA (Parité des Pouvoirs d'Achat)", "Théorie selon laquelle les taux de change s'ajustent pour égaliser les prix entre pays."),
        ("Prime de risque", "Rendement supplémentaire exigé par un investisseur pour compenser un risque plus élevé."),
        ("Put", "Option de vente donnant le droit (non l'obligation) de vendre un actif au prix d'exercice."),
    ],
    "Q": [
        ("QE (Quantitative Easing)", "Politique monétaire non conventionnelle : la banque centrale rachète des actifs pour injecter des liquidités."),
        ("Quote (cotation)", "Prix auquel un actif est proposé à l'achat ou à la vente sur un marché."),
    ],
    "R": [
        ("Rendement actuariel", "Taux interne de rentabilité d'une obligation tenant compte du prix payé et des flux futurs."),
        ("Risque de contrepartie", "Risque qu'une contrepartie ne respecte pas ses engagements contractuels."),
        ("Risque systématique", "Risque lié au marché dans son ensemble, non diversifiable."),
        ("Risque spécifique", "Risque propre à un actif ou secteur, réductible par diversification."),
    ],
    "S": [
        ("S&P 500", "Indice des 500 plus grandes capitalisations boursières américaines."),
        ("Sharpe (ratio de)", "Mesure de la performance ajustée du risque : (Rp − Rf) / σp."),
        ("SICAV", "Société d'Investissement à Capital Variable. Type d'OPCVM avec personnalité morale."),
        ("Spread", "Écart entre deux taux ou deux prix. Ex : spread de crédit = différentiel de taux entre une obligation risquée et le taux sans risque."),
        ("Swap", "Échange de flux financiers entre deux contreparties sur une période donnée."),
    ],
    "T": [
        ("Theta (Θ)", "Dépréciation temporelle d'une option : perte de valeur liée au passage du temps."),
        ("TER (Total Expense Ratio)", "Coût total annuel d'un fonds, exprimé en pourcentage de l'actif géré."),
        ("TMST (Taux Marginal de Substitution Technique)", "Quantité d'un facteur à substituer à un autre pour maintenir la production constante."),
    ],
    "V": [
        ("VaR (Value at Risk)", "Perte maximale attendue sur un horizon donné avec un niveau de confiance fixé (ex: 95%)."),
        ("Vega (ν)", "Sensibilité du prix d'une option à la volatilité implicite du sous-jacent."),
        ("Volatilité", "Mesure des fluctuations d'un actif. Écart-type des rendements, annualisé."),
        ("VL (Valeur Liquidative)", "Prix d'une part d'OPCVM = Actif net / Nombre de parts en circulation."),
    ],
}


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#1e40af,#3b82f6);'>📖</div>
        <div>
            <p class='page-title'>Glossaire Financier</p>
            <p class='page-subtitle'>Dictionnaire complet des termes financiers essentiels</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recherche
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        recherche = st.text_input("🔍 Rechercher un terme", placeholder="Ex: dividende, option, PER...")
    with col_s2:
        lettre_sel = st.selectbox("Lettre", ["Toutes"] + sorted(GLOSSAIRE.keys()))

    if recherche:
        resultats = []
        for lettre, termes in GLOSSAIRE.items():
            for terme, def_ in termes:
                if recherche.lower() in terme.lower() or recherche.lower() in def_.lower():
                    resultats.append((terme, def_))
        if resultats:
            st.markdown(f"**{len(resultats)} résultat(s) pour « {recherche} »**")
            for terme, def_ in resultats:
                with st.expander(f"**{terme}**"):
                    st.markdown(def_)
        else:
            st.warning(f"Aucun résultat pour « {recherche} »")
    else:
        lettres = [lettre_sel] if lettre_sel != "Toutes" else sorted(GLOSSAIRE.keys())
        for lettre in lettres:
            st.markdown(f"## {lettre}")
            for terme, definition in GLOSSAIRE[lettre]:
                with st.expander(f"**{terme}**"):
                    st.markdown(definition)

    st.markdown("---")
    total_termes = sum(len(v) for v in GLOSSAIRE.values())
    st.caption(f"📚 {total_termes} termes financiers · {len(GLOSSAIRE)} lettres couvertes · FinLearn 2025")
