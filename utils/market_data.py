"""
Données de marché en temps réel
=================================
Source : Yahoo Finance via yfinance
Avec cache intelligent pour limiter les appels API
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_OK = True
except ImportError:
    YFINANCE_OK = False

# ─────────────────────────────────────────────────────────────
# TICKERS DE RÉFÉRENCE
# ─────────────────────────────────────────────────────────────

INDICES = {
    "CAC 40":        "^FCHI",
    "S&P 500":       "^GSPC",
    "NASDAQ":        "^IXIC",
    "DAX":           "^GDAXI",
    "EURO STOXX 50": "^STOXX50E",
    "Nikkei 225":    "^N225",
}

ACTIONS_VEDETTES = {
    "LVMH":       "MC.PA",
    "TotalEnergies": "TTE.PA",
    "BNP Paribas": "BNP.PA",
    "Airbus":     "AIR.PA",
    "Stellantis": "STLAM.MI",
    "Apple":      "AAPL",
    "Microsoft":  "MSFT",
    "NVIDIA":     "NVDA",
    "Tesla":      "TSLA",
    "Amazon":     "AMZN",
}

FOREX_PAIRS = {
    "EUR/USD": "EURUSD=X",
    "EUR/GBP": "EURGBP=X",
    "USD/JPY": "JPY=X",
    "EUR/CHF": "EURCHF=X",
    "GBP/USD": "GBPUSD=X",
}

CRYPTOS = {
    "Bitcoin":  "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana":   "SOL-USD",
    "Ripple":   "XRP-USD",
}

OBLIGATIONS = {
    "OAT 10 ans (France)":   "^TNX",
    "Bund 10 ans (Allemagne)": "^DE10YT=RR",
    "Treasury 10Y (USA)":    "^TNX",
    "Treasury 2Y (USA)":     "^IRX",
}

MATIERES_PREMIERES = {
    "Or":       "GC=F",
    "Pétrole":  "CL=F",
    "Argent":   "SI=F",
    "Gaz naturel": "NG=F",
}

# ─────────────────────────────────────────────────────────────
# FONCTIONS DE RÉCUPÉRATION (avec cache)
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)  # Cache 60 secondes
def get_quote(ticker: str) -> dict:
    """Récupère le cours temps réel d'un ticker."""
    if not YFINANCE_OK:
        return _mock_quote(ticker)
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d", interval="1d")
        if hist.empty:
            return _mock_quote(ticker)
        price  = float(info.last_price) if hasattr(info, 'last_price') and info.last_price else float(hist["Close"].iloc[-1])
        prev   = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
        change = price - prev
        pct    = (change / prev * 100) if prev != 0 else 0
        return {
            "ticker":   ticker,
            "price":    round(price, 2),
            "change":   round(change, 2),
            "pct":      round(pct, 2),
            "prev":     round(prev, 2),
            "volume":   getattr(info, 'three_month_average_volume', 0) or 0,
            "ok":       True,
            "updated":  datetime.now().strftime("%H:%M:%S"),
        }
    except Exception:
        return _mock_quote(ticker)


@st.cache_data(ttl=300)  # Cache 5 minutes
def get_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Récupère l'historique de prix."""
    if not YFINANCE_OK:
        return _mock_history(ticker, period)
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df.empty:
            return _mock_history(ticker, period)
        df.index = pd.to_datetime(df.index)
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception:
        return _mock_history(ticker, period)


@st.cache_data(ttl=3600)  # Cache 1 heure
def get_info(ticker: str) -> dict:
    """Récupère les informations fondamentales."""
    if not YFINANCE_OK:
        return {}
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "name":        info.get("longName", ticker),
            "sector":      info.get("sector", "N/A"),
            "market_cap":  info.get("marketCap", 0),
            "pe_ratio":    info.get("trailingPE", None),
            "dividend":    info.get("dividendYield", None),
            "beta":        info.get("beta", None),
            "52w_high":    info.get("fiftyTwoWeekHigh", None),
            "52w_low":     info.get("fiftyTwoWeekLow", None),
            "currency":    info.get("currency", "EUR"),
            "exchange":    info.get("exchange", "N/A"),
            "description": info.get("longBusinessSummary", "")[:500],
        }
    except Exception:
        return {}


@st.cache_data(ttl=60)
def get_multiple_quotes(tickers: dict) -> pd.DataFrame:
    """Récupère les cours de plusieurs tickers en une fois."""
    rows = []
    for name, ticker in tickers.items():
        q = get_quote(ticker)
        rows.append({
            "Nom":        name,
            "Ticker":     ticker,
            "Prix":       q["price"],
            "Variation":  q["change"],
            "Var. (%)":   q["pct"],
            "Statut":     "🟢" if q["pct"] >= 0 else "🔴",
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def get_bond_yield(maturity_years: int = 10) -> float:
    """Récupère le taux des obligations d'État."""
    try:
        if maturity_years <= 2:
            ticker = "^IRX"
        elif maturity_years <= 5:
            ticker = "^FVX"
        else:
            ticker = "^TNX"
        q = get_quote(ticker)
        return q["price"]
    except Exception:
        return 3.5 + (maturity_years * 0.05)  # Valeur de repli


# ─────────────────────────────────────────────────────────────
# DONNÉES MOCK (si yfinance indisponible)
# ─────────────────────────────────────────────────────────────

def _mock_quote(ticker: str) -> dict:
    """Génère des données simulées réalistes."""
    seed = sum(ord(c) for c in ticker)
    np.random.seed(seed % 1000)
    base_prices = {
        "^FCHI": 7450, "^GSPC": 5100, "^IXIC": 16000,
        "MC.PA": 720, "AAPL": 185, "MSFT": 415, "NVDA": 850,
        "EURUSD=X": 1.085, "BTC-USD": 67000, "GC=F": 2300,
        "^TNX": 4.25, "CL=F": 78,
    }
    price = base_prices.get(ticker, 100 + seed % 900)
    pct   = round(np.random.uniform(-2.5, 2.5), 2)
    change = round(price * pct / 100, 2)
    return {
        "ticker": ticker,
        "price":  round(price + np.random.uniform(-price*0.01, price*0.01), 2),
        "change": change,
        "pct":    pct,
        "prev":   round(price, 2),
        "volume": int(np.random.uniform(1e6, 50e6)),
        "ok":     True,
        "updated": datetime.now().strftime("%H:%M:%S"),
    }


def _mock_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Génère un historique de prix simulé."""
    periods_map = {"1d":1, "5d":5, "1mo":22, "3mo":66, "6mo":130, "1y":252, "2y":504}
    n = periods_map.get(period, 252)
    seed = sum(ord(c) for c in ticker)
    np.random.seed(seed % 1000)
    base_prices = {
        "^FCHI": 7450, "^GSPC": 5100, "^IXIC": 16000,
        "MC.PA": 720, "AAPL": 185, "MSFT": 415, "NVDA": 850,
        "EURUSD=X": 1.085, "BTC-USD": 67000,
    }
    start = base_prices.get(ticker, 100 + seed % 400)
    returns = np.random.normal(0.0003, 0.012, n)
    prices  = start * np.exp(np.cumsum(returns))
    dates   = pd.date_range(end=datetime.now(), periods=n, freq="B")
    lows    = prices * (1 - np.abs(np.random.normal(0, 0.005, n)))
    highs   = prices * (1 + np.abs(np.random.normal(0, 0.005, n)))
    opens   = prices * (1 + np.random.normal(0, 0.003, n))
    return pd.DataFrame({
        "Open":   opens, "High": highs, "Low": lows,
        "Close":  prices,
        "Volume": np.random.randint(500000, 50000000, n)
    }, index=dates)


# ─────────────────────────────────────────────────────────────
# CALCULS FINANCIERS UTILITAIRES
# ─────────────────────────────────────────────────────────────

def calculer_rendement_obligataire(prix: float, coupon: float, valeur_nominale: float, maturite: int) -> float:
    """Calcule le taux de rendement actuariel d'une obligation (Newton-Raphson)."""
    taux = coupon / valeur_nominale
    for _ in range(100):
        flux = sum([coupon / (1 + taux) ** t for t in range(1, maturite + 1)])
        flux += valeur_nominale / (1 + taux) ** maturite
        f    = flux - prix
        df   = sum([-t * coupon / (1 + taux) ** (t + 1) for t in range(1, maturite + 1)])
        df  -= maturite * valeur_nominale / (1 + taux) ** (maturite + 1)
        if abs(df) < 1e-10:
            break
        taux -= f / df
    return round(taux * 100, 4)


def black_scholes(S, K, T, r, sigma, option_type="call"):
    """Calcule le prix d'une option via Black-Scholes."""
    from math import log, sqrt, exp
    try:
        from scipy.stats import norm
        use_scipy = True
    except ImportError:
        use_scipy = False

    if T <= 0:
        return max(0, S - K) if option_type == "call" else max(0, K - S)

    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)

    def N(x):
        if use_scipy:
            return norm.cdf(x)
        # Approximation si scipy absent
        return 0.5 * (1 + np.tanh(x * 0.7071067811865476))

    if option_type == "call":
        return round(S * N(d1) - K * exp(-r * T) * N(d2), 4)
    else:
        return round(K * exp(-r * T) * N(-d2) - S * N(-d1), 4)


def calculer_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Calcule la Value at Risk (VaR) historique."""
    return round(float(returns.quantile(1 - confidence)), 4)


def calculer_sharpe(returns: pd.Series, risk_free: float = 0.03) -> float:
    """Calcule le ratio de Sharpe annualisé."""
    if returns.std() == 0:
        return 0
    excess = returns.mean() * 252 - risk_free
    return round(excess / (returns.std() * np.sqrt(252)), 2)


def format_price(price: float, currency: str = "€") -> str:
    """Formate un prix avec la devise appropriée."""
    if price >= 1_000_000_000:
        return f"{price/1e9:.2f}Md{currency}"
    if price >= 1_000_000:
        return f"{price/1e6:.2f}M{currency}"
    if price >= 1_000:
        return f"{price:,.0f}{currency}"
    return f"{price:.4f}{currency}" if price < 0.1 else f"{price:.2f}{currency}"
