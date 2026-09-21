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

# ==================== شروط Pine مضبوطة للإنتاج (بعد التشخيص) ====================
# نتيجة التشخيص على بيانات حقيقية: عتبة 3% الموحدة كانت تحجب ~95% من
# إعادات الاختبار على الإنتراداي (مثال: AAPL فريم الساعة: 25 إعادة اختبار
# كلها محجوبة، و0 إشارة في 630 شمعة). والسبب الثاني: تتبع أحدث قمة فقط
# يعني إعادة الاختبار تأتي بعد 1-3 شموع قبل أن يتكون أي دفع سعري.
# الإصلاح: عتبة اختراق لكل فريم حسب تذبذبه + مستويان كبيران ناضجان (7,7)
# + نافذة 5-40 شمعة بعد الاختراق (مثل البوت القديم الناجح).
P_PIVOT_MAJOR   = 7       # القمم/القيعان القوية فقط هي المستويات
P_PIVOT_MINOR   = 3       # محسوب لكن لا يستخدم كمستوى (يبقى للتوافق)
P_PROX_PCT      = 0.015   # (احتياطي) نسبة دمج الصغرى مع الكبرى
P_MIN_BARS      = 3       # حد Pine الأدنى للبقاء فوق/تحت (نستخدم >=4 إغلاقات)
PCT_TF  = {"30m": 0.008, "1h": 0.01, "4h": 0.015, "1d": 0.025, "1wk": 0.03}
RET_TF  = {"30m": 0.009, "1h": 0.009, "4h": 0.008, "1d": 0.006, "1wk": 0.005}
WIN_TF  = {"30m": 6, "1h": 4, "4h": 3, "1d": 2, "1wk": 2}  # نافذة الإشارة الطازجة (فحص كل 90د يفوت شموع 30m)
N_LVLS  = 2               # آخر مستويين كبيرين ناضجين (توازن: إشارات زينة بدون سبام)
MIN_BARS_AFTER = 5
MAX_BARS_AFTER = 40
MIN_CLOSE_ABOVE = 4       # أقل عدد إغلاقات فوق المقاومة (تحتها للدعم)
DEEP_GUARD = 0.015        # إلغاء لو انكسر السعر 1.5% عكس الاتجاه بعد الاختراق
MIN_BOUNCE = 0.003        # أقل ارتداد من اللو (للشراء) على شمعة الإشارة

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

# ==================== شروط Pine مضبوطة للإنتاج ====================
# الفكرة من مؤشرك: قمة/قاع قوي -> اختراق % -> ثبات -> إعادة اختبار + إغلاق مؤكد
#  شراء: قمة (7,7) -> إغلاق فوقها -> دفع كافٍ (للتحقق) -> >=4 إغلاقات فوق ->
#        لو يلمس القمة + إغلاق صاعد + ارتداد
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
    """شروط Pine مضبوطة للإنتاج. ترجع (signal_type, msg) أو (None, None).

    الفكرة من مؤشرك محفوظة: قمة/قاع قوي (7,7) -> اختراق % -> ثبات
    إغلاقات فوق المستوى -> إعادة اختبار بلمس المستوى + إغلاق صاعد.
    المضبوط بعد التشخيص على بيانات حقيقية:
    - عتبة الاختراق لكل فريم (3% مستحيلة على فريم الساعة للأسهم الكبيرة).
    - آخر مستويين ناضجين (القمة الأحدث بعمر <8 شموع تهدم الإشارة لأن
      إعادة اختبارها فورية قبل أي دفع سعري).
    - نافذة 5-40 شمعة بعد الاختراق + نافذة إشارة طازجة لكل فريم
      (فحص كل 90 دقيقة يفوت شموع 30m لو النافذة ضيقة).
    """
    try:
        df = get_data(sym, tf_info["interval"], tf_info["period"])
        if df is None or len(df) < 60:
            return None, None

        high_vals  = df["High"].values.astype(float)
        low_vals   = df["Low"].values.astype(float)
        close_vals = df["Close"].values.astype(float)
        open_vals  = df["Open"].values.astype(float)
        vols = df["Volume"].values if "Volume" in df.columns else None
        n = len(df)

        maj_ph, maj_pl, _, _ = _build_pivot_arrays(high_vals, low_vals)

        pct = PCT_TF.get(tf_key, 0.015)
        rm  = RET_TF.get(tf_key, 0.008)
        win = WIN_TF.get(tf_key, 3)

        best_buy = None   # (cur, level, bars_after, extreme)
        best_sell = None

        for cur in range(max(0, n - win), n):
            # ---- شراء: آخر N_LVLS قمم كبرى ناضجة (أقدم من 8 شموع) ----
            pivots = [i for i in range(cur) if not np.isnan(maj_ph[i]) and i < cur - 8][-N_LVLS:]
            for pi in pivots:
                lvl = float(maj_ph[pi])
                brk = -1
                lo = max(0, cur - 45)
                for i in range(lo, cur):
                    if close_vals[i] > lvl:
                        brk = i
                        break
                if brk < 0:
                    continue
                ba = cur - brk
                if ba < MIN_BARS_AFTER or ba > MAX_BARS_AFTER:
                    continue
                top = float(np.max(high_vals[brk:cur + 1]))
                if (top - lvl) / lvl < pct:
                    continue
                if sum(1 for i in range(brk, cur + 1) if close_vals[i] > lvl) < MIN_CLOSE_ABOVE:
                    continue
                if float(np.min(low_vals[brk:cur + 1])) < lvl * (1 - DEEP_GUARD):
                    continue
                if (low_vals[cur] <= lvl * (1 + rm)
                        and close_vals[cur] > lvl
                        and close_vals[cur] > open_vals[cur]
                        and (close_vals[cur] - low_vals[cur]) / low_vals[cur] >= MIN_BOUNCE):
                    best_buy = (cur, lvl, ba, top)
                    break

            # ---- بيع (عكس الشراء على القيعان الكبرى) ----
            pivots_s = [i for i in range(cur) if not np.isnan(maj_pl[i]) and i < cur - 8][-N_LVLS:]
            for pi in pivots_s:
                lvl = float(maj_pl[pi])
                brk = -1
                lo = max(0, cur - 45)
                for i in range(lo, cur):
                    if close_vals[i] < lvl:
                        brk = i
                        break
                if brk < 0:
                    continue
                ba = cur - brk
                if ba < MIN_BARS_AFTER or ba > MAX_BARS_AFTER:
                    continue
                bot = float(np.min(low_vals[brk:cur + 1]))
                if (lvl - bot) / lvl < pct:
                    continue
                if sum(1 for i in range(brk, cur + 1) if close_vals[i] < lvl) < MIN_CLOSE_ABOVE:
                    continue
                if float(np.max(high_vals[brk:cur + 1])) > lvl * (1 + DEEP_GUARD):
                    continue
                if (high_vals[cur] >= lvl * (1 - rm)
                        and close_vals[cur] < lvl
                        and close_vals[cur] < open_vals[cur]):
                    best_sell = (cur, lvl, ba, bot)
                    break

        if best_buy is None and best_sell is None:
            return None, None
        if best_buy is not None and best_sell is not None:
            sig_type = "buy" if best_buy[0] >= best_sell[0] else "sell"
        elif best_buy is not None:
            sig_type = "buy"
        else:
            sig_type = "sell"

        cur_close = float(close_vals[n - 1])
        vol_text = ""
        if vols is not None and len(vols) > 15:
            try:
                avg = float(np.mean(vols[-16:-1]))
                if avg > 0:
                    vol_text = f" | الحجم x{float(vols[-1]) / avg:.1f}"
            except Exception:
                pass

        if sig_type == "buy":
            _, lvl, bars, top = best_buy
            move = (top - lvl) / lvl * 100 if lvl else 0
            msg = (
                f"🟢 <b>تبادل أدوار شراء (Pine)</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 القمة المخترقة: <b>${lvl:.2f}</b>\n"
                f"📈 أعلى بعد الاختراق: ${top:.2f} (+{move:.1f}% / شرط +{pct * 100:.1f}%)\n"
                f"⏱️ الشموع بعد الاختراق: {bars}\n"
                f"💰 السعر الحالي: <b>${cur_close:.2f}</b> (إعادة اختبار {rm * 100:.1f}%){vol_text}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ اختراق + ثبات إغلاقات + لمس القمة + إغلاق صاعد"
            )
            return "buy", msg
        else:
            _, lvl, bars, bot = best_sell
            move = (lvl - bot) / lvl * 100 if lvl else 0
            msg = (
                f"🔴 <b>تبادل أدوار بيع (Pine)</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 القاع المكسور: <b>${lvl:.2f}</b>\n"
                f"📉 أدنى بعد الكسر: ${bot:.2f} (-{move:.1f}% / شرط -{pct * 100:.1f}%)\n"
                f"⏱️ الشموع بعد الكسر: {bars}\n"
                f"💰 السعر الحالي: <b>${cur_close:.2f}</b> (إعادة اختبار {rm * 100:.1f}%){vol_text}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ كسر + ثبات إغلاقات + لمس القاع + إغلاق هابط"
            )
            return "sell", msg

    except Exception:
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
    print("الشروط: قمة/قاع قوي (7,7) + اختراق لكل فريم (0.8%-3%) + ثبات + إعادة اختبار\n")

    check_all()
    schedule.every(90).minutes.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(50)
