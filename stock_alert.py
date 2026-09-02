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

# الفريمات المطلوبة
TIMEFRAMES = {
    "30m": {"interval": "30m", "period": "60d",  "name": "30 دقيقة"},
    "1h":  {"interval": "1h",  "period": "90d",  "name": "ساعة"},
    "4h":  {"interval": "4h",  "period": "120d", "name": "4 ساعات"},
    "1d":  {"interval": "1d",  "period": "2y",   "name": "يومي"},
    "1wk": {"interval": "1wk", "period": "5y",   "name": "أسبوعي"},
}

# إعدادات تبادل الأدوار
SWING_LENGTH       = 4
MIN_BARS_AFTER     = 5
MAX_BARS_AFTER     = 40
MIN_MOVE_PCT       = 0.012
RETEST_TOLERANCE   = 0.009
MIN_BOUNCE_PCT     = 0.004

sent_signals = {}

# ==================== قائمة الأسهم (~700 سهم) ====================
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
    "GTLB":"💻 تكنولوجيا","AI":"💻 تكنولوجيا","BBAI":"💻 تكنولوجيا","SOUN":"💻 تكنولوجيا","SMCI":"💻 تكنولوجيا",
    "APPF":"💻 تكنولوجيا","ALRM":"💻 تكنولوجيا","DOCN":"💻 تكنولوجيا","FROG":"💻 تكنولوجيا","MNDY":"💻 تكنولوجيا",
    "GTLB":"💻 تكنولوجيا","S":"💻 تكنولوجيا","NET":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا","ZS":"💻 تكنولوجيا",
    "CRWD":"💻 تكنولوجيا","PANW":"💻 تكنولوجيا","FTNT":"💻 تكنولوجيا","OKTA":"💻 تكنولوجيا","CYBR":"💻 تكنولوجيا",
    "QLYS":"💻 تكنولوجيا","TENB":"💻 تكنولوجيا","RPD":"💻 تكنولوجيا","VRNS":"💻 تكنولوجيا","SAIL":"💻 تكنولوجيا",

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
    "AFRM":"🏦 مالية","SOFI":"🏦 مالية","LC":"🏦 مالية","NU":"🏦 مالية","MELI":"🏦 مالية","FIS":"🏦 مالية",
    "FISV":"🏦 مالية","GPN":"🏦 مالية","JKHY":"🏦 مالية","FLT":"🏦 مالية","WEX":"🏦 مالية","FOUR":"🏦 مالية",
    "TOST":"🏦 مالية","SQ":"🏦 مالية","PYPL":"🏦 مالية","V":"🏦 مالية","MA":"🏦 مالية","AXP":"🏦 مالية",

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
    "RXRX":"🏥 صحة","SDGR":"🏥 صحة","CERT":"🏥 صحة","DOCS":"🏥 صحة","HIMS":"🏥 صحة","OSCR":"🏥 صحة",
    "GH":"🏥 صحة","NTRA":"🏥 صحة","TXG":"🏥 صحة","PACB":"🏥 صحة","ILMN":"🏥 صحة","TWST":"🏥 صحة",

    # ===== طاقة =====
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة","PXD":"⛽ طاقة","DVN":"⛽ طاقة",
    "MPC":"⛽ طاقة","VLO":"⛽ طاقة","PSX":"⛽ طاقة","HES":"⛽ طاقة","OXY":"⛽ طاقة","APA":"⛽ طاقة",
    "FANG":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة","BKR":"⛽ طاقة","WMB":"⛽ طاقة","KMI":"⛽ طاقة",
    "OKE":"⛽ طاقة","TRGP":"⛽ طاقة","LNG":"⛽ طاقة","EQT":"⛽ طاقة","CTRA":"⛽ طاقة","MRO":"⛽ طاقة",
    "PR":"⛽ طاقة","CHRD":"⛽ طاقة","MTDR":"⛽ طاقة","SM":"⛽ طاقة","RRC":"⛽ طاقة","AR":"⛽ طاقة",
    "CNX":"⛽ طاقة","SWN":"⛽ طاقة","GPOR":"⛽ طاقة","CRK":"⛽ طاقة","NOG":"⛽ طاقة","VTLE":"⛽ طاقة",
    "CIVI":"⛽ طاقة","MGY":"⛽ طاقة","CRC":"⛽ طاقة","BTU":"⛽ طاقة","ARCH":"⛽ طاقة","CEIX":"⛽ طاقة",
    "HCC":"⛽ طاقة","AMR":"⛽ طاقة","METC":"⛽ طاقة","NR":"⛽ طاقة","WTI":"⛽ طاقة","HP":"⛽ طاقة",
    "PTEN":"⛽ طاقة","NBR":"⛽ طاقة","RIG":"⛽ طاقة","VAL":"⛽ طاقة","NE":"⛽ طاقة","DO":"⛽ طاقة",
    "BORR":"⛽ طاقة","SDRL":"⛽ طاقة","NOV":"⛽ طاقة","FTI":"⛽ طاقة","WHD":"⛽ طاقة","LBRT":"⛽ طاقة",

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
    "CPRI":"🛒 استهلاكي","HBI":"🛒 استهلاكي","LEVI":"🛒 استهلاكي","COLM":"🛒 استهلاكي","GIII":"🛒 استهلاكي",
    "CAL":"🛒 استهلاكي","WWW":"🛒 استهلاكي","SHOO":"🛒 استهلاكي","BOOT":"🛒 استهلاكي","VSCO":"🛒 استهلاكي",

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
    "AMCR":"🏭 صناعي","GPK":"🏭 صناعي","BERY":"🏭 صناعي","URI":"🏭 صناعي","FAST":"🏭 صناعي","GWW":"🏭 صناعي",
    "MSM":"🏭 صناعي","WCC":"🏭 صناعي","AIT":"🏭 صناعي","DXPE":"🏭 صناعي","WSO":"🏭 صناعي","POOL":"🏭 صناعي",

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
    "OTTR":"⚡ مرافق","ALE":"⚡ مرافق","PCG":"⚡ مرافق","EIX":"⚡ مرافق","SRE":"⚡ مرافق",

    # ===== مؤشرات وETFs =====
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر","VTI":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","XLV":"📊 مؤشر","XLI":"📊 مؤشر",
    "XLY":"📊 مؤشر","XLP":"📊 مؤشر","XLU":"📊 مؤشر","XLB":"📊 مؤشر","XLRE":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","TLT":"📊 مؤشر","HYG":"📊 مؤشر","LQD":"📊 مؤشر",
    "IEF":"📊 مؤشر","SHY":"📊 مؤشر","AGG":"📊 مؤشر","BND":"📊 مؤشر","VNQ":"📊 مؤشر",
    "IYR":"📊 مؤشر","XBI":"📊 مؤشر","IBB":"📊 مؤشر","SMH":"📊 مؤشر","SOXX":"📊 مؤشر",
    "ARKK":"📊 مؤشر","ARKG":"📊 مؤشر","ARKW":"📊 مؤشر","BOTZ":"📊 مؤشر","ROBO":"📊 مؤشر",
    "HACK":"📊 مؤشر","CIBR":"📊 مؤشر","SKYY":"📊 مؤشر","CLOU":"📊 مؤشر","WCLD":"📊 مؤشر",
    "TAN":"📊 مؤشر","ICLN":"📊 مؤشر","QCLN":"📊 مؤشر","PBW":"📊 مؤشر","LIT":"📊 مؤشر",
    "REMX":"📊 مؤشر","URA":"📊 مؤشر","GDX":"📊 مؤشر","GDXJ":"📊 مؤشر","SIL":"📊 مؤشر",
    "COPX":"📊 مؤشر","JJC":"📊 مؤشر","USO":"📊 مؤشر","UNG":"📊 مؤشر","BNO":"📊 مؤشر",
}

# ==================== دوال مساعدة ====================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"}, timeout=12)
            time.sleep(0.35)
        except Exception as e:
            print(f"خطأ تيليجرام: {e}")

def get_data(sym, interval, period):
    try:
        df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df
    except:
        return None

def find_swings(highs, lows, length=4):
    n = len(highs)
    swing_highs = []
    for i in range(length, n - length):
        if highs[i] == max(highs[i-length : i+length+1]):
            swing_highs.append((i, highs[i]))
    return swing_highs

# ==================== معادلة تبادل الأدوار المحسّنة ====================
def check_role_reversal(sym, sector, tf_key, tf_info):
    try:
        df = get_data(sym, tf_info["interval"], tf_info["period"])
        if df is None or len(df) < 50:
            return None

        closes = df["Close"].values
        opens  = df["Open"].values
        highs  = df["High"].values
        lows   = df["Low"].values
        volumes = df["Volume"].values if "Volume" in df.columns else None

        swing_highs = find_swings(highs, lows, SWING_LENGTH)
        if len(swing_highs) < 2:
            return None

        current_idx = len(df) - 1

        for swing_idx, resistance in reversed(swing_highs[:-1]):
            if current_idx - swing_idx < MIN_BARS_AFTER + 3:
                continue

            break_idx = None
            for i in range(swing_idx + 1, current_idx - MIN_BARS_AFTER):
                if closes[i] > resistance * 1.002:
                    break_idx = i
                    break
            if break_idx is None:
                continue

            bars_after = current_idx - break_idx
            if bars_after < MIN_BARS_AFTER or bars_after > MAX_BARS_AFTER:
                continue

            max_price_after = max(highs[break_idx : current_idx+1])
            move_pct = (max_price_after - resistance) / resistance
            if move_pct < MIN_MOVE_PCT:
                continue

            mid_point = break_idx + (bars_after // 2)
            if mid_point < current_idx:
                mid_low = min(lows[break_idx : mid_point+1])
                if mid_low < resistance * 0.985:
                    continue

            current_low   = lows[current_idx]
            current_close = closes[current_idx]
            current_open  = opens[current_idx]

            near = (current_low <= resistance * (1 + RETEST_TOLERANCE) and 
                    current_low >= resistance * (1 - RETEST_TOLERANCE * 1.3))

            if not near:
                continue

            bullish = current_close > current_open
            closed_above = current_close > resistance
            bounce_from_low = (current_close - current_low) / current_low >= MIN_BOUNCE_PCT

            if bullish and closed_above and bounce_from_low:
                vol_text = ""
                if volumes is not None and len(volumes) > 15:
                    avg_vol = np.mean(volumes[-16:-1])
                    if avg_vol > 0:
                        ratio = volumes[-1] / avg_vol
                        vol_text = f" | الحجم x{ratio:.1f}"

                msg = (
                    f"🟢 <b>تبادل أدوار صحيح</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"<b>${sym}</b>  |  {sector}\n"
                    f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"📍 مقاومة سابقة: <b>${resistance:.2f}</b>\n"
                    f"📈 أعلى سعر بعد الاختراق: ${max_price_after:.2f} (+{move_pct*100:.1f}%)\n"
                    f"💰 السعر الحالي: <b>${current_close:.2f}</b>\n"
                    f"⏱ عدد الشموع بعد الاختراق: {bars_after}{vol_text}\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"✅ اختراق + مشي + رجوع تدريجي + ارتداد"
                )
                return msg

        return None
    except Exception as e:
        return None

# ==================== الفحص الرئيسي ====================
def check_all():
    print(f"\n{'='*55}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    total_signals = 0

    for sym, sector in STOCKS.items():
        print(f"▶ {sym}", end=" ")

        df_d = get_data(sym, "1d", "1y")
        if df_d is None or len(df_d) < 50:
            print("→ بيانات ناقصة")
            continue

        ma50 = df_d["Close"].rolling(50).mean().iloc[-1]
        if df_d["Close"].iloc[-1] < ma50 * 0.98:
            print("→ تحت MA50")
            continue

        found = False
        for tf_key, tf_info in TIMEFRAMES.items():
            key = f"{sym}_{tf_key}"
            if key in sent_signals and datetime.now() - sent_signals[key] < timedelta(hours=8):
                continue

            msg = check_role_reversal(sym, sector, tf_key, tf_info)
            if msg:
                send_telegram(msg)
                sent_signals[key] = datetime.now()
                print(f"→ ✅ إشارة على {tf_info['name']}")
                total_signals += 1
                found = True
                time.sleep(1.1)
                break

        if not found:
            print("→ لا شيء")

        time.sleep(0.35)

    summary = (
        f"🔍 <b>انتهى الفحص</b>\n"
        f"إشارات صحيحة: {total_signals}\n"
        f"⏱ {datetime.now().strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ إجمالي الإشارات: {total_signals}")

# ==================== التشغيل ====================
if __name__ == "__main__":
    print("🚀 بوت تبادل الأدوار - نسخة محسنة (متعدد الفريمات)")
    print(f"عدد الأسهم: {len(STOCKS)}")
    print("الفريمات: 30م | 1س | 4س | يومي | أسبوعي\n")

    check_all()
    schedule.every(90).minutes.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(50)
