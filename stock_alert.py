import yfinance as yf
import requests
import time
import numpy as np
import pandas as pd
import os, sys, json, hashlib

# ── معلومات البوت — تُقرأ من Environment Variables إن وُجدت،
#    وإلا تُستخدم هذه القيم الافتراضية (بوت التلي وقروبات الإرسال)
TOKEN    = os.environ.get("TG_TOKEN",  "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4")
_chats   = os.environ.get("TG_CHATS", "615265045,7775490993,5574232437")
CHAT_IDS = [c.strip() for c in _chats.split(",") if c.strip()]
RUN_ONCE = "--once" in sys.argv

# ═══════════════════════════════════════════════
# شركات فردية ذات أوبشن — بلا مؤشرات أو صناديق
# ═══════════════════════════════════════════════
STOCKS = {
    "AAPL":"💻 تقنية","MSFT":"💻 تقنية","NVDA":"💻 تقنية","GOOGL":"💻 تقنية","AMZN":"💻 تقنية",
    "META":"💻 تقنية","TSLA":"💻 تقنية","AMD":"💻 تقنية","INTC":"💻 تقنية","AVGO":"💻 تقنية",
    "QCOM":"💻 تقنية","TXN":"💻 تقنية","AMAT":"💻 تقنية","MU":"💻 تقنية","LRCX":"💻 تقنية",
    "KLAC":"💻 تقنية","MRVL":"💻 تقنية","ARM":"💻 تقنية","SMCI":"💻 تقنية","DELL":"💻 تقنية",
    "HPQ":"💻 تقنية","IBM":"💻 تقنية","STX":"💻 تقنية","WDC":"💻 تقنية","NTAP":"💻 تقنية",
    "MCHP":"💻 أشباه موصلات","ON":"💻 أشباه موصلات","NXPI":"💻 أشباه موصلات","ADI":"💻 أشباه موصلات",
    "MPWR":"💻 أشباه موصلات","SWKS":"💻 أشباه موصلات","QRVO":"💻 أشباه موصلات","COHR":"💻 أشباه موصلات",
    "TER":"💻 أشباه موصلات","LSCC":"💻 أشباه موصلات","ENTG":"💻 أشباه موصلات","WOLF":"💻 أشباه موصلات",
    "CRDO":"💻 أشباه موصلات","ALAB":"💻 أشباه موصلات","SNDK":"💻 تخزين","PSTG":"💻 تخزين",
    "CRM":"💻 سحابة","ORCL":"💻 سحابة","ADBE":"💻 سحابة","NOW":"💻 سحابة","WDAY":"💻 سحابة",
    "VEEV":"💻 سحابة","HUBS":"💻 سحابة","PAYC":"💻 سحابة","ROP":"💻 سحابة","SNPS":"💻 سحابة",
    "CDNS":"💻 سحابة","PANW":"💻 أمن","CRWD":"💻 أمن","ZS":"💻 أمن","FTNT":"💻 أمن",
    "NET":"💻 أمن","OKTA":"💻 أمن","S":"💻 أمن","CYBR":"💻 أمن","GEN":"💻 أمن",
    "SHOP":"💻 نمو","PLTR":"💻 نمو","SNOW":"💻 نمو","DDOG":"💻 نمو","MDB":"💻 نمو",
    "TEAM":"💻 نمو","TWLO":"💻 نمو","ZM":"💻 نمو","DOCU":"💻 نمو","BOX":"💻 نمو",
    "BILL":"💻 نمو","TOST":"💻 نمو","APP":"💻 نمو","TTD":"💻 نمو","CFLT":"💻 نمو",
    "HOOD":"💻 نمو","RDDT":"💻 نمو","AFRM":"💻 نمو","SOFI":"💻 نمو","UPST":"💻 نمو",
    "PATH":"💻 برمجيات","ESTC":"💻 برمجيات","GTLB":"💻 برمجيات","PCOR":"💻 برمجيات","FIVN":"💻 برمجيات",
    "U":"💻 برمجيات","RBLX":"💻 إنترنت","PINS":"💻 إنترنت","IOT":"💻 إنترنت","CART":"💻 إنترنت",
    "UBER":"💻 إنترنت","DASH":"💻 إنترنت","LYFT":"💻 إنترنت","GRAB":"💻 إنترنت","MELI":"💻 إنترنت",
    "SE":"💻 إنترنت","NU":"💻 تقنية مالية","DUOL":"💻 إنترنت","CAVA":"💻 نمو","CELH":"💻 نمو",
    "AI":"🤖 ذكاء","SOUN":"🤖 ذكاء","IONQ":"🤖 كوانتم","RGTI":"🤖 كوانتم","QBTS":"🤖 كوانتم",
    "BBAI":"🤖 ذكاء","ACHR":"🚁 طيران","JOBY":"🚁 طيران","RKLB":"🚀 فضاء","LUNR":"🚀 فضاء",
    "TEM":"🤖 ذكاء","RBRK":"💻 أمن","MSTR":"🪙 كريبتو","COIN":"🪙 كريبتو","MARA":"🪙 تعدين",
    "RIOT":"🪙 تعدين","HUT":"🪙 تعدين","CLSK":"🪙 تعدين","BTDR":"🪙 تعدين","BTBT":"🪙 تعدين",
    "CORZ":"🪙 تعدين","IREN":"🪙 تعدين","CIFR":"🪙 تعدين","WULF":"🪙 تعدين",
    "JPM":"🏦 بنوك","BAC":"🏦 بنوك","WFC":"🏦 بنوك","C":"🏦 بنوك","GS":"🏦 بنوك",
    "MS":"🏦 بنوك","SCHW":"🏦 بنوك","BK":"🏦 بنوك","STT":"🏦 بنوك","USB":"🏦 بنوك",
    "PNC":"🏦 بنوك","TFC":"🏦 بنوك","RF":"🏦 بنوك","KEY":"🏦 بنوك","FITB":"🏦 بنوك",
    "AXP":"🏦 مدفوعات","V":"🏦 مدفوعات","MA":"🏦 مدفوعات","PYPL":"🏦 مدفوعات","COF":"🏦 مالية",
    "SPGI":"🏦 مالية","MCO":"🏦 مالية","MSCI":"🏦 مالية","ICE":"🏦 مالية","NDAQ":"🏦 مالية",
    "FDS":"🏦 مالية","CME":"🏦 مالية","BLK":"🏦 أصول","BX":"🏦 أصول","KKR":"🏦 أصول",
    "APO":"🏦 أصول","ARES":"🏦 أصول","TROW":"🏦 أصول","ALLY":"🏦 مالية","DFS":"🏦 مالية",
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة","LLY":"🏥 صحة",
    "BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة","VRTX":"🏥 صحة","REGN":"🏥 صحة",
    "MRNA":"🏥 صحة","TMO":"🏥 صحة","DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة",
    "ISRG":"🏥 صحة","DXCM":"🏥 صحة","BSX":"🏥 صحة","BIIB":"🏥 صحة","ILMN":"🏥 صحة",
    "HIMS":"🏥 صحة","INCY":"🏥 صحة","ALNY":"🏥 صحة","EXAS":"🏥 صحة","NTRA":"🏥 صحة",
    "HCA":"🏥 صحة","MOH":"🏥 صحة","UNH":"🏥 صحة","CI":"🏥 صحة","CVS":"🏥 صحة",
    "ELV":"🏥 صحة","HUM":"🏥 صحة","CNC":"🏥 صحة","MCK":"🏥 صحة","CAH":"🏥 صحة",
    "SYK":"🏥 أجهزة","EW":"🏥 أجهزة","ZBH":"🏥 أجهزة","HOLX":"🏥 أجهزة","RMD":"🏥 أجهزة",
    "PODD":"🏥 أجهزة","BMRN":"🧬 بيوتكنولوجيا","IONS":"🧬 بيوتكنولوجيا","NBIX":"🧬 بيوتكنولوجيا",
    "SAGE":"🧬 بيوتكنولوجيا","CRSP":"🧬 بيوتكنولوجيا","BEAM":"🧬 بيوتكنولوجيا","RXRX":"🧬 بيوتكنولوجيا",
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة","DVN":"⛽ طاقة",
    "MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة",
    "PSX":"⛽ طاقة","FANG":"⛽ طاقة","CTRA":"⛽ طاقة","SM":"⛽ طاقة","MTDR":"⛽ طاقة",
    "EQT":"⛽ غاز","WMB":"⛽ غاز","KMI":"⛽ غاز","OKE":"⛽ غاز","LNG":"⛽ غاز",
    "AR":"⛽ غاز","RRC":"⛽ غاز","PR":"⛽ طاقة","OVV":"⛽ طاقة","TALO":"⛽ طاقة",
    "BKR":"⛽ خدمات","NOV":"⛽ خدمات","HP":"⛽ خدمات","LBRT":"⛽ خدمات","FTI":"⛽ خدمات",
    "ENPH":"🌱 طاقة نظيفة","FSLR":"🌱 طاقة نظيفة","BE":"🌱 طاقة نظيفة","PLUG":"🌱 طاقة نظيفة","SEDG":"🌱 طاقة نظيفة",
    "CCJ":"☢️ يورانيوم","UEC":"☢️ يورانيوم","UUUU":"☢️ يورانيوم","LEU":"☢️ يورانيوم","OKLO":"☢️ طاقة نووية",
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي","HD":"🛒 استهلاكي","LOW":"🛒 استهلاكي",
    "MCD":"🛒 مطاعم","SBUX":"🛒 مطاعم","CMG":"🛒 مطاعم","NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي",
    "MNST":"🛒 استهلاكي","ROST":"🛒 استهلاكي","TJX":"🛒 استهلاكي","ULTA":"🛒 استهلاكي","ETSY":"🛒 استهلاكي",
    "ONON":"🛒 استهلاكي","SKX":"🛒 استهلاكي","DECK":"🛒 استهلاكي","RH":"🛒 استهلاكي","DKNG":"🛒 ترفيه",
    "BKNG":"🛒 سفر","ABNB":"🛒 سفر","EXPE":"🛒 سفر","MAR":"🛒 سفر","HLT":"🛒 سفر",
    "CCL":"🛒 سفر","RCL":"🛒 سفر","NCLH":"🛒 سفر","MGM":"🛒 ترفيه","KO":"🛒 استهلاكي",
    "PEP":"🛒 استهلاكي","PG":"🛒 استهلاكي","CL":"🛒 استهلاكي","KMB":"🛒 استهلاكي","GIS":"🛒 استهلاكي",
    "KHC":"🛒 استهلاكي","CAG":"🛒 استهلاكي","SJM":"🛒 استهلاكي","STZ":"🛒 مشروبات","TAP":"🛒 مشروبات",
    "BUD":"🛒 مشروبات","YUM":"🛒 مطاعم","WING":"🛒 مطاعم","DRI":"🛒 مطاعم","TXRH":"🛒 مطاعم",
    "BROS":"🛒 مطاعم","KR":"🛒 تجزئة","DG":"🛒 تجزئة","DLTR":"🛒 تجزئة","SFM":"🛒 تجزئة",
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 نقل","FDX":"🏭 نقل","HON":"🏭 صناعي",
    "GE":"🏭 صناعي","ETN":"🏭 صناعي","EMR":"🏭 صناعي","PWR":"🏭 صناعي","AXON":"🏭 صناعي",
    "DAL":"✈️ نقل","UAL":"✈️ نقل","AAL":"✈️ نقل","LUV":"✈️ نقل","ALK":"✈️ نقل",
    "BA":"✈️ طيران","LMT":"🛡️ دفاع","RTX":"🛡️ دفاع","NOC":"🛡️ دفاع","GD":"🛡️ دفاع",
    "HWM":"🏭 صناعي","URI":"🏭 صناعي","ROK":"🏭 صناعي","PCAR":"🏭 صناعي","CARR":"🏭 صناعي",
    "JCI":"🏭 صناعي","IR":"🏭 صناعي","PH":"🏭 صناعي","ITW":"🏭 صناعي","GWW":"🏭 صناعي",
    "WM":"🏭 خدمات","RSG":"🏭 خدمات","NSC":"🚂 نقل","CSX":"🚂 نقل","UNP":"🚂 نقل",
    "ODFL":"🚚 نقل","XPO":"🚚 نقل","JBHT":"🚚 نقل","CHRW":"🚚 نقل",
    "TMUS":"📡 اتصالات","T":"📡 اتصالات","VZ":"📡 اتصالات","CMCSA":"📡 ميديا","NFLX":"📡 ميديا",
    "DIS":"📡 ميديا","SPOT":"📡 ميديا","WBD":"📡 ميديا","TTWO":"🎮 ألعاب","EA":"🎮 ألعاب",
    "FOXA":"📡 ميديا","FOX":"📡 ميديا","CHTR":"📡 اتصالات","SIRI":"📡 اتصالات","LYV":"📡 ترفيه",
    "IMAX":"📡 ترفيه","AMC":"📡 ترفيه","GME":"🎮 ألعاب",
    "NEM":"⛏️ مواد","FCX":"⛏️ مواد","ALB":"⛏️ مواد","AA":"⛏️ مواد","CLF":"⛏️ مواد",
    "VALE":"⛏️ مواد","BHP":"⛏️ مواد","GOLD":"⛏️ مواد","KGC":"⛏️ مواد","WPM":"⛏️ مواد",
    "AEM":"⛏️ مواد","MP":"⛏️ مواد","NUE":"⛏️ صلب","STLD":"⛏️ صلب","CMC":"⛏️ صلب",
    "RS":"⛏️ صلب","TECK":"⛏️ معادن","SCCO":"⛏️ نحاس","RIO":"⛏️ معادن","MOS":"⛏️ أسمدة",
    "CF":"⛏️ أسمدة","FMC":"⛏️ كيماويات","IPI":"⛏️ أسمدة","CE":"⛏️ كيماويات","DOW":"⛏️ كيماويات",
    "NEE":"⚡ مرافق","DUK":"⚡ مرافق","SO":"⚡ مرافق","AEP":"⚡ مرافق","EXC":"⚡ مرافق",
    "SRE":"⚡ مرافق","XEL":"⚡ مرافق","EIX":"⚡ مرافق","PCG":"⚡ مرافق","CEG":"⚡ طاقة",
    "VST":"⚡ طاقة","NRG":"⚡ طاقة","AES":"⚡ مرافق","PLD":"🏢 عقارات","AMT":"🏢 عقارات",
    "EQIX":"🏢 عقارات","DLR":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات","VICI":"🏢 عقارات",
    "WELL":"🏢 عقارات","AVB":"🏢 عقارات","EQR":"🏢 عقارات","PSA":"🏢 عقارات","CCI":"🏢 عقارات",
    "SBAC":"🏢 عقارات","EXR":"🏢 عقارات","KIM":"🏢 عقارات","BXP":"🏢 عقارات",
    "BABA":"🌏 الصين","JD":"🌏 الصين","PDD":"🌏 الصين","BIDU":"🌏 الصين","NTES":"🌏 الصين",
    "YUMC":"🌏 الصين","BILI":"🌏 الصين","BEKE":"🌏 الصين","FUTU":"🌏 الصين","TIGR":"🌏 الصين",
    "TME":"🌏 الصين","LI":"🚗 سيارات","NIO":"🚗 سيارات","XPEV":"🚗 سيارات",
}

# ═══════════════════════════════════════════════
# شركات إضافية فردية ذات أوبشن — بلا مؤشرات أو صناديق
# ═══════════════════════════════════════════════
ADDITIONAL_STOCKS = {
    "ACN":"💻 خدمات تقنية","ADSK":"💻 برمجيات","ANET":"💻 شبكات","CSCO":"💻 شبكات","HPE":"💻 هاردوير",
    "JNPR":"💻 شبكات","NOK":"💻 اتصالات","ERIC":"💻 اتصالات","GLW":"💻 مكونات","ZBRA":"💻 هاردوير",
    "KEYS":"💻 قياس","TDY":"💻 تقنية","GRMN":"💻 أجهزة","LOGI":"💻 أجهزة","SMAR":"💻 برمجيات",
    "NICE":"💻 برمجيات","FROG":"💻 برمجيات","DOCN":"💻 سحابة","CVLT":"💻 أمن","PD":"💻 برمجيات",
    "DT":"💻 برمجيات","MANH":"💻 برمجيات","TYL":"💻 برمجيات","GLOB":"💻 خدمات تقنية","EPAM":"💻 خدمات تقنية",
    "FSLY":"💻 سحابة","BAND":"💻 اتصالات","ZI":"💻 برمجيات","ALKT":"💻 برمجيات","BMBL":"💻 إنترنت",
    "GFS":"💻 أشباه موصلات","TSM":"💻 أشباه موصلات","ASML":"💻 أشباه موصلات","UMC":"💻 أشباه موصلات",
    "HIMX":"💻 أشباه موصلات","SIMO":"💻 أشباه موصلات","LITE":"💻 أشباه موصلات","OLED":"💻 مكونات",
    "MACOM":"💻 أشباه موصلات","SLAB":"💻 أشباه موصلات","SITM":"💻 أشباه موصلات","CAMT":"💻 أشباه موصلات",
    "RMBS":"💻 أشباه موصلات","AMKR":"💻 أشباه موصلات","PLAB":"💻 أشباه موصلات","ACLS":"💻 أشباه موصلات",
    "VRT":"💻 مراكز بيانات","MOD":"💻 مراكز بيانات","AAOI":"💻 اتصالات","CIEN":"💻 شبكات","FN":"💻 مكونات",
    "VIAV":"💻 اتصالات","UI":"💻 شبكات","COMM":"💻 اتصالات","INOD":"💻 بيانات","SATS":"📡 أقمار",
    "BRK-B":"🏦 مالية","PGR":"🏦 تأمين","CB":"🏦 تأمين","ALL":"🏦 تأمين","AFL":"🏦 تأمين",
    "TRV":"🏦 تأمين","HIG":"🏦 تأمين","MET":"🏦 تأمين","PRU":"🏦 تأمين","AIG":"🏦 تأمين",
    "ACGL":"🏦 تأمين","CINF":"🏦 تأمين","RJF":"🏦 مالية","AMP":"🏦 أصول","BEN":"🏦 أصول",
    "IVZ":"🏦 أصول","SEIC":"🏦 أصول","MKTX":"🏦 مالية","CBOE":"🏦 بورصات","NAVI":"🏦 مالية",
    "ONE":"🏦 مالية","RKT":"🏦 تمويل","UWMC":"🏦 تمويل","PFSI":"🏦 تمويل","FIS":"🏦 مدفوعات",
    "FI":"🏦 مدفوعات","GPN":"🏦 مدفوعات","ADP":"🏦 خدمات","PAYX":"🏦 خدمات","INTU":"🏦 برمجيات",
    "FICO":"🏦 برمجيات","WU":"🏦 مدفوعات","EBAY":"🏦 تجارة",
    "MDLZ":"🛒 استهلاكي","HSY":"🛒 استهلاكي","KDP":"🛒 مشروبات","K":"🛒 استهلاكي","CPB":"🛒 استهلاكي",
    "HRL":"🛒 استهلاكي","TSN":"🛒 استهلاكي","SYY":"🛒 استهلاكي","MKC":"🛒 استهلاكي","CLX":"🛒 استهلاكي",
    "CHD":"🛒 استهلاكي","EL":"🛒 استهلاكي","COTY":"🛒 استهلاكي","PM":"🛒 استهلاكي","MO":"🛒 استهلاكي",
    "BTI":"🛒 استهلاكي","DEO":"🛒 مشروبات","SAM":"🛒 مشروبات","FIZZ":"🛒 مشروبات","BBY":"🛒 تجزئة",
    "WSM":"🛒 تجزئة","FIVE":"🛒 تجزئة","BURL":"🛒 تجزئة","ANF":"🛒 تجزئة","AEO":"🛒 تجزئة",
    "GPS":"🛒 تجزئة","URBN":"🛒 تجزئة","LEVI":"🛒 تجزئة","CROX":"🛒 تجزئة","CPRI":"🛒 تجزئة",
    "KSS":"🛒 تجزئة","M":"🛒 تجزئة","FL":"🛒 تجزئة","PLCE":"🛒 تجزئة","BKE":"🛒 تجزئة",
    "CHWY":"🛒 تجارة","CVNA":"🚗 تجارة","CAR":"🚗 تأجير","ORLY":"🚗 قطع","AZO":"🚗 قطع",
    "AAP":"🚗 قطع","LVS":"🛒 ترفيه","WYNN":"🛒 ترفيه","PENN":"🛒 ترفيه","CZR":"🛒 ترفيه",
    "TDG":"🛡️ طيران","HEI":"🛡️ طيران","LHX":"🛡️ دفاع","BWXT":"🛡️ دفاع","CW":"🛡️ دفاع",
    "TEX":"🏭 صناعي","AGCO":"🏭 صناعي","CNH":"🏭 صناعي","OSK":"🏭 صناعي","WAB":"🏭 صناعي",
    "FAST":"🏭 صناعي","MAS":"🏭 صناعي","SWK":"🏭 صناعي","KBR":"🏭 صناعي","J":"🏭 هندسة",
    "FLS":"🏭 صناعي","GNRC":"🏭 طاقة","HUBB":"🏭 صناعي","AYI":"🏭 صناعي","MLI":"🏭 صناعي",
    "GGG":"🏭 صناعي","WMS":"🏭 صناعي","SITE":"🏭 مواد","MTZ":"🏭 هندسة","DY":"🏭 هندسة",
    "TKR":"🏭 صناعي","ZIM":"🚢 شحن","FRO":"🚢 شحن","STNG":"🚢 شحن","GLNG":"🚢 شحن",
    "FLNG":"🚢 شحن","GSL":"🚢 شحن","SBLK":"🚢 شحن","MATX":"🚢 شحن","KEX":"🚢 شحن",
    "ARCB":"🚚 نقل","RXO":"🚚 نقل","SNDR":"🚚 نقل","KNX":"🚚 نقل","SAIA":"🚚 نقل",
    "BDX":"🏥 أجهزة","BAX":"🏥 أجهزة","WST":"🏥 أجهزة","RVTY":"🏥 أجهزة","STE":"🏥 أجهزة",
    "HSIC":"🏥 أجهزة","PEN":"🏥 أجهزة","GKOS":"🏥 أجهزة","MASI":"🏥 أجهزة","XRAY":"🏥 أجهزة",
    "EXEL":"🧬 بيوتكنولوجيا","UTHR":"🧬 بيوتكنولوجيا","RPRX":"🧬 بيوتكنولوجيا","SRPT":"🧬 بيوتكنولوجيا","RARE":"🧬 بيوتكنولوجيا",
    "VCYT":"🧬 بيوتكنولوجيا","GMED":"🏥 أجهزة","TNDM":"🏥 أجهزة","IRTC":"🏥 أجهزة","INSP":"🏥 أجهزة",
    "ALKS":"🧬 بيوتكنولوجيا","CYTK":"🧬 بيوتكنولوجيا","HALO":"🧬 بيوتكنولوجيا",
    "CIVI":"⛽ طاقة","CHRD":"⛽ طاقة","VNOM":"⛽ طاقة","CRC":"⛽ طاقة","PBF":"⛽ طاقة",
    "DK":"⛽ طاقة","WFRD":"⛽ خدمات","PTEN":"⛽ خدمات","NEX":"⛽ خدمات","RES":"⛽ خدمات",
    "OII":"⛽ خدمات","PUMP":"⛽ خدمات","TDW":"⛽ خدمات","ET":"⛽ غاز","EPD":"⛽ غاز",
    "MPLX":"⛽ غاز","WES":"⛽ غاز","HL":"⛏️ فضة","CDE":"⛏️ فضة","PAAS":"⛏️ فضة",
    "AG":"⛏️ فضة","NEXA":"⛏️ معادن","HBM":"⛏️ معادن","LXU":"⛏️ كيماويات","HUN":"⛏️ كيماويات",
    "OLN":"⛏️ كيماويات","EMN":"⛏️ كيماويات","LYB":"⛏️ كيماويات","PPG":"⛏️ كيماويات","SHW":"⛏️ كيماويات",
    "ATO":"⚡ مرافق","NI":"⚡ مرافق","DTE":"⚡ مرافق","ETR":"⚡ مرافق","FE":"⚡ مرافق",
    "CMS":"⚡ مرافق","PPL":"⚡ مرافق","LNT":"⚡ مرافق","EVRG":"⚡ مرافق","WEC":"⚡ مرافق",
    "AEE":"⚡ مرافق","PEG":"⚡ مرافق","ED":"⚡ مرافق","ES":"⚡ مرافق","AWK":"⚡ مرافق",
    "CNP":"⚡ مرافق","INVH":"🏢 عقارات","CUBE":"🏢 عقارات","REXR":"🏢 عقارات","UDR":"🏢 عقارات",
    "MAA":"🏢 عقارات","CPT":"🏢 عقارات","FRT":"🏢 عقارات","REG":"🏢 عقارات","ARE":"🏢 عقارات",
    "DOC":"🏢 عقارات","ESS":"🏢 عقارات","HST":"🏢 عقارات","KRG":"🏢 عقارات","NNN":"🏢 عقارات",
    "VTR":"🏢 عقارات","LUMN":"📡 اتصالات","ASTS":"📡 أقمار","IRDM":"📡 أقمار","VSAT":"📡 أقمار",
    "GSAT":"📡 أقمار","CMBM":"📡 اتصالات",
    "HOG":"🚗 سيارات","PTON":"🚗 تنقل","TM":"🚗 سيارات","HMC":"🚗 سيارات","STLA":"🚗 سيارات",
    "BWA":"🚗 قطع","DAN":"🚗 قطع","GT":"🚗 إطارات","MGA":"🚗 قطع","VC":"🚗 قطع",
    "ADNT":"🚗 قطع","BNTX":"🌏 بيوتكنولوجيا","NVO":"🌏 صحة","SAP":"🌏 برمجيات","RY":"🌏 بنوك",
    "TD":"🌏 بنوك","BNS":"🌏 بنوك","UBS":"🌏 بنوك","DB":"🌏 بنوك","ING":"🌏 بنوك",
    "LYG":"🌏 بنوك","BCS":"🌏 بنوك","SAN":"🌏 بنوك","IBN":"🌏 بنوك","HDB":"🌏 بنوك",
    "INFY":"🌏 تقنية","WIT":"🌏 تقنية","WNS":"🌏 خدمات","ZTO":"🌏 الصين","TAL":"🌏 الصين",
    "EDU":"🌏 الصين","TCOM":"🌏 الصين","WB":"🌏 الصين","QFIN":"🌏 الصين","VIPS":"🌏 الصين",
    "RLX":"🌏 الصين","MINISO":"🌏 الصين","YMM":"🌏 الصين","KC":"🌏 الصين",
}

STOCKS.update(ADDITIONAL_STOCKS)

# ═══════════════════════════════════════════════
# إرسال ومنع التكرار
# ═══════════════════════════════════════════════
SENT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sent_signals.json")

def load_sent():
    try:
        with open(SENT_FILE) as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_sent(s):
    try:
        with open(SENT_FILE, "w") as f:
            json.dump(list(s)[-500:], f)
    except Exception:
        pass

def sig_key(sym, direction, level, tf, touch_time):
    payload = f"{sym}_{direction}_{level:.4f}_{tf}_{touch_time}"
    return hashlib.md5(payload.encode()).hexdigest()[:16]

SENT = load_sent()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    delivered = False

    for cid in CHAT_IDS:
        try:
            response = requests.post(
                url,
                data={"chat_id": cid, "text": msg, "parse_mode": "HTML"},
                timeout=15,
             )
            response.raise_for_status()
            delivered = True
            time.sleep(0.3)
        except requests.RequestException as e:
            print(f"خطأ في إرسال تيليجرام إلى {cid}: {e}")

    return delivered

# ═══════════════════════════════════════════════
# جلب البيانات: شموع مكتملة فقط
#
# ملاحظة مهمة تم إصلاحها: yfinance لا يدعم فريم "4h" أصلاً
# (الفريمات المدعومة رسمياً: 1m,2m,5m,15m,30m,60m/1h,1d,5d,1wk,1mo,3mo).
# سابقاً كان طلب "4h" مباشرة من yfinance يفشل، وبما أنه يأتي قبل
# "1d" و"1wk" في ترتيب الفحص، كان الخطأ يوقف فحص بقية الفريمات
# (اليومي والأسبوعي) لكل سهم بالكامل — وهذا كان السبب الرئيسي
# لغياب أغلب الإشعارات. الحل: نبني فريم 4 ساعات يدوياً بتجميع
# (resample) بيانات الساعة الفعلية، ونتجاهل أي شمعة 4h غير مكتملة.
# ═══════════════════════════════════════════════
def _drop_unclosed_bar(df, interval):
    if df.empty:
        return df

    durations = {
        "15m": pd.Timedelta(minutes=15),
        "30m": pd.Timedelta(minutes=30),
        "1h": pd.Timedelta(hours=1),
        "4h": pd.Timedelta(hours=4),
        "1d": pd.Timedelta(days=1),
        "1wk": pd.Timedelta(days=7),
    }

    last_stamp = pd.Timestamp(df.index[-1])
    now = pd.Timestamp.now(tz="UTC")

    if last_stamp.tzinfo is None:
        now = now.tz_localize(None)
    else:
        now = now.tz_convert(last_stamp.tz)

    if now < last_stamp + durations.get(interval, pd.Timedelta(days=1)):
        return df.iloc[:-1].copy()

    return df

def get_data(symbol, interval):
    # ── فريم 4 ساعات: مُجمَّع يدوياً من بيانات الساعة (yfinance لا يدعمه مباشرة)
    if interval == "4h":
        base = get_data(symbol, "1h")
        if base.empty or len(base) < 4:
            return base

        agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
        df4h = base.resample("4h").agg(agg).dropna()

        # اقبل فقط الشموع المكتملة (تحتوي 4 شموع ساعة كاملة)
        counts = base["Close"].resample("4h").count()
        df4h = df4h[counts.reindex(df4h.index).fillna(0) >= 4]
        return df4h

    periods = {
        "15m": "60d", "30m": "60d",
        "1h": "730d",   # أقصى مدى تسمح به Yahoo لبيانات الساعة — يفيد فريم 1h و4h معاً
        "1d": "2y", "1wk": "5y",
    }

    df = yf.download(
        symbol,
        period=periods.get(interval, "1y"),
        interval=interval,
        progress=False,
        auto_adjust=True,
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna().sort_index()
    return _drop_unclosed_bar(df, interval)

# ═══════════════════════════════════════════════
# محرك لمس تبادل الأدوار — دون تأكيد شموع
# ═══════════════════════════════════════════════
def detect_role_reversal(df, tf):
    """يرسل عند لمس نقطة تبادل الأدوار بعد كسر مؤكد، دون انتظار شمعة تأكيد.

    صعود: مقاومة هيكلية → كسر فوقها → عودة ولمسها من الأعلى.
    هبوط: دعم هيكلي → كسر تحته → عودة ولمسه من الأسفل.
    """
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        return []

    closes = df["Close"].astype(float).to_numpy()
    opens = df["Open"].astype(float).to_numpy()
    highs = df["High"].astype(float).to_numpy()
    lows = df["Low"].astype(float).to_numpy()
    volumes = df["Volume"].astype(float).to_numpy()
    n = len(closes)

    pivot_side = 4
    structure_window = 35
    trend_bars = 20
    min_trend = 0.02
    min_pivot_to_breakout = 3
    min_retest_bars = 1
    max_retest_bars = 40
    volume_multiplier = 0.90
    stop_buffer = 0.005

    # يحتفظ بلمس حدث منذ آخر جولة فحص تقريبًا.
    recent_touch_bars = {"15 دقيقة": 4, "30 دقيقة": 2}.get(tf, 1)

    min_bars = max(pivot_side * 2, structure_window, trend_bars) + min_pivot_to_breakout + max_retest_bars
    if n < min_bars:
        return []

    true_range = np.empty(n)
    true_range[0] = highs[0] - lows[0]
    true_range[1:] = np.maximum.reduce([
        highs[1:] - lows[1:],
        np.abs(highs[1:] - closes[:-1]),
        np.abs(lows[1:] - closes[:-1]),
    ])
    atr = np.array([np.mean(true_range[max(0, i - 13):i + 1]) for i in range(n)])
    volume_ma = np.array([
        np.mean(volumes[max(0, i - 20):i]) if i >= 20 else np.mean(volumes[:i + 1])
        for i in range(n)
    ])

    def level_zone(price, i):
        return max(price * 0.0080, atr[i] * 0.65)

    def breakout_buffer(price, i):
        return max(price * 0.0025, atr[i] * 0.35)

    def touch_zone(price, i):
        return max(price * 0.0040, atr[i] * 0.40)

    def invalidation_buffer(price, i):
        return max(price * 0.0100, atr[i] * 1.00)

    def volume_ok(i):
        return volume_ma[i] <= 0 or volumes[i] >= volume_multiplier * volume_ma[i]

    def make_signal(direction, level, pivot_i, breakout_i, touch_i, extreme):
        entry = closes[touch_i]

        if direction == "bull":
            stop = extreme * (1 - stop_buffer)
            risk = entry - stop
            target1, target2 = entry + 2 * risk, entry + 3 * risk
        else:
            stop = extreme * (1 + stop_buffer)
            risk = stop - entry
            target1, target2 = entry - 2 * risk, entry - 3 * risk

        if risk <= 0:
            return None

        return {
            "direction": direction,
            "level": level,
            "pattern": "لمس نقطة تبادل الأدوار — دون تأكيد شمعة",
            "valley_drop": abs(level - extreme) / level * 100,
            "uptrend_gain": abs(level - closes[pivot_i - trend_bars]) / closes[pivot_i - trend_bars] * 100,
            "breakout_price": closes[breakout_i],
            "retest_price": entry,
            "current_price": entry,
            "dist_pct": abs(entry - level) / level * 100,
            "tf": tf,
            "gap_bars": breakout_i - pivot_i,
            "stop": stop,
            "target1": target1,
            "target2": target2,
            "confirm_time": str(df.index[touch_i]),
        }

    results = []
    first_pivot = max(pivot_side, structure_window, trend_bars)
    last_pivot = n - pivot_side - min_pivot_to_breakout - min_retest_bars - 1

    # مقاومة صارت دعمًا.
    for pivot_i in range(first_pivot, last_pivot):
        level = highs[pivot_i]
        zone = level_zone(level, pivot_i)
        prior_highs = highs[max(0, pivot_i - structure_window):pivot_i]
        prior_touches = np.where(np.abs(prior_highs - level) <= zone)[0]
        has_prior_touch = any(
            pivot_i - (max(0, pivot_i - structure_window) + p) >= pivot_side * 2
            for p in prior_touches
        )
        if not has_prior_touch:
            continue
        if level < np.max(highs[pivot_i - structure_window:pivot_i + 1]) * 0.985:
            continue
        if level <= np.max(highs[pivot_i - pivot_side:pivot_i]):
            continue
        if level <= np.max(highs[pivot_i + 1:pivot_i + pivot_side + 1]):
            continue
        if (level - closes[pivot_i - trend_bars]) / closes[pivot_i - trend_bars] < min_trend:
            continue

        breakout_i = None
        for i in range(pivot_i + min_pivot_to_breakout, n):
            crossed = (
                closes[i - 1] <= level + level_zone(level, i)
                and closes[i] >= level + breakout_buffer(level, i)
            )
            if crossed and closes[i] > opens[i] and volume_ok(i):
                breakout_i = i
                break

        if breakout_i is None:
            continue

        for i in range(breakout_i + min_retest_bars, min(n, breakout_i + max_retest_bars + 1)):
            if lows[i] < level - invalidation_buffer(level, i):
                break
            if closes[i] < level - invalidation_buffer(level, i):
                break

            touched = (
                lows[i] <= level + touch_zone(level, i)
                and lows[i] >= level - invalidation_buffer(level, i)
            )
            if touched:
                if i >= n - recent_touch_bars:
                    signal = make_signal("bull", level, pivot_i, breakout_i, i, lows[i])
                    if signal:
                        results.append(signal)
                break

    # دعم صار مقاومة.
    for pivot_i in range(first_pivot, last_pivot):
        level = lows[pivot_i]
        zone = level_zone(level, pivot_i)
        prior_lows = lows[max(0, pivot_i - structure_window):pivot_i]
        prior_touches = np.where(np.abs(prior_lows - level) <= zone)[0]
        has_prior_touch = any(
            pivot_i - (max(0, pivot_i - structure_window) + p) >= pivot_side * 2
            for p in prior_touches
        )
        if not has_prior_touch:
            continue
        if level > np.min(lows[pivot_i - structure_window:pivot_i + 1]) * 1.015:
            continue
        if level >= np.min(lows[pivot_i - pivot_side:pivot_i]):
            continue
        if level >= np.min(lows[pivot_i + 1:pivot_i + pivot_side + 1]):
            continue
        if (closes[pivot_i - trend_bars] - level) / closes[pivot_i - trend_bars] < min_trend:
            continue

        breakout_i = None
        for i in range(pivot_i + min_pivot_to_breakout, n):
            crossed = (
                closes[i - 1] >= level - level_zone(level, i)
                and closes[i] <= level - breakout_buffer(level, i)
            )
            if crossed and closes[i] < opens[i] and volume_ok(i):
                breakout_i = i
                break

        if breakout_i is None:
            continue

        for i in range(breakout_i + min_retest_bars, min(n, breakout_i + max_retest_bars + 1)):
            if highs[i] > level + invalidation_buffer(level, i):
                break
            if closes[i] > level + invalidation_buffer(level, i):
                break

            touched = (
                highs[i] >= level - touch_zone(level, i)
                and highs[i] <= level + invalidation_buffer(level, i)
            )
            if touched:
                if i >= n - recent_touch_bars:
                    signal = make_signal("bear", level, pivot_i, breakout_i, i, highs[i])
                    if signal:
                        results.append(signal)
                break

    return results[-1:] if results else []

# ═══════════════════════════════════════════════
# رسالة تيليجرام
# ═══════════════════════════════════════════════
def build_msg(sym, sector, sig):
    d = sig["direction"]
    lv = sig["level"]
    bp = sig["breakout_price"]
    rp = sig["retest_price"]
    cp = sig["current_price"]
    dist = sig["dist_pct"]
    tf = sig["tf"]
    stop = sig["stop"]
    t1 = sig["target1"]
    t2 = sig["target2"]

    if d == "bull":
        header = f"🔔 <b>وصل نقطة تبادل أدوار صعودية — {sym}</b>"
        status = "🟢 مقاومة سابقة → دعم حالي"
    else:
        header = f"🔔 <b>وصل نقطة تبادل أدوار هبوطية — {sym}</b>"
        status = "🔴 دعم سابق → مقاومة حالية"

    return (
        f"{header}\n🏷 {sector}\n📐 الفريم: <b>{tf}</b>\n{status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 نقطة تبادل الأدوار: <b>${lv:.2f}</b>\n"
        f"🚀 سعر الكسر: <b>${bp:.2f}</b>\n"
        f"🎯 سعر اللمس الحالي: <b>${rp:.2f}</b>\n"
        f"📏 البعد عن المستوى: <b>{dist:.2f}%</b>\n"
        f"⏱ وقت اللمس: <b>{sig['confirm_time']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 سعر الدخول المرجعي: <b>${cp:.2f}</b>\n"
        f"🛑 الوقف: <b>${stop:.2f}</b>\n"
        f"🎯 هدف 1 (1:2): <b>${t1:.2f}</b>\n"
        f"🎯 هدف 2 (1:3): <b>${t2:.2f}</b>\n"
        f"⚠️ <i>تنبيه لمس مستوى فقط — لا ينتظر تأكيد شمعة.</i>"
    )

# ═══════════════════════════════════════════════
# الفحص الرئيسي
# ═══════════════════════════════════════════════
def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص ({len(STOCKS)} سهم)")
    total = 0

    TFS = [
        ("15m", "15 دقيقة"), ("30m", "30 دقيقة"), ("1h", "ساعة"),
        ("4h", "4 ساعات"), ("1d", "يومي"), ("1wk", "أسبوعي"),
    ]

    for sym, sector in STOCKS.items():
        new_msgs = []

        # ── كل فريم بمعزل عن الآخر: خطأ في فريم واحد لا يوقف بقية الفريمات
        #    (هذا هو الإصلاح الأهم — سابقاً خطأ فريم 4h كان يُسقط فحص
        #    اليومي والأسبوعي بالكامل لكل سهم بسبب try/except واحد للسهم كله)
        for interval, tf_name in TFS:
            try:
                df = get_data(sym, interval)
                if df.empty or len(df) < 80:
                    continue

                for sig in detect_role_reversal(df, tf_name):
                    key = sig_key(sym, sig["direction"], sig["level"], tf_name, sig["confirm_time"])
                    if key not in SENT:
                        new_msgs.append((build_msg(sym, sector, sig), key))

            except Exception as e:
                print(f"  ⚠️ {sym} [{tf_name}]: {e}")
                continue

        try:
            if new_msgs:
                delivered_for_symbol = 0
                for msg, key in new_msgs:
                    if send_telegram(msg):
                        SENT.add(key)
                        delivered_for_symbol += 1
                        time.sleep(0.8)
                    else:
                        print(f"  ⚠️ {sym}: لم تُرسل الإشارة؛ ستُعاد المحاولة في الفحص القادم")

                save_sent(SENT)
                if delivered_for_symbol:
                    print(f"  ✅ {sym} — {delivered_for_symbol} إشعار مُرسل")
                    total += delivered_for_symbol
            else:
                print(f"  — {sym}: لا إشارات")

        except Exception as e:
            print(f"  ❌ {sym}: {e}")

    send_telegram(
        f"🔍 <b>انتهى الفحص</b>\n"
        f"الأسهم: {len(STOCKS)} | 15د+30د+1h+4h+يومي+أسبوعي\n"
        f"✅ إشارات: {total}\n⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\n✅ إشارات: {total}")

if __name__ == "__main__":
    print(f"🚀 بوت لمس تبادل الأدوار | {len(STOCKS)} سهم | 6 فريمات | كسر ثم لمس مستوى + وقف/هدف")
    check_all()

    if not RUN_ONCE:
        import schedule

        schedule.every(1).hours.do(check_all)
        while True:
            schedule.run_pending()
            time.sleep(60)
