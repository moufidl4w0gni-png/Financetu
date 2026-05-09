"""Module Quiz — Questions interactives sur les instruments financiers"""

import streamlit as st
import random
import json
from datetime import datetime

QUESTIONS = [
    # ACTIONS
    {"id":1,"theme":"Actions","niveau":"Débutant","question":"Qu'est-ce qu'une action ?",
     "options":["Un titre de créance","Un titre de propriété d'une fraction du capital","Un contrat d'assurance","Un dépôt bancaire"],
     "correct":1,"explication":"Une action représente une part de propriété dans une entreprise. L'actionnaire devient copropriétaire."},
    {"id":2,"theme":"Actions","niveau":"Intermédiaire","question":"Le Price-Earnings Ratio (PER) est égal à :",
     "options":["Cours / Chiffre d'affaires","Cours / Dividende","Cours / Bénéfice Par Action","Capitalisation / Fonds propres"],
     "correct":2,"explication":"PER = Cours / BPA. Il indique combien fois les bénéfices sont payés par le marché."},
    {"id":3,"theme":"Actions","niveau":"Avancé","question":"Dans le modèle de Gordon-Shapiro, quel est l'impact d'une hausse du taux d'actualisation r sur le prix de l'action ?",
     "options":["Le prix augmente","Le prix reste stable","Le prix baisse","L'effet dépend du dividende"],
     "correct":2,"explication":"P₀ = D₁/(r−g). Si r augmente, le dénominateur augmente, donc P₀ diminue."},
    # OBLIGATIONS
    {"id":4,"theme":"Obligations","niveau":"Débutant","question":"Qu'est-ce que l'effet balançoire sur les obligations ?",
     "options":["Prix et taux évoluent dans le même sens","Prix et taux évoluent en sens inverse","Le coupon varie avec les taux","La duration augmente avec les taux"],
     "correct":1,"explication":"Quand les taux montent, la valeur actualisée des flux futurs baisse, donc le prix de l'obligation baisse. Et vice-versa."},
    {"id":5,"theme":"Obligations","niveau":"Intermédiaire","question":"Une obligation est émise avec un coupon de 4% et le taux de marché est de 6%. L'obligation est :",
     "options":["Au pair","Au-dessus du pair (sur le pair)","En dessous du pair (sous le pair)","Impossible à déterminer"],
     "correct":2,"explication":"Coupon (4%) < Taux marché (6%) → obligation moins attractive → prix < valeur nominale → sous le pair."},
    {"id":6,"theme":"Obligations","niveau":"Avancé","question":"La duration d'une obligation mesure :",
     "options":["La maturité restante","La sensibilité du prix aux variations de taux","Le rendement actuariel","Le risque de défaut"],
     "correct":1,"explication":"La duration est la durée de vie moyenne pondérée des flux. Elle mesure la sensibilité du prix aux variations de taux."},
    # DÉRIVÉS
    {"id":7,"theme":"Dérivés","niveau":"Débutant","question":"Un call donne à son détenteur :",
     "options":["L'obligation d'acheter","Le droit de vendre","Le droit d'acheter","L'obligation de vendre"],
     "correct":2,"explication":"Un call (option d'achat) donne le DROIT (pas l'obligation) d'acheter l'actif sous-jacent au prix d'exercice K."},
    {"id":8,"theme":"Dérivés","niveau":"Intermédiaire","question":"Le delta d'un call est :",
     "options":["Toujours égal à 1","Toujours négatif","Compris entre 0 et 1","Compris entre -1 et 0"],
     "correct":2,"explication":"Le delta d'un call est entre 0 (OTM profond) et 1 (ITM profond). Il mesure la sensibilité du prix de l'option au prix du sous-jacent."},
    {"id":9,"theme":"Dérivés","niveau":"Avancé","question":"Quelle est la relation de parité call-put ?",
     "options":["C - P = S - Ke^(-rT)","C + P = S + Ke^(-rT)","C = P + S","C × P = S × K"],
     "correct":0,"explication":"C − P = S − Ke^(−rT). Cette relation d'absence d'arbitrage lie le prix du call, du put, du sous-jacent et de la valeur actualisée du strike."},
    # FOREX
    {"id":10,"theme":"Forex","niveau":"Débutant","question":"EUR/USD = 1.0850 signifie :",
     "options":["1 USD = 1.0850 EUR","1 EUR = 1.0850 USD","Le spread est de 1.0850","L'EUR a baissé de 1.0850%"],
     "correct":1,"explication":"EUR est la devise de base (1 unité). USD est la devise de cotation. 1 EUR vaut 1.0850 USD."},
    {"id":11,"theme":"Forex","niveau":"Intermédiaire","question":"La parité des pouvoirs d'achat (PPA) stipule que :",
     "options":["Les taux de change sont fixes","Les prix des biens identiques convergent via le taux de change","Les taux d'intérêt déterminent les changes","Les déficits commerciaux appécient la monnaie"],
     "correct":1,"explication":"La PPA prédit qu'à long terme, les taux de change s'ajustent pour égaliser les prix des biens identiques entre pays."},
    # FONDS
    {"id":12,"theme":"Fonds","niveau":"Débutant","question":"Qu'est-ce qu'un ETF ?",
     "options":["Un fonds géré activement","Un tracker qui réplique un indice, coté en Bourse","Une obligation à taux variable","Un compte d'épargne réglementé"],
     "correct":1,"explication":"Un ETF (Exchange-Traded Fund) est un fonds indiciel coté en Bourse qui réplique la performance d'un indice (CAC 40, S&P 500...)."},
    {"id":13,"theme":"Fonds","niveau":"Intermédiaire","question":"Le ratio de Sharpe mesure :",
     "options":["Le rendement absolu d'un portefeuille","Le risque total d'un portefeuille","Le rendement excédentaire par unité de risque","La corrélation avec le marché"],
     "correct":2,"explication":"Sharpe = (Rp − Rf) / σp. Il mesure la performance ajustée du risque. Un ratio > 1 est généralement considéré bon."},
    # MARCHÉ MONÉTAIRE
    {"id":14,"theme":"Monétaire","niveau":"Débutant","question":"L'Euribor est :",
     "options":["Le taux de l'immobilier en zone euro","Le taux interbancaire offert en euros","Le taux directeur de la BCE","Le taux d'inflation européen"],
     "correct":1,"explication":"L'Euribor (Euro Interbank Offered Rate) est le taux moyen auquel les banques européennes se prêtent entre elles."},
    {"id":15,"theme":"Monétaire","niveau":"Avancé","question":"Un Quantitative Easing (QE) consiste pour la banque centrale à :",
     "options":["Augmenter les taux directeurs","Émettre de la monnaie et racheter des actifs","Restreindre la masse monétaire","Interdire les prêts interbancaires"],
     "correct":1,"explication":"Le QE est une politique non-conventionnelle : la BC crée de la monnaie pour racheter des obligations d'État ou d'entreprise, injectant des liquidités dans l'économie."},
]


def render():
    st.markdown("""
    <div class='page-header'>
        <div class='page-icon' style='background:linear-gradient(135deg,#dc2626,#f97316);'>📝</div>
        <div>
            <p class='page-title'>Quiz Interactifs</p>
            <p class='page-subtitle'>Testez vos connaissances sur les instruments financiers</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Init session
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_total" not in st.session_state:
        st.session_state.quiz_total = 0
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_questions" not in st.session_state:
        st.session_state.quiz_questions = []

    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        theme_sel = st.selectbox("Thème", ["Tous"] + list(set(q["theme"] for q in QUESTIONS)))
    with col_f2:
        niveau_sel = st.selectbox("Niveau", ["Tous", "Débutant", "Intermédiaire", "Avancé"])
    with col_f3:
        nb_q = st.selectbox("Nombre de questions", [5, 10, 15], index=0)

    # Filtrer
    qs_filtrees = [q for q in QUESTIONS
                   if (theme_sel == "Tous" or q["theme"] == theme_sel) and
                      (niveau_sel == "Tous" or q["niveau"] == niveau_sel)]

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🎲 Nouveau quiz", type="primary", use_container_width=True):
            selected = random.sample(qs_filtrees, min(nb_q, len(qs_filtrees)))
            st.session_state.quiz_questions = selected
            st.session_state.quiz_answers = {}
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.rerun()

    if not st.session_state.quiz_questions:
        st.info("👆 Configurez vos filtres et cliquez sur **Nouveau quiz** pour commencer !")
        st.markdown("### 📊 Statistiques globales")
        themes = list(set(q["theme"] for q in QUESTIONS))
        for theme in themes:
            n = len([q for q in QUESTIONS if q["theme"] == theme])
            st.markdown(f"- **{theme}** : {n} questions disponibles")
        return

    questions = st.session_state.quiz_questions
    answers   = st.session_state.quiz_answers
    total_q   = len(questions)
    answered  = len(answers)
    score     = sum(1 for qid, ans in answers.items()
                    if next((q for q in questions if q["id"] == qid), {}).get("correct") == ans)

    # Barre de progression
    st.progress(answered / total_q, text=f"Question {answered}/{total_q} · Score : {score}/{answered if answered else 1}")

    # Questions
    for i, q in enumerate(questions):
        with st.container():
            niveau_color = {"Débutant":"#10b981","Intermédiaire":"#f59e0b","Avancé":"#ef4444"}.get(q["niveau"],"#60a5fa")
            st.markdown(f"""
            <div style='background:#1e293b;border:1px solid #334155;border-radius:12px;
                        padding:20px;margin-bottom:12px;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'>
                    <span style='font-weight:600;color:#f1f5f9'>Q{i+1}. {q["question"]}</span>
                    <div>
                        <span style='background:rgba(96,165,250,0.15);color:#60a5fa;font-size:11px;
                               padding:2px 8px;border-radius:12px;margin-right:4px'>{q["theme"]}</span>
                        <span style='background:rgba(0,0,0,0.3);color:{niveau_color};font-size:11px;
                               padding:2px 8px;border-radius:12px'>{q["niveau"]}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            already_answered = q["id"] in answers
            if already_answered:
                user_ans = answers[q["id"]]
                correct_ans = q["correct"]
                for j, opt in enumerate(q["options"]):
                    if j == correct_ans:
                        st.markdown(f"✅ **{opt}** ← Bonne réponse")
                    elif j == user_ans:
                        st.markdown(f"❌ ~~{opt}~~ ← Votre réponse")
                    else:
                        st.markdown(f"  {opt}")
                if user_ans == correct_ans:
                    st.success(f"🎉 Correct ! {q['explication']}")
                else:
                    st.error(f"💡 {q['explication']}")
            else:
                choix = st.radio(
                    f"Q{i+1}", q["options"],
                    key=f"quiz_{q['id']}", index=None,
                    label_visibility="collapsed"
                )
                if choix is not None:
                    idx_choix = q["options"].index(choix)
                    answers[q["id"]] = idx_choix
                    st.session_state.quiz_answers = answers
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # Résultats finaux
    if answered == total_q:
        st.markdown("---")
        st.markdown("## 🏆 Résultats")
        note = score / total_q * 20
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Score", f"{score}/{total_q}")
        col_r2.metric("Note", f"{note:.1f}/20")
        col_r3.metric("Réussite", f"{score/total_q*100:.0f}%")

        if note >= 16:
            st.success("🥇 Excellent ! Vous maîtrisez parfaitement ce sujet !")
        elif note >= 12:
            st.info("🥈 Bien ! Quelques points à revoir.")
        elif note >= 10:
            st.warning("🥉 Passable. Relisez les cours correspondants.")
        else:
            st.error("📚 À retravailler. Consultez les modules de cours.")

        if st.button("🔄 Refaire un quiz", type="primary"):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.rerun()
