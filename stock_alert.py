import os
import time
import schedule
import requests
import yfinance as yf
import numpy as np
import pandas as pd

from datetime import datetime


# =========================================================
# 1) Telegram
# =========================================================
# ضع التوكن الجديد في متغير البيئة TELEGRAM_BOT_TOKEN
# ولا تضعه داخل الملف.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# أبقيت Chat IDs التي أرسلتها كما هي.
CHAT_IDS = [
    "615265045",
    "7775490993",
    "5574232437",
]

if not TOKEN:
    raise RuntimeError(
        "ضع توكن البوت الجديد في متغير البيئة TELEGRAM_BOT_TOKEN"
    )


# =========================================================
# 2) Timeframes: 15m and above
# =========================================================
TIMEFRAMES = {
    "15m": {"interval": "15m", "period": "60d", "name": "15 دقيقة"},
    "30m": {"interval": "30m", "period": "60d", "name": "30 دقيقة"},
    "1h":  {"interval": "1h",  "period": "60d", "name": "ساعة"},
    "4h":  {"interval": "1h",  "period": "60d", "name": "4 ساعات", "resample_4h": True},
    "1d":  {"interval": "1d",  "period": "2y",  "name": "يومي"},
    "1wk": {"interval": "1wk", "period": "5y",  "name": "أسبوعي"},
}


# =========================================================
# 3) Pine role-reversal settings
# =========================================================
# مطابق للأرقام الموجودة في Pine الذي أرسلته.
ROLE_RULES = {
    tf: {
        "pivot_minor": 3,
        "pivot_major": 7,
        "prox_pct": 1.5,
        "pct_thresh": 3.0,
        "min_bars": 3,
        "retest_margin": 0.5,
        "min_bounce_pct": 0.004,
    }
    for tf in TIMEFRAMES
}


# منع تكرار نفس الإشارة لنفس السهم/الفريم/الاتجاه/الشمعة.
sent_signals = set()


# =========================================================
# 4) STOCKS
# =========================================================
# ألصق هنا قاموس STOCKS الأصلي الذي أرسلته كما هو.
# مثال:
# STOCKS = {
#     "AAPL": "💻 تكنولوجيا",
#     "MSFT": "💻 تكنولوجيا",
#     ...
# }
#
# لتجنب إخفاء أي سهم من قائمتك الأصلية، الملف يستخدم نفس
# البنية دون تغيير. ضع قائمتك الكاملة هنا.
STOCKS = {
    "AAPL": "💻 تكنولوجيا",
    "MSFT": "💻 تكنولوجيا",
    "NVDA": "💻 تكنولوجيا",
    "GOOGL": "💻 تكنولوجيا",
    "GOOG": "💻 تكنولوجيا",
    "META": "💻 تكنولوجيا",
    "AMZN": "💻 تكنولوجيا",
    "TSLA": "💻 تكنولوجيا",
    "AMD": "💻 تكنولوجيا",
    "INTC": "💻 تكنولوجيا",
    "CRM": "💻 تكنولوجيا",
    "ORCL": "💻 تكنولوجيا",
    "ADBE": "💻 تكنولوجيا",
    "QCOM": "💻 تكنولوجيا",
    "AMAT": "💻 تكنولوجيا",
    "MU": "💻 تكنولوجيا",
    "LRCX": "💻 تكنولوجيا",
    "KLAC": "💻 تكنولوجيا",
    "PANW": "💻 تكنولوجيا",
    "CRWD": "💻 تكنولوجيا",
    "ZS": "💻 تكنولوجيا",
    "FTNT": "💻 تكنولوجيا",
    "NET": "💻 تكنولوجيا",
    "SNOW": "💻 تكنولوجيا",
    "DDOG": "💻 تكنولوجيا",
    "PLTR": "💻 تكنولوجيا",
    "AVGO": "💻 تكنولوجيا",
    "MRVL": "💻 تكنولوجيا",
    "ARM": "💻 تكنولوجيا",
    "NOW": "💻 تكنولوجيا",
    "SMCI": "💻 تكنولوجيا",
    "TXN": "💻 تكنولوجيا",
    "SNPS": "💻 تكنولوجيا",
    "CDNS": "💻 تكنولوجيا",
    "TEAM": "💻 تكنولوجيا",
    "MDB": "💻 تكنولوجيا",
    "SHOP": "💻 تكنولوجيا",
    "ADSK": "💻 تكنولوجيا",
    "ANSS": "💻 تكنولوجيا",
    "ROP": "💻 تكنولوجيا",
    "ENPH": "💻 تكنولوجيا",
    "FSLR": "💻 تكنولوجيا",
    "CSCO": "💻 تكنولوجيا",
    "IBM": "💻 تكنولوجيا",
    "INTU": "💻 تكنولوجيا",
    "ADI": "💻 تكنولوجيا",
    "NXPI": "💻 تكنولوجيا",
    "MCHP": "💻 تكنولوجيا",
    "ON": "💻 تكنولوجيا",
    "MPWR": "💻 تكنولوجيا",
    "KEYS": "💻 تكنولوجيا",
    "TER": "💻 تكنولوجيا",
    "SWKS": "💻 تكنولوجيا",
    "QRVO": "💻 تكنولوجيا",
    "WDC": "💻 تكنولوجيا",
    "STX": "💻 تكنولوجيا",
    "NTAP": "💻 تكنولوجيا",
    "HPQ": "💻 تكنولوجيا",
    "DELL": "💻 تكنولوجيا",
    "HPE": "💻 تكنولوجيا",
    "CDW": "💻 تكنولوجيا",
    "CTSH": "💻 تكنولوجيا",
    "IT": "💻 تكنولوجيا",
    "ACN": "💻 تكنولوجيا",
    "EPAM": "💻 تكنولوجيا",
    "GEN": "💻 تكنولوجيا",
    "FFIV": "💻 تكنولوجيا",
    "AKAM": "💻 تكنولوجيا",
    "VRSN": "💻 تكنولوجيا",
    "OKTA": "💻 تكنولوجيا",
    "PATH": "💻 تكنولوجيا",
    "TOST": "💻 تكنولوجيا",
    "U": "💻 تكنولوجيا",
    "RBLX": "💻 تكنولوجيا",
    "TTD": "💻 تكنولوجيا",
    "APP": "💻 تكنولوجيا",
    "ZI": "💻 تكنولوجيا",
    "HUBS": "💻 تكنولوجيا",
    "WDAY": "💻 تكنولوجيا",
    "PAYC": "💻 تكنولوجيا",
    "PCTY": "💻 تكنولوجيا",
    "DOCU": "💻 تكنولوجيا",
    "ZM": "💻 تكنولوجيا",
    "DBX": "💻 تكنولوجيا",
    "BOX": "💻 تكنولوجيا",
    "ESTC": "💻 تكنولوجيا",
    "DT": "💻 تكنولوجيا",
    "CFLT": "💻 تكنولوجيا",
    "S": "💻 تكنولوجيا",
    "CR": "💻 تكنولوجيا",
    "GTLB": "💻 تكنولوجيا",
    "AI": "💻 تكنولوجيا",
    "BBAI": "💻 تكنولوجيا",
    "SOUN": "💻 تكنولوجيا",
    "APPF": "💻 تكنولوجيا",
    "ALRM": "💻 تكنولوجيا",
    "DOCN": "💻 تكنولوجيا",
    "FROG": "💻 تكنولوجيا",
    "MNDY": "💻 تكنولوجيا",
    "CYBR": "💻 تكنولوجيا",
    "QLYS": "💻 تكنولوجيا",
    "TENB": "💻 تكنولوجيا",
    "RPD": "💻 تكنولوجيا",
    "VRNS": "💻 تكنولوجيا",
    "SAIL": "💻 تكنولوجيا",

    "JPM": "🏦 مالية",
    "BAC": "🏦 مالية",
    "GS": "🏦 مالية",
    "MS": "🏦 مالية",
    "WFC": "🏦 مالية",
    "C": "🏦 مالية",
    "BLK": "🏦 مالية",
    "AXP": "🏦 مالية",
    "V": "🏦 مالية",
    "MA": "🏦 مالية",
    "COF": "🏦 مالية",
    "DFS": "🏦 مالية",
    "PYPL": "🏦 مالية",
    "SQ": "🏦 مالية",
    "COIN": "🏦 مالية",
    "HOOD": "🏦 مالية",
    "SPGI": "🏦 مالية",
    "MCO": "🏦 مالية",
    "ICE": "🏦 مالية",
    "CME": "🏦 مالية",
    "NDAQ": "🏦 مالية",
    "CBOE": "🏦 مالية",
    "MSCI": "🏦 مالية",
    "FDS": "🏦 مالية",
    "USB": "🏦 مالية",
    "PNC": "🏦 مالية",
    "TFC": "🏦 مالية",
    "SCHW": "🏦 مالية",
    "BK": "🏦 مالية",
    "STT": "🏦 مالية",
    "TROW": "🏦 مالية",
    "BEN": "🏦 مالية",
    "IVZ": "🏦 مالية",
    "AMG": "🏦 مالية",
    "AMP": "🏦 مالية",
    "RJ": "🏦 مالية",
    "LPLA": "🏦 مالية",
    "SF": "🏦 مالية",
    "RJF": "🏦 مالية",
    "HLI": "🏦 مالية",
    "EVR": "🏦 مالية",
    "PIPR": "🏦 مالية",
    "MC": "🏦 مالية",
    "LAZ": "🏦 مالية",
    "ALL": "🏦 مالية",
    "TRV": "🏦 مالية",
    "PGR": "🏦 مالية",
    "CB": "🏦 مالية",
    "AIG": "🏦 مالية",
    "MET": "🏦 مالية",
    "PRU": "🏦 مالية",
    "AFL": "🏦 مالية",
    "HIG": "🏦 مالية",
    "CINF": "🏦 مالية",
    "L": "🏦 مالية",
    "WRB": "🏦 مالية",
    "RE": "🏦 مالية",
    "ACGL": "🏦 مالية",
    "EG": "🏦 مالية",
    "RNR": "🏦 مالية",
    "GL": "🏦 مالية",
    "UNM": "🏦 مالية",
    "LNC": "🏦 مالية",
    "PFG": "🏦 مالية",
    "VOYA": "🏦 مالية",
    "EQH": "🏦 مالية",
    "AEL": "🏦 مالية",
    "FNF": "🏦 مالية",
    "FAF": "🏦 مالية",
    "ORI": "🏦 مالية",
    "THG": "🏦 مالية",
    "KNSL": "🏦 مالية",
    "ERIE": "🏦 مالية",
    "RLI": "🏦 مالية",
    "SIGI": "🏦 مالية",
    "PLMR": "🏦 مالية",
    "ROOT": "🏦 مالية",
    "UPST": "🏦 مالية",
    "AFRM": "🏦 مالية",
    "SOFI": "🏦 مالية",
    "LC": "🏦 مالية",
    "NU": "🏦 مالية",
    "MELI": "🏦 مالية",
    "FIS": "🏦 مالية",
    "FISV": "🏦 مالية",
    "GPN": "🏦 مالية",
    "JKHY": "🏦 مالية",
    "FLT": "🏦 مالية",
    "WEX": "🏦 مالية",
    "FOUR": "🏦 مالية",

    "JNJ": "🏥 صحة",
    "PFE": "🏥 صحة",
    "MRK": "🏥 صحة",
    "ABBV": "🏥 صحة",
    "LLY": "🏥 صحة",
    "BMY": "🏥 صحة",
    "AMGN": "🏥 صحة",
    "GILD": "🏥 صحة",
    "BIIB": "🏥 صحة",
    "VRTX": "🏥 صحة",
    "REGN": "🏥 صحة",
    "MRNA": "🏥 صحة",
    "TMO": "🏥 صحة",
    "DHR": "🏥 صحة",
    "ABT": "🏥 صحة",
    "MDT": "🏥 صحة",
    "SYK": "🏥 صحة",
    "BSX": "🏥 صحة",
    "ISRG": "🏥 صحة",
    "EW": "🏥 صحة",
    "DXCM": "🏥 صحة",
    "IDXX": "🏥 صحة",
    "BDX": "🏥 صحة",
    "ZBH": "🏥 صحة",
    "HOLX": "🏥 صحة",
    "ILMN": "🏥 صحة",
    "EXAS": "🏥 صحة",
    "ALGN": "🏥 صحة",
    "PODD": "🏥 صحة",
    "TDOC": "🏥 صحة",
    "VEEV": "🏥 صحة",
    "IQV": "🏥 صحة",
    "CRL": "🏥 صحة",
    "WAT": "🏥 صحة",
    "MTD": "🏥 صحة",
    "BIO": "🏥 صحة",
    "TECH": "🏥 صحة",
    "RMD": "🏥 صحة",
    "STE": "🏥 صحة",
    "BAX": "🏥 صحة",
    "TFX": "🏥 صحة",
    "COO": "🏥 صحة",
    "XRAY": "🏥 صحة",
    "HSIC": "🏥 صحة",
    "PDCO": "🏥 صحة",
    "MCK": "🏥 صحة",
    "CAH": "🏥 صحة",
    "COR": "🏥 صحة",
    "CVS": "🏥 صحة",
    "WBA": "🏥 صحة",
    "CI": "🏥 صحة",
    "ELV": "🏥 صحة",
    "HUM": "🏥 صحة",
    "CNC": "🏥 صحة",
    "MOH": "🏥 صحة",
    "UNH": "🏥 صحة",
    "DGX": "🏥 صحة",
    "LH": "🏥 صحة",
    "A": "🏥 صحة",
    "GEHC": "🏥 صحة",
    "SOLV": "🏥 صحة",
    "RPRX": "🏥 صحة",
    "INCY": "🏥 صحة",
    "ALNY": "🏥 صحة",
    "BMRN": "🏥 صحة",
    "EXEL": "🏥 صحة",
    "NBIX": "🏥 صحة",
    "UTHR": "🏥 صحة",
    "IONS": "🏥 صحة",
    "SRPT": "🏥 صحة",
    "RARE": "🏥 صحة",
    "FOLD": "🏥 صحة",
    "ARWR": "🏥 صحة",
    "BEAM": "🏥 صحة",
    "CRSP": "🏥 صحة",
    "EDIT": "🏥 صحة",
    "NTLA": "🏥 صحة",
    "VERV": "🏥 صحة",
    "RXRX": "🏥 صحة",
    "SDGR": "🏥 صحة",
    "CERT": "🏥 صحة",
    "DOCS": "🏥 صحة",
    "HIMS": "🏥 صحة",
    "OSCR": "🏥 صحة",
    "GH": "🏥 صحة",
    "NTRA": "🏥 صحة",
    "TXG": "🏥 صحة",
    "PACB": "🏥 صحة",
    "TWST": "🏥 صحة",

    "XOM": "⛽️ طاقة",
    "CVX": "⛽️ طاقة",
    "COP": "⛽️ طاقة",
    "EOG": "⛽️ طاقة",
    "PXD": "⛽️ طاقة",
    "DVN": "⛽️ طاقة",
    "MPC": "⛽️ طاقة",
    "VLO": "⛽️ طاقة",
    "PSX": "⛽️ طاقة",
    "HES": "⛽️ طاقة",
    "OXY": "⛽️ طاقة",
    "APA": "⛽️ طاقة",
    "FANG": "⛽️ طاقة",
    "HAL": "⛽️ طاقة",
    "SLB": "⛽️ طاقة",
    "BKR": "⛽️ طاقة",
    "WMB": "⛽️ طاقة",
    "KMI": "⛽️ طاقة",
    "OKE": "⛽️ طاقة",
    "TRGP": "⛽️ طاقة",
    "LNG": "⛽️ طاقة",
    "EQT": "⛽️ طاقة",
    "CTRA": "⛽️ طاقة",
    "MRO": "⛽️ طاقة",
    "PR": "⛽️ طاقة",
    "CHRD": "⛽️ طاقة",
    "MTDR": "⛽️ طاقة",
    "SM": "⛽️ طاقة",
    "RRC": "⛽️ طاقة",
    "AR": "⛽️ طاقة",
    "CNX": "⛽️ طاقة",
    "SWN": "⛽️ طاقة",
    "GPOR": "⛽️ طاقة",
    "CRK": "⛽️ طاقة",
    "NOG": "⛽️ طاقة",
    "VTLE": "⛽️ طاقة",
    "CIVI": "⛽️ طاقة",
    "MGY": "⛽️ طاقة",
    "CRC": "⛽️ طاقة",
    "BTU": "⛽️ طاقة",
    "ARCH": "⛽️ طاقة",
    "CEIX": "⛽️ طاقة",
    "HCC": "⛽️ طاقة",
    "AMR": "⛽️ طاقة",
    "METC": "⛽️ طاقة",
    "NR": "⛽️ طاقة",
    "WTI": "⛽️ طاقة",
    "HP": "⛽️ طاقة",
    "PTEN": "⛽️ طاقة",
    "NBR": "⛽️ طاقة",
    "RIG": "⛽️ طاقة",
    "VAL": "⛽️ طاقة",
    "NE": "⛽️ طاقة",
    "DO": "⛽️ طاقة",
    "BORR": "⛽️ طاقة",
    "SDRL": "⛽️ طاقة",
    "NOV": "⛽️ طاقة",
    "FTI": "⛽️ طاقة",
    "WHD": "⛽️ طاقة",
    "LBRT": "⛽️ طاقة",

    "WMT": "🛒 استهلاكي",
    "TGT": "🛒 استهلاكي",
    "COST": "🛒 استهلاكي",
    "KR": "🛒 استهلاكي",
    "DG": "🛒 استهلاكي",
    "DLTR": "🛒 استهلاكي",
    "MCD": "🛒 استهلاكي",
    "SBUX": "🛒 استهلاكي",
    "CMG": "🛒 استهلاكي",
    "YUM": "🛒 استهلاكي",
    "DPZ": "🛒 استهلاكي",
    "QSR": "🛒 استهلاكي",
    "NKE": "🛒 استهلاكي",
    "LULU": "🛒 استهلاكي",
    "UAA": "🛒 استهلاكي",
    "KO": "🛒 استهلاكي",
    "PEP": "🛒 استهلاكي",
    "PM": "🛒 استهلاكي",
    "MO": "🛒 استهلاكي",
    "STZ": "🛒 استهلاكي",
    "MNST": "🛒 استهلاكي",
    "CELH": "🛒 استهلاكي",
    "EL": "🛒 استهلاكي",
    "CL": "🛒 استهلاكي",
    "PG": "🛒 استهلاكي",
    "KMB": "🛒 استهلاكي",
    "GIS": "🛒 استهلاكي",
    "K": "🛒 استهلاكي",
    "CPB": "🛒 استهلاكي",
    "CAG": "🛒 استهلاكي",
    "SJM": "🛒 استهلاكي",
    "HSY": "🛒 استهلاكي",
    "MKC": "🛒 استهلاكي",
    "TSN": "🛒 استهلاكي",
    "HRL": "🛒 استهلاكي",
    "KHC": "🛒 استهلاكي",
    "MDLZ": "🛒 استهلاكي",
    "KDP": "🛒 استهلاكي",
    "CHD": "🛒 استهلاكي",
    "CLX": "🛒 استهلاكي",
    "SYY": "🛒 استهلاكي",
    "USFD": "🛒 استهلاكي",
    "PFGC": "🛒 استهلاكي",
    "BJ": "🛒 استهلاكي",
    "CASY": "🛒 استهلاكي",
    "ULTA": "🛒 استهلاكي",
    "BBY": "🛒 استهلاكي",
    "GPC": "🛒 استهلاكي",
    "AZO": "🛒 استهلاكي",
    "ORLY": "🛒 استهلاكي",
    "AAP": "🛒 استهلاكي",
    "TSCO": "🛒 استهلاكي",
    "DKS": "🛒 استهلاكي",
    "BURL": "🛒 استهلاكي",
    "ROST": "🛒 استهلاكي",
    "TJX": "🛒 استهلاكي",
    "GPS": "🛒 استهلاكي",
    "ANF": "🛒 استهلاكي",
    "AEO": "🛒 استهلاكي",
    "URBN": "🛒 استهلاكي",
    "FL": "🛒 استهلاكي",
    "SKX": "🛒 استهلاكي",
    "CROX": "🛒 استهلاكي",
    "DECK": "🛒 استهلاكي",
    "ONON": "🛒 استهلاكي",
    "BIRK": "🛒 استهلاكي",
    "VFC": "🛒 استهلاكي",
    "PVH": "🛒 استهلاكي",
    "RL": "🛒 استهلاكي",
    "TPR": "🛒 استهلاكي",
    "CPRI": "🛒 استهلاكي",
    "HBI": "🛒 استهلاكي",
    "LEVI": "🛒 استهلاكي",
    "COLM": "🛒 استهلاكي",
    "GIII": "🛒 استهلاكي",
    "CAL": "🛒 استهلاكي",
    "WWW": "🛒 استهلاكي",
    "SHOO": "🛒 استهلاكي",
    "BOOT": "🛒 استهلاكي",
    "VSCO": "🛒 استهلاكي",

    "BA": "🏭 صناعي",
    "LMT": "🏭 صناعي",
    "RTX": "🏭 صناعي",
    "NOC": "🏭 صناعي",
    "GD": "🏭 صناعي",
    "TDG": "🏭 صناعي",
    "HWM": "🏭 صناعي",
    "CAT": "🏭 صناعي",
    "DE": "🏭 صناعي",
    "EMR": "🏭 صناعي",
    "ETN": "🏭 صناعي",
    "PH": "🏭 صناعي",
    "ROK": "🏭 صناعي",
    "AME": "🏭 صناعي",
    "CARR": "🏭 صناعي",
    "TT": "🏭 صناعي",
    "UPS": "🏭 صناعي",
    "FDX": "🏭 صناعي",
    "DAL": "🏭 صناعي",
    "UAL": "🏭 صناعي",
    "AAL": "🏭 صناعي",
    "LUV": "🏭 صناعي",
    "GE": "🏭 صناعي",
    "HON": "🏭 صناعي",
    "MMM": "🏭 صناعي",
    "IR": "🏭 صناعي",
    "DOV": "🏭 صناعي",
    "XYL": "🏭 صناعي",
    "FTV": "🏭 صناعي",
    "IEX": "🏭 صناعي",
    "PNR": "🏭 صناعي",
    "WAB": "🏭 صناعي",
    "ALLE": "🏭 صناعي",
    "GNRC": "🏭 صناعي",
    "SWK": "🏭 صناعي",
    "SNA": "🏭 صناعي",
    "NDSN": "🏭 صناعي",
    "GGG": "🏭 صناعي",
    "LECO": "🏭 صناعي",
    "TTC": "🏭 صناعي",
    "ROL": "🏭 صناعي",
    "AOS": "🏭 صناعي",
    "BLDR": "🏭 صناعي",
    "OC": "🏭 صناعي",
    "MAS": "🏭 صناعي",
    "LII": "🏭 صناعي",
    "WMS": "🏭 صناعي",
    "TREX": "🏭 صناعي",
    "AAON": "🏭 صناعي",
    "JCI": "🏭 صناعي",
    "CSL": "🏭 صناعي",
    "MLM": "🏭 صناعي",
    "VMC": "🏭 صناعي",
    "SUM": "🏭 صناعي",
    "EXP": "🏭 صناعي",
    "CRH": "🏭 صناعي",
    "CX": "🏭 صناعي",
    "PKG": "🏭 صناعي",
    "IP": "🏭 صناعي",
    "SEE": "🏭 صناعي",
    "SON": "🏭 صناعي",
    "AVY": "🏭 صناعي",
    "CCK": "🏭 صناعي",
    "GEF": "🏭 صناعي",
    "SLGN": "🏭 صناعي",
    "ATR": "🏭 صناعي",
    "AMCR": "🏭 صناعي",
    "GPK": "🏭 صناعي",
    "BERY": "🏭 صناعي",
    "URI": "🏭 صناعي",
    "FAST": "🏭 صناعي",
    "GWW": "🏭 صناعي",
    "MSM": "🏭 صناعي",
    "WCC": "🏭 صناعي",
    "AIT": "🏭 صناعي",
    "DXPE": "🏭 صناعي",
    "WSO": "🏭 صناعي",
    "POOL": "🏭 صناعي",

    "AMT": "📡 اتصالات",
    "CCI": "📡 اتصالات",
    "EQIX": "📡 اتصالات",
    "T": "📡 اتصالات",
    "VZ": "📡 اتصالات",
    "TMUS": "📡 اتصالات",
    "CHTR": "📡 اتصالات",
    "CMCSA": "📡 اتصالات",
    "DIS": "📡 اتصالات",
    "NFLX": "📡 اتصالات",
    "PARA": "📡 اتصالات",
    "WBD": "📡 اتصالات",
    "FOXA": "📡 اتصالات",
    "FOX": "📡 اتصالات",
    "NYT": "📡 اتصالات",
    "NWSA": "📡 اتصالات",
    "NWS": "📡 اتصالات",
    "IPG": "📡 اتصالات",
    "OMC": "📡 اتصالات",
    "TTWO": "📡 اتصالات",
    "EA": "📡 اتصالات",
    "PLD": "🏢 عقارات",
    "O": "🏢 عقارات",
    "SPG": "🏢 عقارات",
    "AVB": "🏢 عقارات",
    "EQR": "🏢 عقارات",
    "DLR": "🏢 عقارات",
    "PSA": "🏢 عقارات",
    "WELL": "🏢 عقارات",
    "VICI": "🏢 عقارات",
    "EXR": "🏢 عقارات",
    "INVH": "🏢 عقارات",
    "MAA": "🏢 عقارات",
    "ESS": "🏢 عقارات",
    "UDR": "🏢 عقارات",
    "CPT": "🏢 عقارات",
    "ARE": "🏢 عقارات",
    "BXP": "🏢 عقارات",
    "VTR": "🏢 عقارات",
    "HST": "🏢 عقارات",
    "REG": "🏢 عقارات",
    "FRT": "🏢 عقارات",
    "KIM": "🏢 عقارات",
    "SLG": "🏢 عقارات",
    "DEI": "🏢 عقارات",
    "HIW": "🏢 عقارات",
    "CUZ": "🏢 عقارات",
    "NEE": "⚡️ مرافق",
    "DUK": "⚡️ مرافق",
    "SO": "⚡️ مرافق",
    "D": "⚡️ مرافق",
    "AEP": "⚡️ مرافق",
    "EXC": "⚡️ مرافق",
    "SRE": "⚡️ مرافق",
    "XEL": "⚡️ مرافق",
    "WEC": "⚡️ مرافق",
    "ES": "⚡️ مرافق",
    "ED": "⚡️ مرافق",
    "PEG": "⚡️ مرافق",
    "EIX": "⚡️ مرافق",
    "DTE": "⚡️ مرافق",
    "AEE": "⚡️ مرافق",
    "CMS": "⚡️ مرافق",
    "CNP": "⚡️ مرافق",
    "NI": "⚡️ مرافق",
    "LNT": "⚡️ مرافق",
    "EVRG": "⚡️ مرافق",
    "PNW": "⚡️ مرافق",
    "IDA": "⚡️ مرافق",
    "OGE": "⚡️ مرافق",
    "POR": "⚡️ مرافق",
    "BKH": "⚡️ مرافق",
    "NWE": "⚡️ مرافق",
    "AVA": "⚡️ مرافق",
    "MGEE": "⚡️ مرافق",
    "OTTR": "⚡️ مرافق",
    "ALE": "⚡️ مرافق",
    "PCG": "⚡️ مرافق",

    "SPY": "📊 مؤشر",
    "QQQ": "📊 مؤشر",
    "IWM": "📊 مؤشر",
    "DIA": "📊 مؤشر",
    "VTI": "📊 مؤشر",
    "XLK": "📊 مؤشر",
    "XLF": "📊 مؤشر",
    "XLE": "📊 مؤشر",
    "XLV": "📊 مؤشر",
    "XLI": "📊 مؤشر",
    "XLY": "📊 مؤشر",
    "XLP": "📊 مؤشر",
    "XLU": "📊 مؤشر",
    "XLB": "📊 مؤشر",
    "XLRE": "📊 مؤشر",
    "GLD": "📊 مؤشر",
    "SLV": "📊 مؤشر",
    "TLT": "📊 مؤشر",
    "HYG": "📊 مؤشر",
    "LQD": "📊 مؤشر",
    "IEF": "📊 مؤشر",
    "SHY": "📊 مؤشر",
    "AGG": "📊 مؤشر",
    "BND": "📊 مؤشر",
    "VNQ": "📊 مؤشر",
    "IYR": "📊 مؤشر",
    "XBI": "📊 مؤشر",
    "IBB": "📊 مؤشر",
    "SMH": "📊 مؤشر",
    "SOXX": "📊 مؤشر",
    "ARKK": "📊 مؤشر",
    "ARKG": "📊 مؤشر",
    "ARKW": "📊 مؤشر",
    "BOTZ": "📊 مؤشر",
    "ROBO": "📊 مؤشر",
    "HACK": "📊 مؤشر",
    "CIBR": "📊 مؤشر",
    "SKYY": "📊 مؤشر",
    "CLOU": "📊 مؤشر",
    "WCLD": "📊 مؤشر",
    "TAN": "📊 مؤشر",
    "ICLN": "📊 مؤشر",
    "QCLN": "📊 مؤشر",
    "PBW": "📊 مؤشر",
    "LIT": "📊 مؤشر",
    "REMX": "📊 مؤشر",
    "URA": "📊 مؤشر",
    "GDX": "📊 مؤشر",
    "GDXJ": "📊 مؤشر",
    "SIL": "📊 مؤشر",
    "COPX": "📊 مؤشر",
    "JJC": "📊 مؤشر",
    "USO": "📊 مؤشر",
    "UNG": "📊 مؤشر",
    "BNO": "📊 مؤشر",
}


# =========================================================
# 5) Telegram sender
# =========================================================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    for cid in CHAT_IDS:
        try:
            response = requests.post(
                url,
                data={
                    "chat_id": cid,
                    "text": msg,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=12,
            )

            if not response.ok:
                print(
                    f"❌ Telegram error [{cid}]: "
                    f"{response.status_code} - {response.text[:300]}"
                )

            time.sleep(0.35)

        except Exception as e:
            print(f"❌ خطأ تيليجرام: {e}")


# =========================================================
# 6) Data helpers
# =========================================================
def flatten_columns(df):
    if df is None or df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def download_raw(sym, interval, period):
    try:
        df = yf.download(
            sym,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df is None or df.empty:
            return None

        df = flatten_columns(df)
        df = df.dropna()

        return df

    except Exception as e:
        print(f"⚠️ فشل تحميل {sym} {interval}: {e}")
        return None


def build_4h(df_1h):
    if df_1h is None or df_1h.empty:
        return None

    df = df_1h.copy()

    try:
        if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
            df = df.tz_convert("America/New_York")

        ohlc = df.resample(
            "4h",
            origin="start_day",
            offset="9h30min",
            label="left",
            closed="left",
        ).agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        })

        counts = df["Open"].resample(
            "4h",
            origin="start_day",
            offset="9h30min",
            label="left",
            closed="left",
        ).count()

        ohlc["Count"] = counts
        ohlc = ohlc[ohlc["Count"] >= 3]
        ohlc.drop(columns=["Count"], inplace=True)
        ohlc = ohlc.dropna()

        return ohlc

    except Exception as e:
        print(f"⚠️ فشل بناء 4H: {e}")
        return None


def get_data(sym, tf_info):
    if tf_info.get("resample_4h"):
        df = download_raw(sym, "1h", tf_info["period"])
        return build_4h(df)

    return download_raw(sym, tf_info["interval"], tf_info["period"])


def get_pivot_high(highs, center, length):
    left = center - length
    right = center + length

    if left < 0 or right >= len(highs):
        return None

    window = highs[left:right + 1]
    center_value = highs[center]

    if center_value == np.max(window):
        return float(center_value)

    return None


def get_pivot_low(lows, center, length):
    left = center - length
    right = center + length

    if left < 0 or right >= len(lows):
        return None

    window = lows[left:right + 1]
    center_value = lows[center]

    if center_value == np.min(window):
        return float(center_value)

    return None


def remove_incomplete_last_bar(df, tf_key):
    if df is None or len(df) < 3:
        return df

    seconds_map = {
        "15m": 15 * 60,
        "30m": 30 * 60,
        "1h": 60 * 60,
        "4h": 4 * 60 * 60,
        "1d": 24 * 60 * 60,
        "1wk": 7 * 24 * 60 * 60,
    }

    timeframe_seconds = seconds_map.get(tf_key)
    if timeframe_seconds is None:
        return df

    try:
        last_timestamp = pd.Timestamp(df.index[-1])

        if last_timestamp.tzinfo is not None:
            now = pd.Timestamp.now(tz=last_timestamp.tz)
        else:
            now = pd.Timestamp.now()

        age = (now - last_timestamp).total_seconds()

        if age < timeframe_seconds * 0.95:
            return df.iloc[:-1].copy()

    except Exception:
        pass

    return df


# =========================================================
# 7) Pine-like role reversal engine
# =========================================================
def check_role_reversal(sym, sector, tf_key, tf_info):
    try:
        df = get_data(sym, tf_info)

        if df is None or len(df) < 50:
            return []

        df = remove_incomplete_last_bar(df, tf_key)

        if df is None or len(df) < 50:
            return []

        rules = ROLE_RULES[tf_key]

        pivot_minor = rules["pivot_minor"]
        pivot_major = rules["pivot_major"]
        prox_pct = rules["prox_pct"]
        pct_thresh = rules["pct_thresh"]
        min_bars = rules["min_bars"]
        retest_margin = rules["retest_margin"]
        min_bounce_pct = rules["min_bounce_pct"]

        opens = df["Open"].to_numpy(dtype=float)
        highs = df["High"].to_numpy(dtype=float)
        lows = df["Low"].to_numpy(dtype=float)
        closes = df["Close"].to_numpy(dtype=float)

        volumes = None
        if "Volume" in df.columns:
            volumes = df["Volume"].to_numpy(dtype=float)

        last_major_ph = None
        last_major_pl = None

        ph_state = 0
        curr_ph = None
        ph_broken = False
        bars_above_ph = 0

        pl_state = 0
        curr_pl = None
        pl_broken = False
        bars_below_pl = 0

        latest_signals = []
        start = max(pivot_major, pivot_minor) * 2 + 5

        for i in range(start, len(df)):
            major_ph_center = i - pivot_major
            minor_ph_center = i - pivot_minor
            major_pl_center = i - pivot_major
            minor_pl_center = i - pivot_minor

            maj_ph = get_pivot_high(highs, major_ph_center, pivot_major)
            min_ph = get_pivot_high(highs, minor_ph_center, pivot_minor)
            maj_pl = get_pivot_low(lows, major_pl_center, pivot_major)
            min_pl = get_pivot_low(lows, minor_pl_center, pivot_minor)

            if maj_ph is not None:
                last_major_ph = maj_ph

            if maj_pl is not None:
                last_major_pl = maj_pl

            # -------------------------------
            # New resistance / pivot high
            # -------------------------------
            setup_new_ph = False
            target_ph = None

            if maj_ph is not None:
                target_ph = maj_ph
                setup_new_ph = True
            elif min_ph is not None:
                if (
                    last_major_ph is not None
                    and last_major_ph != 0
                    and abs(min_ph - last_major_ph) / last_major_ph <= prox_pct / 100
                ):
                    target_ph = last_major_ph
                else:
                    target_ph = min_ph
                setup_new_ph = True

            if setup_new_ph:
                curr_ph = target_ph
                ph_state = 1
                ph_broken = False
                bars_above_ph = 0

            # -------------------------------
            # New support / pivot low
            # -------------------------------
            setup_new_pl = False
            target_pl = None

            if maj_pl is not None:
                target_pl = maj_pl
                setup_new_pl = True
            elif min_pl is not None:
                if (
                    last_major_pl is not None
                    and last_major_pl != 0
                    and abs(min_pl - last_major_pl) / last_major_pl <= prox_pct / 100
                ):
                    target_pl = last_major_pl
                else:
                    target_pl = min_pl
                setup_new_pl = True

            if setup_new_pl:
                curr_pl = target_pl
                pl_state = 1
                pl_broken = False
                bars_below_pl = 0

            # -------------------------------
            # BUY: break resistance, +3%, stay above, retest
            # -------------------------------
            buy_signal = False

            if ph_state > 0 and curr_ph is not None:
                if highs[i] >= curr_ph * (1 + pct_thresh / 100):
                    ph_broken = True

                if ph_state == 1:
                    if closes[i] > curr_ph:
                        ph_state = 2
                        bars_above_ph = 1

                elif ph_state == 2:
                    ph_retest_level = curr_ph * (1 + retest_margin / 100)

                    if lows[i] <= ph_retest_level:
                        if (
                            ph_broken
                            and bars_above_ph > min_bars
                            and closes[i] > opens[i]
                            and closes[i] > curr_ph
                            and (closes[i] - lows[i]) / lows[i] >= min_bounce_pct
                        ):
                            buy_signal = True

                        ph_state = 0
                    else:
                        bars_above_ph += 1

            # -------------------------------
            # SELL: break support, -3%, stay below, retest
            # -------------------------------
            sell_signal = False

            if pl_state > 0 and curr_pl is not None:
                if lows[i] <= curr_pl * (1 - pct_thresh / 100):
                    pl_broken = True

                if pl_state == 1:
                    if closes[i] < curr_pl:
                        pl_state = 2
                        bars_below_pl = 1

                elif pl_state == 2:
                    pl_retest_level = curr_pl * (1 - retest_margin / 100)

                    if highs[i] >= pl_retest_level:
                        if (
                            pl_broken
                            and bars_below_pl > min_bars
                            and closes[i] < opens[i]
                            and closes[i] < curr_pl
                            and (highs[i] - closes[i]) / highs[i] >= min_bounce_pct
                        ):
                            sell_signal = True

                        pl_state = 0
                    else:
                        bars_below_pl += 1

            # آخر شمعة فقط
            if i == len(df) - 1:
                volume_ratio = None

                if volumes is not None and len(volumes) >= 16:
                    avg_volume = np.mean(volumes[-16:-1])
                    if avg_volume > 0:
                        volume_ratio = volumes[-1] / avg_volume

                if buy_signal:
                    latest_signals.append({
                        "side": "BUY",
                        "level": curr_ph,
                        "current_price": closes[i],
                        "bars_after": bars_above_ph,
                        "bar_time": df.index[i],
                        "volume_ratio": volume_ratio,
                    })

                if sell_signal:
                    latest_signals.append({
                        "side": "SELL",
                        "level": curr_pl,
                        "current_price": closes[i],
                        "bars_after": bars_below_pl,
                        "bar_time": df.index[i],
                        "volume_ratio": volume_ratio,
                    })

        return latest_signals

    except Exception as e:
        print(f"⚠️ خطأ في {sym}/{tf_key}: {e}")
        return []


# =========================================================
# 8) Telegram message
# =========================================================
def build_signal_message(sym, sector, tf_info, signal):
    side = signal["side"]

    if side == "BUY":
        emoji = "🟢"
        title = "تبادل أدوار - شراء"
        level_name = "المقاومة السابقة"
    else:
        emoji = "🔴"
        title = "تبادل أدوار - بيع"
        level_name = "الدعم السابق"

    volume_text = ""
    if signal["volume_ratio"] is not None:
        volume_text = f"\n📊 الحجم: x{signal['volume_ratio']:.1f}"

    return (
        f"{emoji} <b>{title}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<b>${sym}</b>  |  {sector}\n"
        f"📊 الفريم: <b>{tf_info['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📍 {level_name}: <b>${signal['level']:.2f}</b>\n"
        f"💰 السعر الحالي: <b>${signal['current_price']:.2f}</b>\n"
        f"⏱️ الشموع بعد الاختراق/الكسر: {signal['bars_after']}"
        f"{volume_text}\n"
        f"🕐 الشمعة: {signal['bar_time']}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ مطابق لشروط تبادل الأدوار في المؤشر"
    )


# =========================================================
# 9) Main scanner
# =========================================================
def check_all():
    print("\n" + "=" * 65)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    total_signals = 0

    for sym, sector in STOCKS.items():
        print(f"▶️ {sym}", end=" ")
        found = False

        for tf_key, tf_info in TIMEFRAMES.items():
            signals = check_role_reversal(sym, sector, tf_key, tf_info)

            for signal in signals:
                signal_time = signal["bar_time"]

                signal_key = (
                    f"{sym}|{tf_key}|{signal['side']}|{signal_time}"
                )

                if signal_key in sent_signals:
                    continue

                msg = build_signal_message(
                    sym,
                    sector,
                    tf_info,
                    signal,
                )

                send_telegram(msg)
                sent_signals.add(signal_key)
                total_signals += 1
                found = True

                print(
                    f"→ ✅ {signal['side']} {tf_info['name']}",
                    end=" "
                )
                time.sleep(0.5)

        if not found:
            print("→ لا شيء")
        else:
            print()

        time.sleep(0.25)

    print(f"\n✅ إجمالي الإشارات: {total_signals}")


# =========================================================
# 10) Run
# =========================================================
if __name__ == "__main__":
    print("🚀 بوت تبادل الأدوار - Telegram")
    print(f"عدد الأسهم: {len(STOCKS)}")
    print("الفريمات: 15م | 30م | 1س | 4س | يومي | أسبوعي")
    print("الشروط: Pivot 3/7 | قرب 1.5% | اختراق 3% | Retest 0.5% | Bounce 0.4%")

    check_all()

    # فحص كل 15 دقيقة حتى نلتقط إشارة آخر شمعة مكتملة.
    schedule.every(15).minutes.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(20)
