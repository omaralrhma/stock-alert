import yfinance as yf
import requests
import time
import numpy as np
import os, sys, json, hashlib

TOKEN    = os.environ.get("TG_TOKEN",  "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4")
_chats   = os.environ.get("TG_CHATS", "615265045,7775490993,5574232437")
CHAT_IDS = [c.strip() for c in _chats.split(",") if c.strip()]
RUN_ONCE = "--once" in sys.argv

# ═══════════════════════════════════════════════
# 300+ سهم — أعلى تداول أوبشن
# ═══════════════════════════════════════════════
STOCKS = {
    # تكنولوجيا كبرى
    "AAPL":"💻 تك","MSFT":"💻 تك","NVDA":"💻 تك","GOOGL":"💻 تك","AMZN":"💻 تك",
    "META":"💻 تك","TSLA":"💻 تك","AMD":"💻 تك","INTC":"💻 تك","AVGO":"💻 تك",
    "QCOM":"💻 تك","TXN":"💻 تك","AMAT":"💻 تك","MU":"💻 تك","LRCX":"💻 تك",
    "KLAC":"💻 تك","MRVL":"💻 تك","ARM":"💻 تك","SMCI":"💻 تك","DELL":"💻 تك",
    "HPQ":"💻 تك","IBM":"💻 تك","STX":"💻 تك","WDC":"💻 تك","NTAP":"💻 تك",
    # تكنولوجيا سحابة وأمن
    "CRM":"💻 سحابة","ORCL":"💻 سحابة","ADBE":"💻 سحابة","NOW":"💻 سحابة","WDAY":"💻 سحابة",
    "VEEV":"💻 سحابة","HUBS":"💻 سحابة","PAYC":"💻 سحابة","ROP":"💻 سحابة","ANSS":"💻 سحابة",
    "SNPS":"💻 سحابة","CDNS":"💻 سحابة","PANW":"💻 أمن","CRWD":"💻 أمن","ZS":"💻 أمن",
    "FTNT":"💻 أمن","NET":"💻 أمن","OKTA":"💻 أمن","S":"💻 أمن","CYBR":"💻 أمن",
    # تكنولوجيا نمو
    "SHOP":"💻 نمو","PLTR":"💻 نمو","SNOW":"💻 نمو","DDOG":"💻 نمو","MDB":"💻 نمو",
    "TEAM":"💻 نمو","TWLO":"💻 نمو","ZM":"💻 نمو","DOCU":"💻 نمو","BOX":"💻 نمو",
    "BILL":"💻 نمو","TOST":"💻 نمو","APP":"💻 نمو","TTD":"💻 نمو","CFLT":"💻 نمو",
    "HOOD":"💻 نمو","RDDT":"💻 نمو","AFRM":"💻 نمو","SOFI":"💻 نمو","UPST":"💻 نمو",
    # ذكاء اصطناعي وكوانتم
    "AI":"🤖 ذكاء","SOUN":"🤖 ذكاء","IONQ":"🤖 ذكاء","RGTI":"🤖 ذكاء","QBTS":"🤖 ذكاء",
    "BBAI":"🤖 ذكاء","ACHR":"🤖 ذكاء","JOBY":"🤖 ذكاء","RKLB":"🤖 ذكاء","LUNR":"🤖 ذكاء",
    # مؤشرات وصناديق
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر","VXX":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","XLV":"📊 مؤشر","XLI":"📊 مؤشر",
    "XLP":"📊 مؤشر","XLY":"📊 مؤشر","XLB":"📊 مؤشر","XLRE":"📊 مؤشر","XLC":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","GDX":"📊 مؤشر","TLT":"📊 مؤشر","HYG":"📊 مؤشر",
    "EEM":"📊 مؤشر","FXI":"📊 مؤشر","KWEB":"📊 مؤشر","ARKK":"📊 مؤشر","ARKW":"📊 مؤشر",
    "TQQQ":"📊 رافعة","SQQQ":"📊 رافعة","SOXL":"📊 رافعة","SOXS":"📊 رافعة",
    "SPXL":"📊 رافعة","UVXY":"📊 رافعة","LABU":"📊 رافعة","FNGU":"📊 رافعة",
    # صحة
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة","LLY":"🏥 صحة",
    "BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة","VRTX":"🏥 صحة","REGN":"🏥 صحة",
    "MRNA":"🏥 صحة","TMO":"🏥 صحة","DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة",
    "ISRG":"🏥 صحة","DXCM":"🏥 صحة","BSX":"🏥 صحة","BIIB":"🏥 صحة","ILMN":"🏥 صحة",
    "HIMS":"🏥 صحة","INCY":"🏥 صحة","ALNY":"🏥 صحة","EXAS":"🏥 صحة","NTRA":"🏥 صحة",
    "HCA":"🏥 صحة","MOH":"🏥 صحة","UNH":"🏥 صحة","CI":"🏥 صحة","CVS":"🏥 صحة",
    # طاقة
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة","DVN":"⛽ طاقة",
    "MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة",
    "HES":"⛽ طاقة","PSX":"⛽ طاقة","MRO":"⛽ طاقة","APA":"⛽ طاقة","FANG":"⛽ طاقة",
    "CTRA":"⛽ طاقة","SM":"⛽ طاقة","RIG":"⛽ طاقة","NOG":"⛽ طاقة","MTDR":"⛽ طاقة",
    "ENPH":"🌱 متجددة","FSLR":"🌱 متجددة","BE":"🌱 متجددة","PLUG":"🌱 متجددة","SEDG":"🌱 متجددة",
    # استهلاكي
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي","HD":"🛒 استهلاكي","LOW":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي","NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي",
    "MNST":"🛒 استهلاكي","ROST":"🛒 استهلاكي","TJX":"🛒 استهلاكي","ULTA":"🛒 استهلاكي","ETSY":"🛒 استهلاكي",
    "ONON":"🛒 استهلاكي","SKX":"🛒 استهلاكي","DECK":"🛒 استهلاكي","RH":"🛒 استهلاكي","W":"🛒 استهلاكي",
    "DKNG":"🛒 ترفيه","BKNG":"🛒 ترفيه","ABNB":"🛒 ترفيه","EXPE":"🛒 ترفيه","MAR":"🛒 ترفيه",
    "HLT":"🛒 ترفيه","CCL":"🛒 ترفيه","RCL":"🛒 ترفيه","NCLH":"🛒 ترفيه","MGM":"🛒 ترفيه",
    # صناعي ونقل
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 صناعي","FDX":"🏭 صناعي","HON":"🏭 صناعي",
    "GE":"🏭 صناعي","ETN":"🏭 صناعي","EMR":"🏭 صناعي","PWR":"🏭 صناعي","AXON":"🏭 صناعي",
    "DAL":"🏭 نقل","UAL":"🏭 نقل","AAL":"🏭 نقل","LUV":"🏭 نقل","ALK":"🏭 نقل",
    # اتصالات وميديا
    "TMUS":"📡 اتصالات","NFLX":"📡 اتصالات","DIS":"📡 اتصالات","SPOT":"📡 اتصالات",
    "WBD":"📡 اتصالات","PARA":"📡 اتصالات","TTWO":"📡 اتصالات","EA":"📡 اتصالات",
    # مواد وتعدين
    "NEM":"⛏ مواد","FCX":"⛏ مواد","ALB":"⛏ مواد","AA":"⛏ مواد","X":"⛏ مواد",
    "CLF":"⛏ مواد","VALE":"⛏ مواد","BHP":"⛏ مواد","GOLD":"⛏ مواد","KGC":"⛏ مواد",
    "WPM":"⛏ مواد","AEM":"⛏ مواد","MP":"⛏ مواد","GDXJ":"⛏ مواد",
    # سيارات وEV
    "RIVN":"🚗 سيارات","LCID":"🚗 سيارات","NIO":"🚗 سيارات","XPEV":"🚗 سيارات",
    "LI":"🚗 سيارات","F":"🚗 سيارات","GM":"🚗 سيارات",
    # عقارات
    "PLD":"🏢 عقارات","AMT":"🏢 عقارات","EQIX":"🏢 عقارات","DLR":"🏢 عقارات",
    "O":"🏢 عقارات","SPG":"🏢 عقارات",
    # كريبتو
    "COIN":"🪙 كريبتو","MSTR":"🪙 كريبتو","MARA":"🪙 كريبتو","RIOT":"🪙 كريبتو",
    "HUT":"🪙 كريبتو","CLSK":"🪙 كريبتو",
    # مالية حلال
    "PYPL":"🏦 مالية","SPGI":"🏦 مالية","MCO":"🏦 مالية","MSCI":"🏦 مالية",
    "ICE":"🏦 مالية","NDAQ":"🏦 مالية","FDS":"🏦 مالية",
}

# ═══════════════════════════════════════════════
# إرسال + منع التكرار
# ═══════════════════════════════════════════════
SENT_FILE = "/tmp/sent_signals.json"

def load_sent():
    try:
        with open(SENT_FILE) as f: return set(json.load(f))
    except: return set()

def save_sent(s):
    try:
        with open(SENT_FILE,"w") as f: json.dump(list(s)[-500:], f)
    except: pass

def sig_key(sym, direction, level, tf):
    return hashlib.md5(f"{sym}_{direction}_{level:.2f}_{tf}".encode()).hexdigest()[:12]

SENT = load_sent()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id":cid,"text":msg,"parse_mode":"HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ: {e}")

# ═══════════════════════════════════════════════
# جلب البيانات
# ═══════════════════════════════════════════════
def get_data(symbol, interval):
    pm = {"15m":"60d","30m":"60d","1h":"60d","4h":"60d","1d":"2y","1wk":"5y"}
    df = yf.download(symbol, period=pm.get(interval,"1y"),
                     interval=interval, progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

# ═══════════════════════════════════════════════
# أنماط الشموع اليابانية — تأكيد الانعكاس عند نقطة تبادل الأدوار
# ═══════════════════════════════════════════════
def _body(o, c, i):
    return abs(c[i] - o[i])

def _rng(h, l, i):
    return max(h[i] - l[i], 1e-9)

def is_bullish_engulfing(o, c, i):
    if i < 1: return False
    prev_bear = c[i-1] < o[i-1]
    curr_bull = c[i]   > o[i]
    return prev_bear and curr_bull and o[i] <= c[i-1] and c[i] >= o[i-1]

def is_bearish_engulfing(o, c, i):
    if i < 1: return False
    prev_bull = c[i-1] > o[i-1]
    curr_bear = c[i]   < o[i]
    return prev_bull and curr_bear and o[i] >= c[i-1] and c[i] <= o[i-1]

def is_hammer_shape(o, c, h, l, i):
    body = _body(o, c, i); rng = _rng(h, l, i)
    if body / rng > 0.35: return False
    lower_wick = min(o[i], c[i]) - l[i]
    upper_wick = h[i] - max(o[i], c[i])
    return lower_wick >= 2 * max(body, rng * 0.05) and upper_wick <= body + rng * 0.08

def is_shooting_star_shape(o, c, h, l, i):
    body = _body(o, c, i); rng = _rng(h, l, i)
    if body / rng > 0.35: return False
    upper_wick = h[i] - max(o[i], c[i])
    lower_wick = min(o[i], c[i]) - l[i]
    return upper_wick >= 2 * max(body, rng * 0.05) and lower_wick <= body + rng * 0.08

def is_doji(o, c, h, l, i):
    return _body(o, c, i) / _rng(h, l, i) <= 0.12

def is_morning_star(o, c, h, l, i):
    if i < 2: return False
    b1, r1 = _body(o, c, i-2), _rng(h, l, i-2)
    b3, r3 = _body(o, c, i),   _rng(h, l, i)
    first_bear_big = c[i-2] < o[i-2] and b1 / r1 > 0.5
    star_small     = _body(o, c, i-1) / _rng(h, l, i-1) < 0.35
    third_bull_big = c[i] > o[i] and b3 / r3 > 0.5
    closes_deep    = c[i] > (o[i-2] + c[i-2]) / 2
    return first_bear_big and star_small and third_bull_big and closes_deep

def is_evening_star(o, c, h, l, i):
    if i < 2: return False
    b1, r1 = _body(o, c, i-2), _rng(h, l, i-2)
    b3, r3 = _body(o, c, i),   _rng(h, l, i)
    first_bull_big = c[i-2] > o[i-2] and b1 / r1 > 0.5
    star_small     = _body(o, c, i-1) / _rng(h, l, i-1) < 0.35
    third_bear_big = c[i] < o[i] and b3 / r3 > 0.5
    closes_deep    = c[i] < (o[i-2] + c[i-2]) / 2
    return first_bull_big and star_small and third_bear_big and closes_deep

def bullish_confirmation(o, c, h, l, i):
    """شمعة تأكيد صعودية عند نقطة تبادل الأدوار (مقاومة تحولت لدعم)"""
    if is_bullish_engulfing(o, c, i):        return "ابتلاع صعودي"
    if is_hammer_shape(o, c, h, l, i):       return "مطرقة / بن بار"
    if i >= 1 and is_doji(o, c, h, l, i-1) and c[i] > o[i] and c[i] > h[i-1]:
        return "دوجي + تأكيد"
    if is_morning_star(o, c, h, l, i):       return "نجمة الصباح"
    return None

def bearish_confirmation(o, c, h, l, i):
    """شمعة تأكيد هبوطية عند نقطة تبادل الأدوار (دعم تحول لمقاومة)"""
    if is_bearish_engulfing(o, c, i):         return "ابتلاع هبوطي"
    if is_shooting_star_shape(o, c, h, l, i): return "نجمة هابطة / بن بار"
    if i >= 1 and is_doji(o, c, h, l, i-1) and c[i] < o[i] and c[i] < l[i-1]:
        return "دوجي + تأكيد"
    if is_evening_star(o, c, h, l, i):        return "نجمة المساء"
    return None

# ═══════════════════════════════════════════════
# تبادل الأدوار الهيكلي الصارم
# ═══════════════════════════════════════════════
def detect_role_reversal(df, tf):
    """
    معادلة تبادل الأدوار الكاملة — 7 شروط، تعمل بنفس المنطق على كل الفريمات
    لأن المبدأ سلوكي/نفسي وليس مرتبطاً بفريم معين:

    ① مستوى مُختبر مرتين على الأقل (Multiple Touches)
    ② اختراق حقيقي بإغلاق واضح + حجم تداول > 1.5x المتوسط
    ③ إعادة اختبار نظيفة (لا إغلاق تحت/فوق المستوى بين الاختراق والـ retest)
    ④ شمعة تأكيد يابانية معتمدة: ابتلاع / مطرقة-بن بار / نجمة صباح-مساء / دوجي+تأكيد
       (هذا هو الشرط الذي يفرّق النموذج الصحيح عن الاختراق الكاذب)
    ⑤ الدخول عند إغلاق شمعة التأكيد
    ⑥ الوقف خلف أدنى/أعلى نقطة سُجّلت أثناء إعادة الاختبار (+هامش 0.5%)
    ⑦ هدفان بنسبة مخاطرة-عائد 1:2 و 1:3

    الشروط الهيكلية (اتجاه سابق، القمة/القاع المطلق، الفجوة الزمنية، عمق الوادي)
    كما هي في النسخة السابقة — لم تُمس.
    """
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    highs   = df["High"].squeeze()
    lows    = df["Low"].squeeze()
    volumes = df["Volume"].squeeze()
    n       = len(closes)

    PS   = 15    # Pivot Side
    AW   = 40    # Absolute Window للقمة المطلقة
    UT   = 30    # Uptrend lookback bars
    UTP  = 0.15  # Uptrend minimum 15%
    MG   = 20    # Min Gap pivot→breakout
    VD   = 0.05  # Valley Depth 5%
    MRB  = 5     # Min Retest Bars
    MXR  = 20    # Max Retest Bars
    CFW  = 5     # نافذة انتظار شمعة التأكيد بعد لمس المنطقة
    BRK  = 0.010 # Breakout 1%
    VOLX = 1.5   # Volume multiplier
    BFL  = 0.992 # Buffer Low
    BFH  = 1.015 # Buffer High
    STOP_BUF = 0.005  # هامش الوقف خلف قاع/قمة إعادة الاختبار

    min_bars = max(PS*2, AW) + MG + MRB + 10
    if n < min_bars:
        return []

    c = closes.values.astype(float)
    o = opens.values.astype(float)
    h = highs.values.astype(float)
    l = lows.values.astype(float)
    v = volumes.values.astype(float)

    vol_ma = np.array([
        np.mean(v[max(0,i-20):i]) if i >= 20 else np.mean(v[:i+1])
        for i in range(n)
    ])

    results = []

    # ══ صعودي: مقاومة → دعم ══
    for pi in range(max(PS, AW, UT), n - PS - MG - 1):
        res = h[pi]

        price_30_before = c[pi - UT]
        uptrend_gain    = (res - price_30_before) / price_30_before
        if uptrend_gain < UTP:
            continue

        abs_window_high = np.max(h[pi - AW: pi + 1])
        if res < abs_window_high * 0.998:
            continue

        if res <= np.max(h[pi-PS:pi]) or res <= np.max(h[pi+1:pi+PS+1]):
            continue

        touch_zone = res * 0.01
        touches = np.sum(np.abs(h[max(0,pi-AW):pi] - res) <= touch_zone)
        if touches < 1:
            continue

        state = 0; bi = None; bc = None; retest_i = None; retest_l = None
        valley = res

        for i in range(pi+1, n):
            ci,oi,hi2,li,vi = c[i],o[i],h[i],l[i],v[i]

            if state == 0:
                if li < valley: valley = li
                if i - pi < MG: continue
                if (res - valley)/res < VD: continue
                vol_ok = vi > VOLX * vol_ma[i] if vol_ma[i] > 0 else True
                if (ci-res)/res >= BRK and ci > oi and vol_ok:
                    state=1; bi=i; bc=ci
                elif ci < res * 0.70:
                    break

            elif state == 1:
                bs = i - bi
                if ci < res: state=0; break
                if bs > MXR: state=0; break
                if bs < MRB: continue
                if BFL*res <= li <= BFH*res:
                    if ci >= res:
                        state = 2; retest_i = i; retest_l = li
                        patt = bullish_confirmation(o, c, h, l, i)
                        if patt:
                            stop = retest_l * (1 - STOP_BUF)
                            risk = ci - stop
                            if risk > 0 and i == n-1:
                                results.append({
                                    "direction":"bull","level":res,"pattern":patt,
                                    "valley_drop":(res-valley)/res*100,
                                    "uptrend_gain":uptrend_gain*100,
                                    "breakout_price":bc,"retest_price":ci,
                                    "current_price":ci,"dist_pct":abs(ci-res)/res*100,
                                    "tf":tf,"gap_bars":bi-pi,
                                    "stop":stop,"target1":ci+2*risk,"target2":ci+3*risk,
                                })
                            state=0; break
                    else:
                        state=0; break

            elif state == 2:
                if ci < res: state=0; break
                if i - retest_i > CFW: state=0; break
                if li < retest_l: retest_l = li
                patt = bullish_confirmation(o, c, h, l, i)
                if patt:
                    stop = retest_l * (1 - STOP_BUF)
                    risk = ci - stop
                    if risk > 0 and i == n-1:
                        results.append({
                            "direction":"bull","level":res,"pattern":patt,
                            "valley_drop":(res-valley)/res*100,
                            "uptrend_gain":uptrend_gain*100,
                            "breakout_price":bc,"retest_price":ci,
                            "current_price":ci,"dist_pct":abs(ci-res)/res*100,
                            "tf":tf,"gap_bars":bi-pi,
                            "stop":stop,"target1":ci+2*risk,"target2":ci+3*risk,
                        })
                    state=0; break

    # ══ هبوطي: دعم → مقاومة ══
    for pi in range(max(PS, AW, UT), n - PS - MG - 1):
        sup = l[pi]

        price_30_before  = c[pi - UT]
        downtrend_drop   = (price_30_before - sup) / price_30_before
        if downtrend_drop < UTP:
            continue

        abs_window_low = np.min(l[pi - AW: pi + 1])
        if sup > abs_window_low * 1.002:
            continue

        if sup >= np.min(l[pi-PS:pi]) or sup >= np.min(l[pi+1:pi+PS+1]):
            continue

        touch_zone = sup * 0.01
        touches = np.sum(np.abs(l[max(0,pi-AW):pi] - sup) <= touch_zone)
        if touches < 1:
            continue

        state = 0; bi = None; bc = None; retest_i = None; retest_h = None
        peak = sup

        for i in range(pi+1, n):
            ci,oi,hi2,li,vi = c[i],o[i],h[i],l[i],v[i]

            if state == 0:
                if hi2 > peak: peak = hi2
                if i - pi < MG: continue
                if (peak-sup)/sup < VD: continue
                vol_ok = vi > VOLX * vol_ma[i] if vol_ma[i] > 0 else True
                if (sup-ci)/sup >= BRK and ci < oi and vol_ok:
                    state=1; bi=i; bc=ci
                elif ci > sup * 1.30:
                    break

            elif state == 1:
                bs = i - bi
                if ci > sup: state=0; break
                if bs > MXR: state=0; break
                if bs < MRB: continue
                if BFL*sup <= hi2 <= BFH*sup:
                    if ci <= sup:
                        state = 2; retest_i = i; retest_h = hi2
                        patt = bearish_confirmation(o, c, h, l, i)
                        if patt:
                            stop = retest_h * (1 + STOP_BUF)
                            risk = stop - ci
                            if risk > 0 and i == n-1:
                                results.append({
                                    "direction":"bear","level":sup,"pattern":patt,
                                    "valley_drop":(peak-sup)/sup*100,
                                    "uptrend_gain":downtrend_drop*100,
                                    "breakout_price":bc,"retest_price":ci,
                                    "current_price":ci,"dist_pct":abs(ci-sup)/sup*100,
                                    "tf":tf,"gap_bars":bi-pi,
                                    "stop":stop,"target1":ci-2*risk,"target2":ci-3*risk,
                                })
                            state=0; break
                    else:
                        state=0; break

            elif state == 2:
                if ci > sup: state=0; break
                if i - retest_i > CFW: state=0; break
                if hi2 > retest_h: retest_h = hi2
                patt = bearish_confirmation(o, c, h, l, i)
                if patt:
                    stop = retest_h * (1 + STOP_BUF)
                    risk = stop - ci
                    if risk > 0 and i == n-1:
                        results.append({
                            "direction":"bear","level":sup,"pattern":patt,
                            "valley_drop":(peak-sup)/sup*100,
                            "uptrend_gain":downtrend_drop*100,
                            "breakout_price":bc,"retest_price":ci,
                            "current_price":ci,"dist_pct":abs(ci-sup)/sup*100,
                            "tf":tf,"gap_bars":bi-pi,
                            "stop":stop,"target1":ci-2*risk,"target2":ci-3*risk,
                        })
                    state=0; break

    return results[-1:] if results else []


def build_msg(sym, sector, sig):
    d,lv,bp,rp,cp = sig["direction"],sig["level"],sig["breakout_price"],sig["retest_price"],sig["current_price"]
    vd,dist,gap,tf = sig["valley_drop"],sig["dist_pct"],sig["gap_bars"],sig["tf"]
    stop, t1, t2, patt = sig["stop"], sig["target1"], sig["target2"], sig["pattern"]
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
        f"📈 الاتجاه قبل القمة: <b>+{ug:.1f}%</b>\n"
        f"🏔 الوادي: <b>{vd:.1f}%</b> | فجوة: <b>{gap} شمعة</b>\n"
        f"🚀 الاختراق: <b>${bp:.2f}</b>\n"
        f"🔄 Retest: <b>${rp:.2f}</b>\n"
        f"🕯 شمعة التأكيد: <b>{patt}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 الدخول: <b>${cp:.2f}</b>\n"
        f"🛑 الوقف: <b>${stop:.2f}</b>\n"
        f"🎯 هدف 1 (1:2): <b>${t1:.2f}</b>\n"
        f"🎯 هدف 2 (1:3): <b>${t2:.2f}</b>\n"
        f"📏 البعد: <b>{dist:.2f}%</b>"
    )


# ═══════════════════════════════════════════════
# الفحص الرئيسي
# ═══════════════════════════════════════════════
def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص ({len(STOCKS)} سهم)")
    total = 0
    TFS = [("15m","15 دقيقة"),("30m","30 دقيقة"),("1h","ساعة"),
           ("4h","4 ساعات"),("1d","يومي"),("1wk","أسبوعي")]

    for sym, sector in STOCKS.items():
        try:
            new_msgs = []
            for interval, tf_name in TFS:
                df = get_data(sym, interval)
                if df.empty or len(df) < 80: continue
                for sig in detect_role_reversal(df, tf_name):
                    key = sig_key(sym, sig["direction"], sig["level"], tf_name)
                    if key not in SENT:
                        new_msgs.append((build_msg(sym, sector, sig), key))

            if new_msgs:
                for msg, key in new_msgs:
                    send_telegram(msg)
                    SENT.add(key)
                    time.sleep(0.8)
                save_sent(SENT)
                print(f"  ✅ {sym} — {len(new_msgs)} إشعار")
                total += 1
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


print(f"🚀 بوت تبادل الأدوار | {len(STOCKS)} سهم | 6 فريمات | تأكيد بالشموع اليابانية + وقف/هدف")
check_all()

if not RUN_ONCE:
    import schedule
    schedule.every(1).hours.do(check_all)
    while True:
        schedule.run_pending()
        time.sleep(60)
