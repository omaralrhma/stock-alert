import yfinance as yf
import requests
import schedule
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ==================== الإعدادات (نفس الربط القديم) ====================
TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

TIMEFRAMES = {
    "30m": {"interval": "30m", "period": "60d",  "name": "30 دقيقة"},
    "1h":  {"interval": "1h",  "period": "90d",  "name": "ساعة"},
    "4h":  {"interval": "4h",  "period": "120d", "name": "4 ساعات"},
    "1d":  {"interval": "1d",  "period": "2y",   "name": "يومي"},
    "1wk": {"interval": "1wk", "period": "5y",   "name": "أسبوعي"},
}

# ==================== شروط Pine المستبدلة (من مؤشرك) ====================
P_PIVOT_MINOR   = 3
P_PIVOT_MAJOR   = 7
P_PROX_PCT      = 0.015   # 1.5% دمج القمة الصغرى مع الكبرى
P_PCT_THRESH    = 0.03    # 3% اختراق / كسر مطلوب
P_MIN_BARS      = 3       # البقاء فوق / تحت
P_RETEST_MARGIN = 0.005   # 0.5% سماح إعادة الاختبار
P_LOOKBACK      = 500     # نحاكي ذاكرة Pine من آخر 500 شمعة فقط (كفاية + سرعة)
P_SIGNAL_WINDOW = 3       # نقبل إشارة ظهرت في آخر 3 شموع (عشان فحص 90 دقيقة ما يفوت 30m)

sent_signals = {}

# ==================== قائمة الأسهم (نفس القائمة القديمة) ====================
STOCKS = {
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
    "APPF":"💻 تكنولوجيا","ALRM":"💻 تكنولوجيا","DOCN":"💻 تكنولوجيا","FROG":"💻 تكنولوجيا","MNDY":"💻 تكنولوجيا",
    "CYBR":"💻 تكنولوجيا","QLYS":"💻 تكنولوجيا","TENB":"💻 تكنولوجيا","RPD":"💻 تكنولوجيا","VRNS":"💻 تكنولوجيا","SAIL":"💻 تكنولوجيا",
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية","WFC":"🏦 مالية","C":"🏦 مالية",
    "BLK":"🏦 مالية","AXP":"🏦 مالية","V":"🏦 مالية","MA":"🏦 مالية","COF":"🏦 مالية","DFS":"🏦 مالية",
    "PYPL":"🏦 مالية","SQ":"🏦 مالية","COIN":"🏦 مالية","HOOD":"🏦 مالية","SPGI":"🏦 مالية","MCO":"🏦 مالية",
    "ICE":"🏦 مالية","CME":"🏦 مالية","NDAQ":"🏦 مالية","CBOE":"🏦 مالية","MSCI":"🏦 مالية","FDS":"🏦 مالية",
    "USB":"🏦 مالية","PNC":"🏦 مالية","TFC":"🏦 مالية","SCHW":"🏦 مالية","BK":"🏦 مالية","STT":"🏦 مالية",
    "TROW":"🏦 مالية","BEN":"🏦 مالية","IVZ":"🏦 مالية","AMG":"🏦 مالية","AMP":"🏦 مالية",
    "LPLA":"🏦 مالية","SF":"🏦 مالية","RJF":"🏦 مالية","HLI":"🏦 مالية","EVR":"🏦 مالية","PIPR":"🏦 مالية",
    "MC":"🏦 مالية","LAZ":"🏦 مالية","ALL":"🏦 مالية","TRV":"🏦 مالية","PGR":"🏦 مالية","CB":"🏦 مالية",
    "AIG":"🏦 مالية","MET":"🏦 مالية","PRU":"🏦 مالية","AFL":"🏦 مالية","HIG":"🏦 مالية","CINF":"🏦 مالية",
    "L":"🏦 مالية","WRB":"🏦 مالية","RE":"🏦 مالية","ACGL":"🏦 مالية","EG":"🏦 مالية","RNR":"🏦 مالية",
    "GL":"🏦 مالية","UNM":"🏦 مالية","LNC":"🏦 مالية","PFG":"🏦 مالية","VOYA":"🏦 مالية","EQH":"🏦 مالية",
    "AEL":"🏦 مالية","FNF":"🏦 مالية","FAF":"🏦 مالية","ORI":"🏦 مالية","THG":"🏦 مالية","KNSL":"🏦 مالية",
    "ERIE":"🏦 مالية","RLI":"🏦 مالية","SIGI":"🏦 مالية","PLMR":"🏦 مالية","ROOT":"🏦 مالية","UPST":"🏦 مالية",
    "AFRM":"🏦 مالية","SOFI":"🏦 مالية","LC":"🏦 مالية","NU":"🏦 مالية","MELI":"🏦 مالية","FIS":"🏦 مالية",
    "FISV":"🏦 مالية","GPN":"🏦 مالية","JKHY":"🏦 مالية","FLT":"🏦 مالية","WEX":"🏦 مالية","FOUR":"🏦 مالية",
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
    "GH":"🏥 صحة","NTRA":"🏥 صحة","TXG":"🏥 صحة","PACB":"🏥 صحة","TWST":"🏥 صحة",
    "XOM":"⛽️ طاقة","CVX":"⛽️ طاقة","COP":"⛽️ طاقة","EOG":"⛽️ طاقة","PXD":"⛽️ طاقة","DVN":"⛽️ طاقة",
    "MPC":"⛽️ طاقة","VLO":"⛽️ طاقة","PSX":"⛽️ طاقة","HES":"⛽️ طاقة","OXY":"⛽️ طاقة","APA":"⛽️ طاقة",
    "FANG":"⛽️ طاقة","HAL":"⛽️ طاقة","SLB":"⛽️ طاقة","BKR":"⛽️ طاقة","WMB":"⛽️ طاقة","KMI":"⛽️ طاقة",
    "OKE":"⛽️ طاقة","TRGP":"⛽️ طاقة","LNG":"⛽️ طاقة","EQT":"⛽️ طاقة","CTRA":"⛽️ طاقة","MRO":"⛽️ طاقة",
    "PR":"⛽️ طاقة","CHRD":"⛽️ طاقة","MTDR":"⛽️ طاقة","SM":"⛽️ طاقة","RRC":"⛽️ طاقة","AR":"⛽️ طاقة",
    "CNX":"⛽️ طاقة","SWN":"⛽️ طاقة","GPOR":"⛽️ طاقة","CRK":"⛽️ طاقة","NOG":"⛽️ طاقة","VTLE":"⛽️ طاقة",
    "CIVI":"⛽️ طاقة","MGY":"⛽️ طاقة","CRC":"⛽️ طاقة","BTU":"⛽️ طاقة","ARCH":"⛽️ طاقة","CEIX":"⛽️ طاقة",
    "HCC":"⛽️ طاقة","AMR":"⛽️ طاقة","METC":"⛽️ طاقة","NR":"⛽️ طاقة","WTI":"⛽️ طاقة","HP":"⛽️ طاقة",
    "PTEN":"⛽️ طاقة","NBR":"⛽️ طاقة","RIG":"⛽️ طاقة","VAL":"⛽️ طاقة","NE":"⛽️ طاقة","DO":"⛽️ طاقة",
    "BORR":"⛽️ طاقة","SDRL":"⛽️ طاقة","NOV":"⛽️ طاقة","FTI":"⛽️ طاقة","WHD":"⛽️ طاقة","LBRT":"⛽️ طاقة",
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
    "AMT":"📡 اتصالات","CCI":"📡 اتصالات","EQIX":"📡 اتصالات","T":"📡 اتصالات","VZ":"📡 اتصالات",
    "TMUS":"📡 اتصالات","CHTR":"📡 اتصالات","CMCSA":"📡 اتصالات","DIS":"📡 اتصالات","NFLX":"📡 اتصالات",
    "PARA":"📡 اتصالات","WBD":"📡 اتصالات","FOXA":"📡 اتصالات","FOX":"📡 اتصالات","NYT":"📡 اتصالات",
    "NWSA":"📡 اتصالات","NWS":"📡 اتصالات","IPG":"📡 اتصالات","OMC":"📡 اتصالات","TTWO":"📡 اتصالات",
    "EA":"📡 اتصالات","PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات","AVB":"🏢 عقارات",
    "EQR":"🏢 عقارات","DLR":"🏢 عقارات","PSA":"🏢 عقارات","WELL":"🏢 عقارات","VICI":"🏢 عقارات",
    "EXR":"🏢 عقارات","INVH":"🏢 عقارات","MAA":"🏢 عقارات","ESS":"🏢 عقارات","UDR":"🏢 عقارات",
    "CPT":"🏢 عقارات","ARE":"🏢 عقارات","BXP":"🏢 عقارات","VTR":"🏢 عقارات","HST":"🏢 عقارات",
    "REG":"🏢 عقارات","FRT":"🏢 عقارات","KIM":"🏢 عقارات","SLG":"🏢 عقارات","DEI":"🏢 عقارات",
    "HIW":"🏢 عقارات","CUZ":"🏢 عقارات","NEE":"⚡️ مرافق","DUK":"⚡️ مرافق","SO":"⚡️ مرافق",
    "D":"⚡️ مرافق","AEP":"⚡️ مرافق","EXC":"⚡️ مرافق","SRE":"⚡️ مرافق","XEL":"⚡️ مرافق",
    "WEC":"⚡️ مرافق","ES":"⚡️ مرافق","ED":"⚡️ مرافق","PEG":"⚡️ مرافق","EIX":"⚡️ مرافق",
    "DTE":"⚡️ مرافق","AEE":"⚡️ مرافق","CMS":"⚡️ مرافق","CNP":"⚡️ مرافق","NI":"⚡️ مرافق",
    "LNT":"⚡️ مرافق","EVRG":"⚡️ مرافق","PNW":"⚡️ مرافق","IDA":"⚡️ مرافق","OGE":"⚡️ مرافق",
    "POR":"⚡️ مرافق","BKH":"⚡️ مرافق","NWE":"⚡️ مرافق","AVA":"⚡️ مرافق","MGEE":"⚡️ مرافق",
    "OTTR":"⚡️ مرافق","ALE":"⚡️ مرافق","PCG":"⚡️ مرافق",
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

# ==================== دوال مساعدة (نفسها) ====================
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
    except Exception:
        return None

# ==================== ترجمة مؤشر Pine إلى Python (استبدال كامل) ====================
# Pine الأصلي:
#  pivot_minor=3, pivot_major=7, prox=1.5%, pct=3%, min_bars=3, retest=0.5%
#  شراء: قمة -> إغلاق فوقها -> high يحقق +3% -> بقاء >3 شموع فوق -> low يلمس القمة +0.5%
#  بيع: عكسها على القيعان

def _build_pivot_arrays(high_vals, low_vals):
    n = len(high_vals)
    hs = pd.Series(high_vals)
    ls = pd.Series(low_vals)

    w_maj = P_PIVOT_MAJOR * 2 + 1   # 15
    w_min = P_PIVOT_MINOR * 2 + 1   # 7

    roll_max_maj = hs.rolling(w_maj, min_periods=w_maj).max().values
    roll_min_maj = ls.rolling(w_maj, min_periods=w_maj).min().values
    roll_max_min = hs.rolling(w_min, min_periods=w_min).max().values
    roll_min_min = ls.rolling(w_min, min_periods=w_min).min().values

    sh7 = np.full(n, np.nan); sh7[P_PIVOT_MAJOR:] = high_vals[:-P_PIVOT_MAJOR]
    sl7 = np.full(n, np.nan); sl7[P_PIVOT_MAJOR:] = low_vals[:-P_PIVOT_MAJOR]
    sh3 = np.full(n, np.nan); sh3[P_PIVOT_MINOR:] = high_vals[:-P_PIVOT_MINOR]
    sl3 = np.full(n, np.nan); sl3[P_PIVOT_MINOR:] = low_vals[:-P_PIVOT_MINOR]

    maj_ph = np.where(roll_max_maj == sh7, sh7, np.nan)
    maj_pl = np.where(roll_min_maj == sl7, sl7, np.nan)
    min_ph = np.where(roll_max_min == sh3, sh3, np.nan)
    min_pl = np.where(roll_min_min == sl3, sl3, np.nan)
    return maj_ph, maj_pl, min_ph, min_pl

def check_pine_reversal(sym, sector, tf_key, tf_info):
    """ترجمة حرفية لمنطق Pine. ترجع (signal_type, msg) أو (None, None)."""
    try:
        df = get_data(sym, tf_info["interval"], tf_info["period"])
        if df is None or len(df) < 60:
            return None, None

        high_vals  = df["High"].values.astype(float)
        low_vals   = df["Low"].values.astype(float)
        close_vals = df["Close"].values.astype(float)
        vols = df["Volume"].values if "Volume" in df.columns else None
        n = len(df)

        maj_ph, maj_pl, min_ph, min_pl = _build_pivot_arrays(high_vals, low_vals)

        start = max(0, n - P_LOOKBACK)

        # last_major قبل بداية المحاكاة (عشان الدمج)
        last_major_ph = np.nan
        last_major_pl = np.nan
        pre_ph = np.where(~np.isnan(maj_ph[:start]))[0] if start > 0 else np.array([], dtype=int)
        pre_pl = np.where(~np.isnan(maj_pl[:start]))[0] if start > 0 else np.array([], dtype=int)
        if len(pre_ph) > 0:
            last_major_ph = float(maj_ph[pre_ph[-1]])
        if len(pre_pl) > 0:
            last_major_pl = float(maj_pl[pre_pl[-1]])

        curr_ph = np.nan; ph_state = 0; ph_broken = False; bars_above = 0; ph_setup = -1
        curr_pl = np.nan; pl_state = 0; pl_broken = False; bars_below = 0; pl_setup = -1

        buy_idx = -1;  buy_info = None
        sell_idx = -1; sell_info = None

        for cur in range(start, n):
            # --- تحديث آخر قمة/قاع كبرى ---
            if not np.isnan(maj_ph[cur]):
                last_major_ph = float(maj_ph[cur])
            if not np.isnan(maj_pl[cur]):
                last_major_pl = float(maj_pl[cur])

            # --- setup القمم (شراء) : الكبرى أولاً ثم الصغرى مع الدمج ---
            if not np.isnan(maj_ph[cur]):
                curr_ph = float(maj_ph[cur]); ph_state = 1; ph_broken = False; bars_above = 0; ph_setup = cur
            elif not np.isnan(min_ph[cur]):
                mp = float(min_ph[cur])
                target = mp
                if not np.isnan(last_major_ph):
                    if abs(mp - last_major_ph) / last_major_ph <= P_PROX_PCT:
                        target = float(last_major_ph)
                curr_ph = target; ph_state = 1; ph_broken = False; bars_above = 0; ph_setup = cur

            # --- setup القيعان (بيع) ---
            if not np.isnan(maj_pl[cur]):
                curr_pl = float(maj_pl[cur]); pl_state = 1; pl_broken = False; bars_below = 0; pl_setup = cur
            elif not np.isnan(min_pl[cur]):
                mp = float(min_pl[cur])
                target = mp
                if not np.isnan(last_major_pl):
                    if abs(mp - last_major_pl) / last_major_pl <= P_PROX_PCT:
                        target = float(last_major_pl)
                curr_pl = target; pl_state = 1; pl_broken = False; bars_below = 0; pl_setup = cur

            # --- منطق الشراء (نفس Pine) ---
            if ph_state > 0 and not np.isnan(curr_ph):
                if high_vals[cur] >= curr_ph * (1 + P_PCT_THRESH):
                    ph_broken = True
                if ph_state == 1:
                    if close_vals[cur] > curr_ph:
                        ph_state = 2; bars_above = 1
                elif ph_state == 2:
                    retest = curr_ph * (1 + P_RETEST_MARGIN)
                    if low_vals[cur] <= retest:
                        if ph_broken and bars_above > P_MIN_BARS:
                            buy_idx = cur
                            seg_high = float(np.max(high_vals[ph_setup:cur+1])) if ph_setup >= 0 else float(high_vals[cur])
                            buy_info = dict(level=float(curr_ph), bars=int(bars_above), top=seg_high, setup=ph_setup)
                        ph_state = 0
                    else:
                        bars_above += 1

            # --- منطق البيع (عكس الشراء) ---
            if pl_state > 0 and not np.isnan(curr_pl):
                if low_vals[cur] <= curr_pl * (1 - P_PCT_THRESH):
                    pl_broken = True
                if pl_state == 1:
                    if close_vals[cur] < curr_pl:
                        pl_state = 2; bars_below = 1
                elif pl_state == 2:
                    retest = curr_pl * (1 - P_RETEST_MARGIN)
                    if high_vals[cur] >= retest:
                        if pl_broken and bars_below > P_MIN_BARS:
                            sell_idx = cur
                            seg_low = float(np.min(low_vals[pl_setup:cur+1])) if pl_setup >= 0 else float(low_vals[cur])
                            sell_info = dict(level=float(curr_pl), bars=int(bars_below), bottom=seg_low, setup=pl_setup)
                        pl_state = 0
                    else:
                        bars_below += 1

        # --- هل الإشارة على آخر الشموع؟ (نافذة 3 شموع عشان فحص 90د لا يفوت 30m) ---
        last = n - 1
        sig_type = None; sig_idx = -1; info = None
        # لو الاثنين حديثين نأخذ الأحدث
        buy_fresh = (buy_idx >= 0 and (last - buy_idx) < P_SIGNAL_WINDOW)
        sell_fresh = (sell_idx >= 0 and (last - sell_idx) < P_SIGNAL_WINDOW)
        if buy_fresh and sell_fresh:
            if buy_idx >= sell_idx:
                sig_type, sig_idx, info = "buy", buy_idx, buy_info
            else:
                sig_type, sig_idx, info = "sell", sell_idx, sell_info
        elif buy_fresh:
            sig_type, sig_idx, info = "buy", buy_idx, buy_info
        elif sell_fresh:
            sig_type, sig_idx, info = "sell", sell_idx, sell_info
        else:
            return None, None

        cur_close = float(close_vals[last])
        vol_text = ""
        if vols is not None and len(vols) > 15:
            try:
                avg = float(np.mean(vols[-16:-1]))
                if avg > 0:
                    vol_text = f" | الحجم x{float(vols[-1])/avg:.1f}"
            except Exception:
                pass

        if sig_type == "buy":
            lvl = info["level"]; bars = info["bars"]; top = info["top"]
            move = (top - lvl) / lvl * 100 if lvl else 0
            msg = (
                f"🟢 <b>تبادل أدوار شراء (Pine)</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 القمة المخترقة: <b>${lvl:.2f}</b>\n"
                f"📈 أعلى بعد الاختراق: ${top:.2f} (+{move:.1f}% / شرط +3%)\n"
                f"⏱️ البقاء فوق القمة: {bars} شموع (شرط &gt;3)\n"
                f"💰 السعر الحالي: <b>${cur_close:.2f}</b> (إعادة اختبار 0.5%){vol_text}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ إغلاق فوق + اختراق 3% + ثبات + لمس القمة"
            )
            return "buy", msg
        else:
            lvl = info["level"]; bars = info["bars"]; bot = info["bottom"]
            move = (lvl - bot) / lvl * 100 if lvl else 0
            msg = (
                f"🔴 <b>تبادل أدوار بيع (Pine)</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 القاع المكسور: <b>${lvl:.2f}</b>\n"
                f"📉 أدنى بعد الكسر: ${bot:.2f} (-{move:.1f}% / شرط -3%)\n"
                f"⏱️ البقاء تحت القاع: {bars} شموع (شرط &gt;3)\n"
                f"💰 السعر الحالي: <b>${cur_close:.2f}</b> (إعادة اختبار 0.5%){vol_text}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ إغلاق تحت + كسر 3% + ثبات + لمس القاع"
            )
            return "sell", msg

    except Exception as e:
        # print(f"{sym} pine err: {e}")
        return None, None

# ==================== الفحص الرئيسي (نفس الهيكل القديم) ====================
def check_all():
    print(f"\n{'='*55}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    total_buy = 0
    total_sell = 0

    for sym, sector in STOCKS.items():
        print(f"▶️ {sym}", end=" ")

        # فلتر MA50 للشراء فقط (البيع مسموح حتى تحت المتوسط)
        df_d = get_data(sym, "1d", "1y")
        if df_d is None or len(df_d) < 50:
            print("→ بيانات ناقصة")
            continue
        try:
            ma50 = float(df_d["Close"].rolling(50).mean().iloc[-1])
            last_d = float(df_d["Close"].iloc[-1])
            below_ma = last_d < ma50 * 0.98
        except Exception:
            below_ma = False

        found = False
        for tf_key, tf_info in TIMEFRAMES.items():
            # مفاتيح منفصلة شراء/بيع عشان ما يحجب أحدهما الآخر
            kb = f"{sym}_{tf_key}_BUY"
            ks = f"{sym}_{tf_key}_SELL"
            now = datetime.now()
            if kb in sent_signals and ks in sent_signals:
                if now - sent_signals[kb] < timedelta(hours=8) and now - sent_signals[ks] < timedelta(hours=8):
                    continue

            sig, msg = check_pine_reversal(sym, sector, tf_key, tf_info)
            if sig is None:
                continue

            if sig == "buy":
                if below_ma:
                    # نتجاهل الشراء تحت MA50 ونكمل فريم ثاني (البيع سيظهر لو موجود)
                    continue
                if kb in sent_signals and now - sent_signals[kb] < timedelta(hours=8):
                    continue
                send_telegram(msg)
                sent_signals[kb] = now
                print(f"→ ✅ شراء Pine على {tf_info['name']}")
                total_buy += 1
                found = True
                time.sleep(1.1)
                break
            else:  # sell — بدون فلتر MA50
                if ks in sent_signals and now - sent_signals[ks] < timedelta(hours=8):
                    continue
                send_telegram(msg)
                sent_signals[ks] = now
                print(f"→ 🔻 بيع Pine على {tf_info['name']}")
                total_sell += 1
                found = True
                time.sleep(1.1)
                break

        if not found:
            print("→ لا شيء")

        time.sleep(0.35)

    summary = (
        f"🔍 <b>انتهى الفحص (Pine)</b>\n"
        f"🟢 شراء: {total_buy} | 🔴 بيع: {total_sell}\n"
        f"⏱️ {datetime.now().strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ شراء: {total_buy} | بيع: {total_sell}")

# ==================== التشغيل ====================
if __name__ == "__main__":
    print("🚀 بوت تبادل الأدوار - نسخة Pine المستبدلة")
    print(f"عدد الأسهم: {len(STOCKS)}")
    print("الفريمات: 30م | 1س | 4س | يومي | أسبوعي")
    print("الشروط: قمة/قاع (3,7) + دمج 1.5% + اختراق 3% + ثبات >3 + retest 0.5%\n")

    check_all()
    schedule.every(90).minutes.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(50)
