import yfinance as yf
import requests
import schedule
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ==================== الإعدادات ====================
TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

STOCKS = {
    # ===== تكنولوجيا =====
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا","GOOGL":"💻 تكنولوجيا","GOOG":"💻 تكنولوجيا",
    "META":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا","TSLA":"💻 تكنولوجيا","AMD":"💻 تكنولوجيا","INTC":"💻 تكنولوجيا",
    "CRM":"💻 تكنولوجيا","ORCL":"💻 تكنولوجيا","ADBE":"💻 تكنولوجيا","QCOM":"💻 تكنولوجيا","AMAT":"💻 تكنولوجيا",
    "MU":"💻 تكنولوجيا","LRCX":"💻 تكنولوجيا","KLAC":"💻 تكنولوجيا","PANW":"💻 تكنولوجيا","CRWD":"💻 تكنولوجيا",
    "ZS":"💻 تكنولوجيا","FTNT":"💻 تكنولوجيا","NET":"💻 تكنولوجيا","SNOW":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا",
    "PLTR":"💻 تكنولوجيا","AVGO":"💻 تكنولوجيا","MRVL":"💻 تكنولوجيا","ARM":"💻 تكنولوجيا","NOW":"💻 تكنولوجيا",
    "SMCI":"💻 تكنولوجيا","TXN":"💻 تكنولوجيا","SNPS":"💻 تكنولوجيا","CDNS":"💻 تكنولوجيا","TEAM":"💻 تكنولوجيا",
    "MDB":"💻 تكنولوجيا","SHOP":"💻 تكنولوجيا","ADSK":"💻 تكنولوجيا","ANSS":"💻 تكنولوجيا","ROP":"💻 تكنولوجيا",
    "ENPH":"💻 تكنولوجيا","FSLR":"💻 تكنولوجيا","CSCO":"💻 تكنولوجيا","IBM":"💻 تكنولوجيا","INTU":"💻 تكنولوجيا",
    "ADI":"💻 تكنولوجيا","NXPI":"💻 تكنولوجيا","MCHP":"💻 تكنولوجيا","ON":"💻 تكنولوجيا","MPWR":"💻 تكنولوجيا",
    "KEYS":"💻 تكنولوجيا","TER":"💻 تكنولوجيا","SWKS":"💻 تكنولوجيا","QRVO":"💻 تكنولوجيا","WDC":"💻 تكنولوجيا",
    "STX":"💻 تكنولوجيا","NTAP":"💻 تكنولوجيا","HPQ":"💻 تكنولوجيا","DELL":"💻 تكنولوجيا","HPE":"💻 تكنولوجيا",
    "CDW":"💻 تكنولوجيا","CTSH":"💻 تكنولوجيا","IT":"💻 تكنولوجيا","ACN":"💻 تكنولوجيا","EPAM":"💻 تكنولوجيا",
    "GEN":"💻 تكنولوجيا","FFIV":"💻 تكنولوجيا","AKAM":"💻 تكنولوجيا","VRSN":"💻 تكنولوجيا","OKTA":"💻 تكنولوجيا",
    "PATH":"💻 تكنولوجيا","TOST":"💻 تكنولوجيا","U":"💻 تكنولوجيا","RBLX":"💻 تكنولوجيا","TTD":"💻 تكنولوجيا",
    "APP":"💻 تكنولوجيا","ZI":"💻 تكنولوجيا","HUBS":"💻 تكنولوجيا","WDAY":"💻 تكنولوجيا","PAYC":"💻 تكنولوجيا",
    "PCTY":"💻 تكنولوجيا","DOCU":"💻 تكنولوجيا","ZM":"💻 تكنولوجيا","DBX":"💻 تكنولوجيا","BOX":"💻 تكنولوجيا",
    "ESTC":"💻 تكنولوجيا","DT":"💻 تكنولوجيا","CFLT":"💻 تكنولوجيا","S":"💻 تكنولوجيا","CR":"💻 تكنولوجيا",
    "GTLB":"💻 تكنولوجيا","AI":"💻 تكنولوجيا","BBAI":"💻 تكنولوجيا","SOUN":"💻 تكنولوجيا",

    # ===== مالية =====
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية","WFC":"🏦 مالية","C":"🏦 مالية",
    "BLK":"🏦 مالية","AXP":"🏦 مالية","V":"🏦 مالية","MA":"🏦 مالية","COF":"🏦 مالية","DFS":"🏦 مالية",
    "PYPL":"🏦 مالية","SQ":"🏦 مالية","COIN":"🏦 مالية","HOOD":"🏦 مالية","SPGI":"🏦 مالية","MCO":"🏦 مالية",
    "ICE":"🏦 مالية","CME":"🏦 مالية","NDAQ":"🏦 مالية","CBOE":"🏦 مالية","MSCI":"🏦 مالية","FDS":"🏦 مالية",
    "USB":"🏦 مالية","PNC":"🏦 مالية","TFC":"🏦 مالية","SCHW":"🏦 مالية","BK":"🏦 مالية","STT":"🏦 مالية",
    "TROW":"🏦 مالية","BEN":"🏦 مالية","IVZ":"🏦 مالية","AMG":"🏦 مالية","AMP":"🏦 مالية","RJ":"🏦 مالية",
    "LPLA":"🏦 مالية","SF":"🏦 مالية","RJF":"🏦 مالية","HLI":"🏦 مالية","EVR":"🏦 مالية","PIPR":"🏦 مالية",
    "MC":"🏦 مالية","LAZ":"🏦 مالية","ALL":"🏦 مالية","TRV":"🏦 مالية","PGR":"🏦 مالية","CB":"🏦 مالية",
    "AIG":"🏦 مالية","MET":"🏦 مالية","PRU":"🏦 مالية","AFL":"🏦 مالية","HIG":"🏦 مالية","CINF":"🏦 مالية",
    "L":"🏦 مالية","WRB":"🏦 مالية","RE":"🏦 مالية","ACGL":"🏦 مالية","EG":"🏦 مالية","RNR":"🏦 مالية",
    "GL":"🏦 مالية","UNM":"🏦 مالية","LNC":"🏦 مالية","PFG":"🏦 مالية","VOYA":"🏦 مالية","EQH":"🏦 مالية",
    "AEL":"🏦 مالية","FNF":"🏦 مالية","FAF":"🏦 مالية","ORI":"🏦 مالية","THG":"🏦 مالية","KNSL":"🏦 مالية",
    "ERIE":"🏦 مالية","RLI":"🏦 مالية","SIGI":"🏦 مالية","PLMR":"🏦 مالية","ROOT":"🏦 مالية","UPST":"🏦 مالية",
    "AFRM":"🏦 مالية","SOFI":"🏦 مالية","LC":"🏦 مالية","NU":"🏦 مالية","MELI":"🏦 مالية",

    # ===== صحة =====
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة","LLY":"🏥 صحة","BMY":"🏥 صحة",
    "AMGN":"🏥 صحة","GILD":"🏥 صحة","BIIB":"🏥 صحة","VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة",
    "TMO":"🏥 صحة","DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة","SYK":"🏥 صحة","BSX":"🏥 صحة",
    "ISRG":"🏥 صحة","EW":"🏥 صحة","DXCM":"🏥 صحة","IDXX":"🏥 صحة","BDX":"🏥 صحة","ZBH":"🏥 صحة",
    "HOLX":"🏥 صحة","ILMN":"🏥 صحة","EXAS":"🏥 صحة","ALGN":"🏥 صحة","PODD":"🏥 صحة","TDOC":"🏥 صحة",
    "VEEV":"🏥 صحة","IQV":"🏥 صحة","CRL":"🏥 صحة","WAT":"🏥 صحة","MTD":"🏥 صحة","BIO":"🏥 صحة",
    "TECH":"🏥 صحة","RMD":"🏥 صحة","STE":"🏥 صحة","BAX":"🏥 صحة","TFX":"🏥 صحة","COO":"🏥 صحة",
    "XRAY":"🏥 صحة","HSIC":"🏥 صحة","PDCO":"🏥 صحة","MCK":"🏥 صحة","CAH":"🏥 صحة","COR":"🏥 صحة",
    "CVS":"🏥 صحة","WBA":"🏥 صحة","CI":"🏥 صحة","ELV":"🏥 صحة","HUM":"🏥 صحة","CNC":"🏥 صحة",
    "MOH":"🏥 صحة","UNH":"🏥 صحة","DGX":"🏥 صحة","LH":"🏥 صحة","A":"🏥 صحة","GEHC":"🏥 صحة",
    "SOLV":"🏥 صحة","RPRX":"🏥 صحة","INCY":"🏥 صحة","ALNY":"🏥 صحة","BMRN":"🏥 صحة","EXEL":"🏥 صحة",
    "NBIX":"🏥 صحة","UTHR":"🏥 صحة","IONS":"🏥 صحة","SRPT":"🏥 صحة","RARE":"🏥 صحة","FOLD":"🏥 صحة",
    "ARWR":"🏥 صحة","BEAM":"🏥 صحة","CRSP":"🏥 صحة","EDIT":"🏥 صحة","NTLA":"🏥 صحة","VERV":"🏥 صحة",
    "RXRX":"🏥 صحة","SDGR":"🏥 صحة","CERT":"🏥 صحة","DOCS":"🏥 صحة",

    # ===== طاقة =====
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة","PXD":"⛽ طاقة","DVN":"⛽ طاقة",
    "MPC":"⛽ طاقة","VLO":"⛽ طاقة","PSX":"⛽ طاقة","HES":"⛽ طاقة","OXY":"⛽ طاقة","APA":"⛽ طاقة",
    "FANG":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة","BKR":"⛽ طاقة","WMB":"⛽ طاقة","KMI":"⛽ طاقة",
    "OKE":"⛽ طاقة","TRGP":"⛽ طاقة","LNG":"⛽ طاقة","EQT":"⛽ طاقة","CTRA":"⛽ طاقة","MRO":"⛽ طاقة",
    "PR":"⛽ طاقة","CHRD":"⛽ طاقة","MTDR":"⛽ طاقة","SM":"⛽ طاقة","RRC":"⛽ طاقة","AR":"⛽ طاقة",
    "CNX":"⛽ طاقة","SWN":"⛽ طاقة","GPOR":"⛽ طاقة","CRK":"⛽ طاقة","NOG":"⛽ طاقة","VTLE":"⛽ طاقة",
    "CIVI":"⛽ طاقة","MGY":"⛽ طاقة","CRC":"⛽ طاقة","BTU":"⛽ طاقة","ARCH":"⛽ طاقة","CEIX":"⛽ طاقة",
    "HCC":"⛽ طاقة","AMR":"⛽ طاقة","METC":"⛽ طاقة","NR":"⛽ طاقة","WTI":"⛽ طاقة",

    # ===== استهلاكي =====
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي","KR":"🛒 استهلاكي","DG":"🛒 استهلاكي",
    "DLTR":"🛒 استهلاكي","MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي","YUM":"🛒 استهلاكي",
    "DPZ":"🛒 استهلاكي","QSR":"🛒 استهلاكي","NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","UAA":"🛒 استهلاكي",
    "KO":"🛒 استهلاكي","PEP":"🛒 استهلاكي","PM":"🛒 استهلاكي","MO":"🛒 استهلاكي","STZ":"🛒 استهلاكي",
    "MNST":"🛒 استهلاكي","CELH":"🛒 استهلاكي","EL":"🛒 استهلاكي","CL":"🛒 استهلاكي","PG":"🛒 استهلاكي",
    "KMB":"🛒 استهلاكي","GIS":"🛒 استهلاكي","K":"🛒 استهلاكي","CPB":"🛒 استهلاكي","CAG":"🛒 استهلاكي",
    "SJM":"🛒 استهلاكي","HSY":"🛒 استهلاكي","MKC":"🛒 استهلاكي","TSN":"🛒 استهلاكي","HRL":"🛒 استهلاكي",
    "KHC":"🛒 استهلاكي","MDLZ":"🛒 استهلاكي","KDP":"🛒 استهلاكي","CHD":"🛒 استهلاكي","CLX":"🛒 استهلاكي",
    "SYY":"🛒 استهلاكي","USFD":"🛒 استهلاكي","PFGC":"🛒 استهلاكي","BJ":"🛒 استهلاكي","CASY":"🛒 استهلاكي",
    "ULTA":"🛒 استهلاكي","BBY":"🛒 استهلاكي","GPC":"🛒 استهلاكي","AZO":"🛒 استهلاكي","ORLY":"🛒 استهلاكي",
    "AAP":"🛒 استهلاكي","TSCO":"🛒 استهلاكي","DKS":"🛒 استهلاكي","BURL":"🛒 استهلاكي","ROST":"🛒 استهلاكي",
    "TJX":"🛒 استهلاكي","GPS":"🛒 استهلاكي","ANF":"🛒 استهلاكي","AEO":"🛒 استهلاكي","URBN":"🛒 استهلاكي",
    "FL":"🛒 استهلاكي","SKX":"🛒 استهلاكي","CROX":"🛒 استهلاكي","DECK":"🛒 استهلاكي","ONON":"🛒 استهلاكي",
    "BIRK":"🛒 استهلاكي","VFC":"🛒 استهلاكي","PVH":"🛒 استهلاكي","RL":"🛒 استهلاكي","TPR":"🛒 استهلاكي",
    "CPRI":"🛒 استهلاكي","HBI":"🛒 استهلاكي","LEVI":"🛒 استهلاكي",

    # ===== صناعي =====
    "BA":"🏭 صناعي","LMT":"🏭 صناعي","RTX":"🏭 صناعي","NOC":"🏭 صناعي","GD":"🏭 صناعي","TDG":"🏭 صناعي",
    "HWM":"🏭 صناعي","CAT":"🏭 صناعي","DE":"🏭 صناعي","EMR":"🏭 صناعي","ETN":"🏭 صناعي","PH":"🏭 صناعي",
    "ROK":"🏭 صناعي","AME":"🏭 صناعي","CARR":"🏭 صناعي","TT":"🏭 صناعي","UPS":"🏭 صناعي","FDX":"🏭 صناعي",
    "DAL":"🏭 صناعي","UAL":"🏭 صناعي","AAL":"🏭 صناعي","LUV":"🏭 صناعي","GE":"🏭 صناعي","HON":"🏭 صناعي",
    "MMM":"🏭 صناعي","IR":"🏭 صناعي","DOV":"🏭 صناعي","XYL":"🏭 صناعي","FTV":"🏭 صناعي","IEX":"🏭 صناعي",
    "PNR":"🏭 صناعي","WAB":"🏭 صناعي","ALLE":"🏭 صناعي","GNRC":"🏭 صناعي","SWK":"🏭 صناعي","SNA":"🏭 صناعي",
    "NDSN":"🏭 صناعي","GGG":"🏭 صناعي","LECO":"🏭 صناعي","TTC":"🏭 صناعي","ROL":"🏭 صناعي","AOS":"🏭 صناعي",
    "BLDR":"🏭 صناعي","OC":"🏭 صناعي","MAS":"🏭 صناعي","LII":"🏭 صناعي","WMS":"🏭 صناعي","TREX":"🏭 صناعي",
    "AAON":"🏭 صناعي","JCI":"🏭 صناعي","CSL":"🏭 صناعي","MLM":"🏭 صناعي","VMC":"🏭 صناعي","SUM":"🏭 صناعي",
    "EXP":"🏭 صناعي","CRH":"🏭 صناعي","CX":"🏭 صناعي","PKG":"🏭 صناعي","IP":"🏭 صناعي","SEE":"🏭 صناعي",
    "SON":"🏭 صناعي","AVY":"🏭 صناعي","CCK":"🏭 صناعي","GEF":"🏭 صناعي","SLGN":"🏭 صناعي","ATR":"🏭 صناعي",
    "AMCR":"🏭 صناعي","GPK":"🏭 صناعي","BERY":"🏭 صناعي",

    # ===== اتصالات وعقارات ومرافق =====
    "AMT":"📡 اتصالات","CCI":"📡 اتصالات","EQIX":"📡 اتصالات","T":"📡 اتصالات","VZ":"📡 اتصالات",
    "TMUS":"📡 اتصالات","CHTR":"📡 اتصالات","CMCSA":"📡 اتصالات","DIS":"📡 اتصالات","NFLX":"📡 اتصالات",
    "PARA":"📡 اتصالات","WBD":"📡 اتصالات","FOXA":"📡 اتصالات","FOX":"📡 اتصالات","NYT":"📡 اتصالات",
    "NWSA":"📡 اتصالات","NWS":"📡 اتصالات","IPG":"📡 اتصالات","OMC":"📡 اتصالات","TTWO":"📡 اتصالات",
    "EA":"📡 اتصالات","PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات","AVB":"🏢 عقارات",
    "EQR":"🏢 عقارات","DLR":"🏢 عقارات","PSA":"🏢 عقارات","WELL":"🏢 عقارات","VICI":"🏢 عقارات",
    "EXR":"🏢 عقارات","INVH":"🏢 عقارات","MAA":"🏢 عقارات","ESS":"🏢 عقارات","UDR":"🏢 عقارات",
    "CPT":"🏢 عقارات","ARE":"🏢 عقارات","BXP":"🏢 عقارات","VTR":"🏢 عقارات","HST":"🏢 عقارات",
    "REG":"🏢 عقارات","FRT":"🏢 عقارات","KIM":"🏢 عقارات","SLG":"🏢 عقارات","DEI":"🏢 عقارات",
    "HIW":"🏢 عقارات","CUZ":"🏢 عقارات","NEE":"⚡ مرافق","DUK":"⚡ مرافق","SO":"⚡ مرافق",
    "D":"⚡ مرافق","AEP":"⚡ مرافق","EXC":"⚡ مرافق","SRE":"⚡ مرافق","XEL":"⚡ مرافق",
    "WEC":"⚡ مرافق","ES":"⚡ مرافق","ED":"⚡ مرافق","PEG":"⚡ مرافق","EIX":"⚡ مرافق",
    "DTE":"⚡ مرافق","AEE":"⚡ مرافق","CMS":"⚡ مرافق","CNP":"⚡ مرافق","NI":"⚡ مرافق",
    "LNT":"⚡ مرافق","EVRG":"⚡ مرافق","PNW":"⚡ مرافق","IDA":"⚡ مرافق","OGE":"⚡ مرافق",
    "POR":"⚡ مرافق","BKH":"⚡ مرافق","NWE":"⚡ مرافق","AVA":"⚡ مرافق","MGEE":"⚡ مرافق",
    "OTTR":"⚡ مرافق","ALE":"⚡ مرافق",

    # ===== مؤشرات وETFs =====
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر","VTI":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","XLV":"📊 مؤشر","XLI":"📊 مؤشر",
    "XLY":"📊 مؤشر","XLP":"📊 مؤشر","XLU":"📊 مؤشر","XLB":"📊 مؤشر","XLRE":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","TLT":"📊 مؤشر","HYG":"📊 مؤشر","LQD":"📊 مؤشر",
    "IEF":"📊 مؤشر","SHY":"📊 مؤشر","AGG":"📊 مؤشر","BND":"📊 مؤشر","VNQ":"📊 مؤشر",
    "IYR":"📊 مؤشر","XBI":"📊 مؤشر","IBB":"📊 مؤشر","SMH":"📊 مؤشر","SOXX":"📊 مؤشر",
    "ARKK":"📊 مؤشر","ARKG":"📊 مؤشر","ARKW":"📊 مؤشر","BOTZ":"📊 مؤشر","ROBO":"📊 مؤشر",
    "HACK":"📊 مؤشر","CIBR":"📊 مؤشر","SKYY":"📊 مؤشر","CLOU":"📊 مؤشر","WCLD":"📊 مؤشر",
}

# ==================== إعدادات تبادل الأدوار ====================
SWING_LENGTH      = 5
RETEST_TOLERANCE  = 0.008
MIN_BARS_AFTER    = 3
MAX_BARS_AFTER    = 35
LOOKBACK_SWINGS   = 40

sent_signals = {}

# ==================== دوال مساعدة ====================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"}, timeout=10)
            time.sleep(0.4)
        except Exception as e:
            print(f"خطأ تيليجرام: {e}")

def get_data(sym, interval, period):
    try:
        df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df
    except Exception as e:
        print(f"  خطأ تحميل {sym} {interval}: {e}")
        return None

def find_swings(df, length=5):
    highs = df["High"].values
    lows  = df["Low"].values
    n = len(df)
    swing_highs = []
    swing_lows  = []
    for i in range(length, n - length):
        if highs[i] == max(highs[i-length:i+length+1]):
            swing_highs.append((i, highs[i]))
        if lows[i] == min(lows[i-length:i+length+1]):
            swing_lows.append((i, lows[i]))
    return swing_highs, swing_lows

# ==================== فلتر الاتجاه ====================
def is_trending_up(sym):
    try:
        df_d = get_data(sym, "1d", "8mo")
        if df_d is None or len(df_d) < 55:
            return False
        close_d = df_d["Close"].iloc[-1]
        ma50_d  = df_d["Close"].rolling(50).mean().iloc[-1]
        if close_d <= ma50_d:
            return False

        df_w = get_data(sym, "1wk", "2y")
        if df_w is None or len(df_w) < 25:
            return False
        close_w = df_w["Close"].iloc[-1]
        ma20_w  = df_w["Close"].rolling(20).mean().iloc[-1]
        if close_w <= ma20_w:
            return False

        return True
    except:
        return False

# ==================== معادلة تبادل الأدوار ====================
def check_role_reversal(sym, sector):
    try:
        df = get_data(sym, "4h", "90d")
        if df is None or len(df) < 60:
            return None

        closes = df["Close"].values
        opens  = df["Open"].values
        highs  = df["High"].values
        lows   = df["Low"].values
        volumes = df["Volume"].values if "Volume" in df.columns else None

        swing_highs, _ = find_swings(df, SWING_LENGTH)
        if not swing_highs:
            return None

        current_idx = len(df) - 1
        recent_highs = [sh for sh in swing_highs if sh[0] < current_idx - MIN_BARS_AFTER]
        if not recent_highs:
            return None

        last_swing_idx, resistance = recent_highs[-1]

        broken = False
        break_idx = None
        for i in range(last_swing_idx + 1, current_idx):
            if closes[i] > resistance:
                broken = True
                break_idx = i
                break

        if not broken or break_idx is None:
            return None

        bars_since_break = current_idx - break_idx
        if bars_since_break < MIN_BARS_AFTER or bars_since_break > MAX_BARS_AFTER:
            return None

        current_low   = lows[current_idx]
        current_close = closes[current_idx]
        current_open  = opens[current_idx]
        prev_close    = closes[current_idx - 1]

        near_level = abs(current_low - resistance) / resistance <= RETEST_TOLERANCE or \
                     (current_low <= resistance * (1 + RETEST_TOLERANCE) and current_close > resistance)

        bullish_rejection = current_close > current_open and current_close > resistance
        prev_near = prev_close <= resistance * (1 + RETEST_TOLERANCE * 1.5)

        if near_level and bullish_rejection and prev_near:
            vol_label = "عادي"
            vol_ratio = 1.0
            if volumes is not None and len(volumes) > 20:
                avg_vol = np.mean(volumes[-21:-1])
                curr_vol = volumes[-1]
                if avg_vol > 0:
                    vol_ratio = curr_vol / avg_vol
                    vol_label = "🔺 عالي" if vol_ratio >= 1.5 else "عادي"

            bounce_pct = ((current_close - current_low) / current_low) * 100 if current_low > 0 else 0

            msg = (
                f"🟢 <b>تبادل أدوار إيجابي — ${sym}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🏷 {sector}\n"
                f"📊 الفريم: 4 ساعات\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ <b>فلتر الاتجاه الصاعد محقق</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔄 <b>تفاصيل الإشارة</b>\n"
                f"  • مقاومة سابقة: ${resistance:.2f}\n"
                f"  • تم اختراقها ثم إعادة اختبارها\n"
                f"  • السعر الحالي: ${current_close:.2f}\n"
                f"  • نسبة الارتداد: {bounce_pct:.1f}%\n"
                f"  • الحجم: {vol_label} (x{vol_ratio:.1f})\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 فرصة دخول مع الاتجاه (Role Reversal)"
            )
            return msg

        return None

    except Exception as e:
        print(f"    خطأ RR {sym}: {e}")
        return None

# ==================== الفحص الرئيسي ====================
def check_all():
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    total = 0
    checked = 0

    for sym, sector in STOCKS.items():
        try:
            print(f"  فحص {sym}...", end=" ")
            checked += 1

            if sym in sent_signals:
                last_time = sent_signals[sym]
                if datetime.now() - last_time < timedelta(hours=6):
                    print("↳ تم إرسالها مؤخرًا")
                    continue

            if not is_trending_up(sym):
                print("↳ اتجاه ❌")
                continue
            print("↳ اتجاه ✅", end=" ")

            msg = check_role_reversal(sym, sector)
            if msg:
                send_telegram(msg)
                sent_signals[sym] = datetime.now()
                print("→ إشارة ✅ أُرسلت")
                total += 1
                time.sleep(1.2)
            else:
                print("→ لا تبادل أدوار")

            time.sleep(0.45)

        except Exception as e:
            print(f"\n  ❌ {sym}: {e}")

    summary = (
        f"🔍 <b>انتهى الفحص</b>\n"
        f"الأسهم المفحوصة: {checked}\n"
        f"إشارات تبادل أدوار: {total}\n"
        f"⏱ {datetime.now().strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ إجمالي الإشارات: {total}")

# ==================== التشغيل ====================
if __name__ == "__main__":
    print("🚀 بوت تبادل الأدوار (Role Reversal) - Multi TF Filter")
    print(f"عدد الأسهم: {len(STOCKS)}")
    print("الفحص كل ساعة\n")

    check_all()
    schedule.every(1).hours.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(45)
