"""CSS global de la plateforme FinLearn"""

import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #0f172a !important;
    color: #f1f5f9 !important;
}
[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.main .block-container { padding: 1.5rem 2rem !important; max-width: 1400px; }
h1,h2,h3,h4,h5,h6 { font-family: 'Inter', sans-serif !important; }

/* ── BOUTONS ─────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1e40af, #1d4ed8) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.5) !important;
}
.stButton > button[kind="secondary"] {
    background: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #334155 !important;
    color: #f1f5f9 !important;
}

/* ── INPUTS ──────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.2) !important;
}

/* ── MÉTRIQUES ───────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #1e293b !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

/* ── DATAFRAMES ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
.dvn-scroller { background: #1e293b !important; }

/* ── EXPANDER ────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ── PAGE DE CONNEXION ───────────────────────────────────── */
.login-container {
    text-align: center;
    padding: 32px 0 16px;
}
.login-logo {
    font-size: 52px;
    margin-bottom: 8px;
    filter: drop-shadow(0 0 20px rgba(37,99,235,0.6));
}
.login-title {
    font-size: 36px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
}
.login-subtitle {
    font-size: 14px;
    color: #94a3b8;
    margin: 6px 0 16px;
}
.login-badge {
    display: inline-block;
    background: rgba(37,99,235,0.15);
    border: 1px solid rgba(37,99,235,0.3);
    color: #60a5fa;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.login-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px;
    margin: 20px 0;
}
.ent-info {
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
}

/* ── SIDEBAR USER ────────────────────────────────────────── */
.sidebar-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: rgba(37,99,235,0.12);
    border-radius: 10px;
    border: 1px solid rgba(37,99,235,0.2);
}
.sidebar-avatar {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 15px; color: white;
    flex-shrink: 0;
}
.sidebar-name { font-weight: 600; font-size: 14px; color: #f1f5f9; }
.sidebar-role { font-size: 11px; color: #94a3b8; margin-top: 1px; }

/* ── CARDS ───────────────────────────────────────────────── */
.fin-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.fin-card:hover { border-color: #2563eb; }

.fin-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.fin-card-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}
.fin-card-title { font-size: 15px; font-weight: 600; color: #f1f5f9; }
.fin-card-desc  { font-size: 13px; color: #94a3b8; line-height: 1.6; }

/* ── PRIX TEMPS RÉEL ─────────────────────────────────────── */
.price-up   { color: #10b981 !important; font-weight: 600; }
.price-down { color: #ef4444 !important; font-weight: 600; }
.price-mono { font-family: 'JetBrains Mono', monospace !important; }

.ticker-badge {
    display: inline-block;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    color: #60a5fa;
}

/* ── QUIZ ────────────────────────────────────────────────── */
.quiz-question {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
}
.quiz-correct { border-color: #10b981 !important; background: rgba(16,185,129,0.08) !important; }
.quiz-wrong   { border-color: #ef4444 !important; background: rgba(239,68,68,0.08) !important; }

/* ── PROGRESS MODULE ─────────────────────────────────────── */
.module-badge-done {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    border: 1px solid #10b981;
    color: #10b981;
    font-size: 11px; font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
}
.module-badge-todo {
    display: inline-block;
    background: rgba(148,163,184,0.1);
    border: 1px solid #334155;
    color: #94a3b8;
    font-size: 11px; font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
}

/* ── PAGE HEADERS ────────────────────────────────────────── */
.page-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 28px;
    padding-bottom: 20px;
    border-bottom: 1px solid #1e293b;
}
.page-icon {
    width: 52px; height: 52px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
}
.page-title { font-size: 24px; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-subtitle { font-size: 14px; color: #94a3b8; margin: 4px 0 0; }

/* ── ALERTES ─────────────────────────────────────────────── */
.stAlert { border-radius: 10px !important; }
.stSuccess { background: rgba(16,185,129,0.1) !important; border: 1px solid #10b981 !important; }
.stError   { background: rgba(239,68,68,0.1) !important;  border: 1px solid #ef4444 !important; }
.stInfo    { background: rgba(37,99,235,0.1) !important;  border: 1px solid #2563eb !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border: 1px solid #f59e0b !important; }

/* ── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }

/* ── SIDEBAR BUTTONS ─────────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    justify-content: flex-start !important;
    border-radius: 8px !important;
    margin-bottom: 2px !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #1e293b !important;
    color: #f1f5f9 !important;
}
</style>
""", unsafe_allow_html=True)
