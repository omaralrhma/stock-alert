import yfinance as yf
import requests
import time
import numpy as np
import pandas as pd
import os, sys, json, hashlib

TOKEN = os.environ.get("TG_TOKEN", "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4")
_chats = os.environ.get("TG_CHATS", "615265045,7775490993,5574232437")
CHAT_IDS = [c.strip() for c in _chats.split(",") if c.strip()]
RUN_ONCE = "--once" in sys.argv

if not TOKEN:
    raise RuntimeError("ضع رمز البوت في متغير البيئة TG_TOKEN؛ لا تضعه داخل الملف.")
if not CHAT_IDS:
    raise RuntimeError("ضع معرّف محادثة واحدًا أو أكثر في متغير البيئة TG_CHATS.")

# ═══════════════════════════════════════════════
# أسهم شركات فردية ذات أوبشن — بدون مؤشرات أو صناديق
# ═══════════════════════════════════════════════
STOCKS = {
    # تقنية كبرى وأشباه موصلات
    "AAPL":"💻 تقنية","MSFT":"💻 تقنية","NVDA":"💻 تقنية","GOOGL":"💻 تقنية","AMZN":"💻 تقنية",
    "META":"💻 تقنية","TSLA":"💻 تقنية","AMD":"💻 تقنية","INTC":"💻 تقنية","AVGO":"💻 تقنية",
    "QCOM":"💻 تقنية","TXN":"💻 تقنية","AMAT":"💻 تقنية","MU":"💻 تقنية","LRCX":"💻 تقنية",
    "KLAC":"💻 تقنية","MRVL":"💻 تقنية","ARM":"💻 تقنية","SMCI":"💻 تقنية","DELL":"💻 تقنية",
    "HPQ":"💻 تقنية","IBM":"💻 تقنية","STX":"💻 تقنية","WDC":"💻 تقنية","NTAP":"💻 تقنية",
    "MCHP":"💻 أشباه موصلات","ON":"💻 أشباه موصلات","NXPI":"💻 أشباه موصلات","ADI":"💻 أشباه موصلات",
    "MPWR":"💻 أشباه موصلات","SWKS":"💻 أشباه موصلات","QRVO":"💻 أشباه موصلات","COHR":"💻 أشباه موصلات",
    "TER":"💻 أشباه موصلات","LSCC":"💻 أشباه موصلات","ENTG":"💻 أشباه موصلات","WOLF":"💻 أشباه موصلات",
    "CRDO":"💻 أشباه موصلات","ALAB":"💻 أشباه موصلات","SNDK":"💻 تخزين","PSTG":"💻 تخزين",

    # برمجيات وسحابة وأمن وإنترنت
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

    # ذكاء اصطناعي وكوانتم وطيران فضائي وكريبتو
    "AI":"🤖 ذكاء","SOUN":"🤖 ذكاء","IONQ":"🤖 كوانتم","RGTI":"🤖 كوانتم","QBTS":"🤖 كوانتم",
    "BBAI":"🤖 ذكاء","ACHR":"🚁 طيران","JOBY":"🚁 طيران","RKLB":"🚀 فضاء","LUNR":"🚀 فضاء",
    "TEM":"🤖 ذكاء","RBRK":"💻 أمن","MSTR":"🪙 كريبتو","COIN":"🪙 كريبتو","MARA":"🪙 تعدين",
    "RIOT":"🪙 تعدين","HUT":"🪙 تعدين","CLSK":"🪙 تعدين","BTDR":"🪙 تعدين","BTBT":"🪙 تعدين",
    "CORZ":"🪙 تعدين","IREN":"🪙 تعدين","CIFR":"🪙 تعدين","WULF":"🪙 تعدين",

    # بنوك وخدمات مالية ومدفوعات وإدارة أصول
    "JPM":"🏦 بنوك","BAC":"🏦 بنوك","WFC":"🏦 بنوك","C":"🏦 بنوك","GS":"🏦 بنوك",
    "MS":"🏦 بنوك","SCHW":"🏦 بنوك","BK":"🏦 بنوك","STT":"🏦 بنوك","USB":"🏦 بنوك",
    "PNC":"🏦 بنوك","TFC":"🏦 بنوك","RF":"🏦 بنوك","KEY":"🏦 بنوك","FITB":"🏦 بنوك",
    "AXP":"🏦 مدفوعات","V":"🏦 مدفوعات","MA":"🏦 مدفوعات","PYPL":"🏦 مدفوعات","COF":"🏦 مالية",
    "SPGI":"🏦 مالية","MCO":"🏦 مالية","MSCI":"🏦 مالية","ICE":"🏦 مالية","NDAQ":"🏦 مالية",
    "FDS":"🏦 مالية","CME":"🏦 مالية","BLK":"🏦 أصول","BX":"🏦 أصول","KKR":"🏦 أصول",
    "APO":"🏦 أصول","ARES":"🏦 أصول","TROW":"🏦 أصول","ALLY":"🏦 مالية","DFS":"🏦 مالية",

    # رعاية صحية وأدوية وبيوتكنولوجيا
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

    # طاقة وخدمات طاقة وطاقة نظيفة
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة","DVN":"⛽ طاقة",
    "MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة",
    "PSX":"⛽ طاقة","FANG":"⛽ طاقة","CTRA":"⛽ طاقة","SM":"⛽ طاقة","MTDR":"⛽ طاقة",
    "EQT":"⛽ غاز","WMB":"⛽ غاز","KMI":"⛽ غاز","OKE":"⛽ غاز","LNG":"⛽ غاز",
    "AR":"⛽ غاز","RRC":"⛽ غاز","PR":"⛽ طاقة","OVV":"⛽ طاقة","TALO":"⛽ طاقة",
    "BKR":"⛽ خدمات","NOV":"⛽ خدمات","HP":"⛽ خدمات","LBRT":"⛽ خدمات","FTI":"⛽ خدمات",
    "ENPH":"🌱 طاقة نظيفة","FSLR":"🌱 طاقة نظيفة","BE":"🌱 طاقة نظيفة","PLUG":"🌱 طاقة نظيفة","SEDG":"🌱 طاقة نظيفة",
    "CCJ":"☢️ يورانيوم","UEC":"☢️ يورانيوم","UUUU":"☢️ يورانيوم","LEU":"☢️ يورانيوم","OKLO":"☢️ طاقة نووية",

    # استهلاكي وتجزئة وسفر ومطاعم
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

    # صناعي ودفاع ونقل
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 نقل","FDX":"🏭 نقل","HON":"🏭 صناعي",
    "GE":"🏭 صناعي","ETN":"🏭 صناعي","EMR":"🏭 صناعي","PWR":"🏭 صناعي","AXON":"🏭 صناعي",
    "DAL":"✈️ نقل","UAL":"✈️ نقل","AAL":"✈️ نقل","LUV":"✈️ نقل","ALK":"✈️ نقل",
    "BA":"✈️ طيران","LMT":"🛡️ دفاع","RTX":"🛡️ دفاع","NOC":"🛡️ دفاع","GD":"🛡️ دفاع",
    "HWM":"🏭 صناعي","URI":"🏭 صناعي","ROK":"🏭 صناعي","PCAR":"🏭 صناعي","CARR":"🏭 صناعي",
    "JCI":"🏭 صناعي","IR":"🏭 صناعي","PH":"🏭 صناعي","ITW":"🏭 صناعي","GWW":"🏭 صناعي",
    "WM":"🏭 خدمات","RSG":"🏭 خدمات","NSC":"🚂 نقل","CSX":"🚂 نقل","UNP":"🚂 نقل",
    "ODFL":"🚚 نقل","XPO":"🚚 نقل","JBHT":"🚚 نقل","CHRW":"🚚 نقل",

    # اتصالات وميديا
    "TMUS":"📡 اتصالات","T":"📡 اتصالات","VZ":"📡 اتصالات","CMCSA":"📡 ميديا","NFLX":"📡 ميديا",
    "DIS":"📡 ميديا","SPOT":"📡 ميديا","WBD":"📡 ميديا","TTWO":"🎮 ألعاب","EA":"🎮 ألعاب",
    "FOXA":"📡 ميديا","FOX":"📡 ميديا","CHTR":"📡 اتصالات","SIRI":"📡 اتصالات","LYV":"📡 ترفيه",
    "IMAX":"📡 ترفيه","AMC":"📡 ترفيه","GME":"🎮 ألعاب",

    # مواد وتعدين
    "NEM":"⛏️ مواد","FCX":"⛏️ مواد","ALB":"⛏️ مواد","AA":"⛏️ مواد","CLF":"⛏️ مواد",
    "VALE":"⛏️ مواد","BHP":"⛏️ مواد","GOLD":"⛏️ مواد","KGC":"⛏️ مواد","WPM":"⛏️ مواد",
    "AEM":"⛏️ مواد","MP":"⛏️ مواد","NUE":"⛏️ صلب","STLD":"⛏️ صلب","CMC":"⛏️ صلب",
    "RS":"⛏️ صلب","TECK":"⛏️ معادن","SCCO":"⛏️ نحاس","RIO":"⛏️ معادن","MOS":"⛏️ أسمدة",
    "CF":"⛏️ أسمدة","FMC":"⛏️ كيماويات","IPI":"⛏️ أسمدة","CE":"⛏️ كيماويات","DOW":"⛏️ كيماويات",

    # مرافق وعقارات
    "NEE":"⚡ مرافق","DUK":"⚡ مرافق","SO":"⚡ مرافق","AEP":"⚡ مرافق","EXC":"⚡ مرافق",
    "SRE":"⚡ مرافق","XEL":"⚡ مرافق","EIX":"⚡ مرافق","PCG":"⚡ مرافق","CEG":"⚡ طاقة",
    "VST":"⚡ طاقة","NRG":"⚡ طاقة","AES":"⚡ مرافق","PLD":"🏢 عقارات","AMT":"🏢 عقارات",
    "EQIX":"🏢 عقارات","DLR":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات","VICI":"🏢 عقارات",
    "WELL":"🏢 عقارات","AVB":"🏢 عقارات","EQR":"🏢 عقارات","PSA":"🏢 عقارات","CCI":"🏢 عقارات",
    "SBAC":"🏢 عقارات","EXR":"🏢 عقارات","KIM":"🏢 عقارات","BXP":"🏢 عقارات",

    # ADRs صينية نشطة بالأوبشن
    "BABA":"🌏 الصين","JD":"🌏 الصين","PDD":"🌏 الصين","BIDU":"🌏 الصين","NTES":"🌏 الصين",
    "YUMC":"🌏 الصين","BILI":"🌏 الصين","BEKE":"🌏 الصين","FUTU":"🌏 الصين","TIGR":"🌏 الصين",
    "TME":"🌏 الصين","LI":"🚗 سيارات","NIO":"🚗 سيارات","XPEV":"🚗 سيارات",
}

# ═══════════════════════════════════════════════
# إرسال ومنع التكرار
# ═══════════════════════════════════════════════
SENT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sent_signals.json",
)

def load_sent():
    try:
        with open(SENT_FILE) as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_sent(signals):
    try:
        with open(SENT_FILE, "w") as f:
            json.dump(list(signals)[-500:], f)
    except Exception:
        pass

def sig_key(sym, direction, level, tf, confirm_time):
    payload = f"{sym}_{direction}_{level:.4f}_{tf}_{confirm_time}"
    return hashlib.md5(payload.encode()).hexdigest()[:16]

SENT = load_sent()

def send_telegram(msg):
    """يرجع True إذا استلمت تيليجرام الرسالة لدى محادثة واحدة على الأقل."""
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
    periods = {
        "15m": "60d",
        "30m": "60d",
        "1h": "60d",
        "4h": "60d",
        "1d": "2y",
        "1wk": "5y",
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
# أنماط الشموع
# ═══════════════════════════════════════════════
def _body(o, c, i):
    return abs(c[i] - o[i])

def _rng(h, l, i):
    return max(h[i] - l[i], 1e-9)

def is_bullish_engulfing(o, c, i):
    if i < 1:
        return False
    prev_bear = c[i - 1] < o[i - 1]
    curr_bull = c[i] > o[i]
    return prev_bear and curr_bull and o[i] <= c[i - 1] and c[i] >= o[i - 1]

def is_bearish_engulfing(o, c, i):
    if i < 1:
        return False
    prev_bull = c[i - 1] > o[i - 1]
    curr_bear = c[i] < o[i]
    return prev_bull and curr_bear and o[i] >= c[i - 1] and c[i] <= o[i - 1]

def is_hammer_shape(o, c, h, l, i):
    body = _body(o, c, i)
    rng = _rng(h, l, i)
    if body / rng > 0.35:
        return False

    lower_wick = min(o[i], c[i]) - l[i]
    upper_wick = h[i] - max(o[i], c[i])
    return lower_wick >= 2 * max(body, rng * 0.05) and upper_wick <= body + rng * 0.08

def is_shooting_star_shape(o, c, h, l, i):
    body = _body(o, c, i)
    rng = _rng(h, l, i)
    if body / rng > 0.35:
        return False

    upper_wick = h[i] - max(o[i], c[i])
    lower_wick = min(o[i], c[i]) - l[i]
    return upper_wick >= 2 * max(body, rng * 0.05) and lower_wick <= body + rng * 0.08

def is_doji(o, c, h, l, i):
    return _body(o, c, i) / _rng(h, l, i) <= 0.12

def is_morning_star(o, c, h, l, i):
    if i < 2:
        return False

    b1, r1 = _body(o, c, i - 2), _rng(h, l, i - 2)
    b3, r3 = _body(o, c, i), _rng(h, l, i)
    first_bear_big = c[i - 2] < o[i - 2] and b1 / r1 > 0.5
    star_small = _body(o, c, i - 1) / _rng(h, l, i - 1) < 0.35
    third_bull_big = c[i] > o[i] and b3 / r3 > 0.5
    closes_deep = c[i] > (o[i - 2] + c[i - 2]) / 2
    return first_bear_big and star_small and third_bull_big and closes_deep

def is_evening_star(o, c, h, l, i):
    if i < 2:
        return False

    b1, r1 = _body(o, c, i - 2), _rng(h, l, i - 2)
    b3, r3 = _body(o, c, i), _rng(h, l, i)
    first_bull_big = c[i - 2] > o[i - 2] and b1 / r1 > 0.5
    star_small = _body(o, c, i - 1) / _rng(h, l, i - 1) < 0.35
    third_bear_big = c[i] < o[i] and b3 / r3 > 0.5
    closes_deep = c[i] < (o[i - 2] + c[i - 2]) / 2
    return first_bull_big and star_small and third_bear_big and closes_deep

def bullish_confirmation(o, c, h, l, i, level):
    rng = _rng(h, l, i)
    closes_strong = c[i] > o[i] and c[i] >= level and (c[i] - l[i]) / rng >= 0.55

    if not closes_strong:
        return None
    if is_bullish_engulfing(o, c, i):
        return "ابتلاع صعودي"
    if is_hammer_shape(o, c, h, l, i):
        return "مطرقة صاعدة"
    if i >= 1 and is_doji(o, c, h, l, i - 1) and c[i] > h[i - 1]:
        return "دوجي + تأكيد صاعد"
    if is_morning_star(o, c, h, l, i):
        return "نجمة الصباح"

    return None

def bearish_confirmation(o, c, h, l, i, level):
    rng = _rng(h, l, i)
    closes_strong = c[i] < o[i] and c[i] <= level and (h[i] - c[i]) / rng >= 0.55

    if not closes_strong:
        return None
    if is_bearish_engulfing(o, c, i):
        return "ابتلاع هبوطي"
    if is_shooting_star_shape(o, c, h, l, i):
        return "شمعة هابطة بذيل علوي"
    if i >= 1 and is_doji(o, c, h, l, i - 1) and c[i] < l[i - 1]:
        return "دوجي + تأكيد هابط"
    if is_evening_star(o, c, h, l, i):
        return "نجمة المساء"

    return None

# ═══════════════════════════════════════════════
# محرك تبادل الأدوار الصارم
# ═══════════════════════════════════════════════
def detect_role_reversal(df, tf):
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        return []

    closes = df["Close"].astype(float).to_numpy()
    opens = df["Open"].astype(float).to_numpy()
    highs = df["High"].astype(float).to_numpy()
    lows = df["Low"].astype(float).to_numpy()
    volumes = df["Volume"].astype(float).to_numpy()
    n = len(closes)

    pivot_side = 8
    structure_window = 60
    trend_bars = 30
    min_trend = 0.10
    min_pivot_to_breakout = 12
    min_retest_bars = 2
    max_retest_bars = 18
    confirm_window = 4
    volume_multiplier = 1.35
    stop_buffer = 0.005

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
        return max(price * 0.0035, atr[i] * 0.35)

    def breakout_buffer(price, i):
        return max(price * 0.004, atr[i] * 0.50)

    def invalidation_buffer(price, i):
        return max(price * 0.002, atr[i] * 0.25)

    def retest_penetration(price, i):
        return max(price * 0.005, atr[i] * 0.60)

    def volume_ok(i):
        return volume_ma[i] <= 0 or volumes[i] >= volume_multiplier * volume_ma[i]

    def make_signal(direction, level, pivot_i, breakout_i, retest_i, retest_extreme):
        entry = closes[retest_i]

        if direction == "bull":
            stop = retest_extreme * (1 - stop_buffer)
            risk = entry - stop
            target1 = entry + 2 * risk
            target2 = entry + 3 * risk
        else:
            stop = retest_extreme * (1 + stop_buffer)
            risk = stop - entry
            target1 = entry - 2 * risk
            target2 = entry - 3 * risk

        if risk <= 0:
            return None

        return {
            "direction": direction,
            "level": level,
            "valley_drop": abs(level - retest_extreme) / level * 100,
            "uptrend_gain": abs(level - closes[pivot_i - trend_bars]) / closes[pivot_i - trend_bars] * 100,
            "breakout_price": closes[breakout_i],
            "retest_price": closes[retest_i],
            "current_price": entry,
            "dist_pct": abs(entry - level) / level * 100,
            "tf": tf,
            "gap_bars": breakout_i - pivot_i,
            "stop": stop,
            "target1": target1,
            "target2": target2,
            "confirm_time": str(df.index[retest_i]),
        }

    results = []
    first_pivot = max(pivot_side, structure_window, trend_bars)
    last_pivot = n - pivot_side - min_pivot_to_breakout - min_retest_bars - 1

    # مقاومة تحولت إلى دعم
    for pivot_i in range(first_pivot, last_pivot):
        level = highs[pivot_i]
        zone = level_zone(level, pivot_i)

        prior_highs = highs[max(0, pivot_i - structure_window):pivot_i]
        touch_positions = np.where(np.abs(prior_highs - level) <= zone)[0]
        separated_touch = any(
            pivot_i - (max(0, pivot_i - structure_window) + p) >= pivot_side * 2
            for p in touch_positions
        )

        if not separated_touch:
            continue
        if level < np.max(highs[pivot_i - structure_window:pivot_i + 1]) * 0.999:
            continue
        if level <= np.max(highs[pivot_i - pivot_side:pivot_i]):
            continue
        if level <= np.max(highs[pivot_i + 1:pivot_i + pivot_side + 1]):
            continue
        if (level - closes[pivot_i - trend_bars]) / closes[pivot_i - trend_bars] < min_trend:
            continue

        state = "seek_breakout"
        breakout_i = None
        retest_i = None
        retest_low = None
        valley = level

        for i in range(pivot_i + 1, n):
            if state == "seek_breakout":
                valley = min(valley, lows[i])

                if i - pivot_i < min_pivot_to_breakout:
                    continue

                pullback_ok = (level - valley) >= max(level * 0.03, atr[i] * 1.50)
                crossed = (
                    closes[i - 1] <= level + level_zone(level, i)
                    and closes[i] >= level + breakout_buffer(level, i)
                )

                if pullback_ok and crossed and closes[i] > opens[i] and volume_ok(i):
                    state = "seek_retest"
                    breakout_i = i
                elif lows[i] < level * 0.70:
                    break

            elif state == "seek_retest":
                elapsed = i - breakout_i

                if lows[i] < level - retest_penetration(level, i):
                    break
                if closes[i] < level - invalidation_buffer(level, i):
                    break
                if elapsed > max_retest_bars:
                    break
                if elapsed < min_retest_bars:
                    continue

                touched_from_above = lows[i] <= level + level_zone(level, i)
                held_support = lows[i] >= level - retest_penetration(level, i)

                if touched_from_above and held_support:
                    if i == n - 1:
                        signal = make_signal("bull", level, pivot_i, breakout_i, i, lows[i])
                        if signal:
                            results.append(signal)
                    break

    # دعم تحول إلى مقاومة
    for pivot_i in range(first_pivot, last_pivot):
        level = lows[pivot_i]
        zone = level_zone(level, pivot_i)

        prior_lows = lows[max(0, pivot_i - structure_window):pivot_i]
        touch_positions = np.where(np.abs(prior_lows - level) <= zone)[0]
        separated_touch = any(
            pivot_i - (max(0, pivot_i - structure_window) + p) >= pivot_side * 2
            for p in touch_positions
        )

        if not separated_touch:
            continue
        if level > np.min(lows[pivot_i - structure_window:pivot_i + 1]) * 1.001:
            continue
        if level >= np.min(lows[pivot_i - pivot_side:pivot_i]):
            continue
        if level >= np.min(lows[pivot_i + 1:pivot_i + pivot_side + 1]):
            continue
        if (closes[pivot_i - trend_bars] - level) / closes[pivot_i - trend_bars] < min_trend:
            continue

        state = "seek_breakout"
        breakout_i = None
        retest_i = None
        retest_high = None
        peak = level

        for i in range(pivot_i + 1, n):
            if state == "seek_breakout":
                peak = max(peak, highs[i])

                if i - pivot_i < min_pivot_to_breakout:
                    continue

                pullback_ok = (peak - level) >= max(level * 0.03, atr[i] * 1.50)
                crossed = (
                    closes[i - 1] >= level - level_zone(level, i)
                    and closes[i] <= level - breakout_buffer(level, i)
                )

                if pullback_ok and crossed and closes[i] < opens[i] and volume_ok(i):
                    state = "seek_retest"
                    breakout_i = i
                elif highs[i] > level * 1.30:
                    break

            elif state == "seek_retest":
                elapsed = i - breakout_i

                if highs[i] > level + retest_penetration(level, i):
                    break
                if closes[i] > level + invalidation_buffer(level, i):
                    break
                if elapsed > max_retest_bars:
                    break
                if elapsed < min_retest_bars:
                    continue

                touched_from_below = highs[i] >= level - level_zone(level, i)
                held_resistance = highs[i] <= level + retest_penetration(level, i)

                if touched_from_below and held_resistance:
                    if i == n - 1:
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
    vd = sig["valley_drop"]
    dist = sig["dist_pct"]
    gap = sig["gap_bars"]
    tf = sig["tf"]
    stop = sig["stop"]
    t1 = sig["target1"]
    t2 = sig["target2"]

    if d == "bull":
        header = f"✅ <b>تبادل أدوار صعودي — {sym}</b>"
        status = "🟢 مقاومة هيكلية → دعم"
    else:
        header = f"✅ <b>تبادل أدوار هبوطي — {sym}</b>"
        status = "🔴 دعم هيكلي → مقاومة"

    ug = sig.get("uptrend_gain", 0)

    return (
        f"{header}\n🏷 {sector}\n📐 الفريم: <b>{tf}</b>\n{status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 المستوى: <b>${lv:.2f}</b>\n"
        f"📈 الاتجاه قبل القمة/القاع: <b>{ug:.1f}%</b>\n"
        f"🏔 عمق إعادة الاختبار: <b>{vd:.1f}%</b> | فجوة: <b>{gap} شمعة</b>\n"
        f"🚀 الاختراق: <b>${bp:.2f}</b>\n"
        f"🔄 Retest: <b>${rp:.2f}</b>\n"
        f"⏱ وقت اللمس: <b>{sig['confirm_time']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 الدخول: <b>${cp:.2f}</b>\n"
        f"🛑 الوقف: <b>${stop:.2f}</b>\n"
        f"🎯 هدف 1 (1:2): <b>${t1:.2f}</b>\n"
        f"🎯 هدف 2 (1:3): <b>${t2:.2f}</b>\n"
        f"📏 البعد عن المستوى: <b>{dist:.2f}%</b>"
    )

# ═══════════════════════════════════════════════
# الفحص الرئيسي
# ═══════════════════════════════════════════════
def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص ({len(STOCKS)} سهم)")
    total = 0

    TFS = [
        ("15m", "15 دقيقة"),
        ("30m", "30 دقيقة"),
        ("1h", "ساعة"),
        ("4h", "4 ساعات"),
        ("1d", "يومي"),
        ("1wk", "أسبوعي"),
    ]

    for sym, sector in STOCKS.items():
        try:
            new_msgs = []

            for interval, tf_name in TFS:
                df = get_data(sym, interval)
                if df.empty or len(df) < 80:
                    continue

                for sig in detect_role_reversal(df, tf_name):
                    key = sig_key(
                        sym,
                        sig["direction"],
                        sig["level"],
                        tf_name,
                        sig["confirm_time"],
                    )

                    if key not in SENT:
                        new_msgs.append((build_msg(sym, sector, sig), key))

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
        f"✅ إشارات مُرسلة: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )

    print(f"\n✅ إشارات مُرسلة: {total}")

if __name__ == "__main__":
    print(
        f"🚀 بوت تبادل الأدوار | {len(STOCKS)} سهم | 6 فريمات | "
        "شموع مغلقة + كسر + إعادة اختبار + تأكيد"
    )

    check_all()

    if not RUN_ONCE:
        import schedule

        schedule.every(1).hours.do(check_all)
        while True:
            schedule.run_pending()
            time.sleep(60)
