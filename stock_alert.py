import yfinance as yf
import requests
import schedule
import time
import numpy as np
import os
import sys
from scipy import stats

# ── يقرأ من Environment Variables إذا موجودة، وإلا يستخدم القيم الافتراضية
TOKEN    = os.environ.get("TG_TOKEN",  "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4")
_chats   = os.environ.get("TG_CHATS", "615265045,7775490993,5574232437")
CHAT_IDS = [c.strip() for c in _chats.split(",") if c.strip()]

# ── وضع التشغيل: --once = فحص واحد ثم يخرج (مناسب لـ GitHub Actions)
RUN_ONCE = "--once" in sys.argv

STOCKS = {
    # ── تكنولوجيا / ميجاكاب
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا",
    "GOOGL":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا","META":"💻 تكنولوجيا",
    "TSLA":"💻 تكنولوجيا","AMD":"💻 تكنولوجيا","INTC":"💻 تكنولوجيا",
    "CRM":"💻 تكنولوجيا","ORCL":"💻 تكنولوجيا","ADBE":"💻 تكنولوجيا",
    "QCOM":"💻 تكنولوجيا","TXN":"💻 تكنولوجيا","AMAT":"💻 تكنولوجيا",
    "MU":"💻 تكنولوجيا","LRCX":"💻 تكنولوجيا","KLAC":"💻 تكنولوجيا",
    "SNPS":"💻 تكنولوجيا","CDNS":"💻 تكنولوجيا","PANW":"💻 تكنولوجيا",
    "CRWD":"💻 تكنولوجيا","ZS":"💻 تكنولوجيا","FTNT":"💻 تكنولوجيا",
    "NET":"💻 تكنولوجيا","SNOW":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا",
    "MDB":"💻 تكنولوجيا","TEAM":"💻 تكنولوجيا","NOW":"💻 تكنولوجيا",
    "SHOP":"💻 تكنولوجيا","PLTR":"💻 تكنولوجيا","AVGO":"💻 تكنولوجيا",
    "MRVL":"💻 تكنولوجيا","ARM":"💻 تكنولوجيا","SMCI":"💻 تكنولوجيا",
    "UBER":"💻 تكنولوجيا","ABNB":"💻 تكنولوجيا","DASH":"💻 تكنولوجيا",
    "RBLX":"💻 تكنولوجيا","U":"💻 تكنولوجيا","HUBS":"💻 تكنولوجيا",
    "GTLB":"💻 تكنولوجيا","BILL":"💻 تكنولوجيا","TWLO":"💻 تكنولوجيا",
    "ZM":"💻 تكنولوجيا","DOCU":"💻 تكنولوجيا","BOX":"💻 تكنولوجيا",
    "DBX":"💻 تكنولوجيا","PATH":"💻 تكنولوجيا","AI":"💻 تكنولوجيا",
    "BBAI":"💻 تكنولوجيا","SOUN":"💻 تكنولوجيا","IONQ":"💻 تكنولوجيا",
    "RGTI":"💻 تكنولوجيا","QBTS":"💻 تكنولوجيا","QUBT":"💻 تكنولوجيا",
    "RXRX":"💻 تكنولوجيا","ACHR":"💻 تكنولوجيا","JOBY":"💻 تكنولوجيا",
    "HOOD":"💻 تكنولوجيا","RDDT":"💻 تكنولوجيا","AFRM":"💻 تكنولوجيا",
    "SOFI":"💻 تكنولوجيا","UPST":"💻 تكنولوجيا","LMND":"💻 تكنولوجيا",
    # ── أوبشن عالي التداول
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","XLV":"📊 مؤشر",
    "XLI":"📊 مؤشر","XLP":"📊 مؤشر","XLU":"📊 مؤشر","XLB":"📊 مؤشر",
    "XLRE":"📊 مؤشر","XLC":"📊 مؤشر","XLY":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","GDX":"📊 مؤشر","GDXJ":"📊 مؤشر",
    "USO":"📊 مؤشر","UNG":"📊 مؤشر","TLT":"📊 مؤشر","HYG":"📊 مؤشر",
    "EEM":"📊 مؤشر","FXI":"📊 مؤشر","KWEB":"📊 مؤشر","ARKK":"📊 مؤشر",
    "VIX":"📊 مؤشر","UVXY":"📊 مؤشر","SQQQ":"📊 مؤشر","TQQQ":"📊 مؤشر",
    "SPXU":"📊 مؤشر","SPXL":"📊 مؤشر","SOXL":"📊 مؤشر","SOXS":"📊 مؤشر",
    # ── صحة
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة","TMO":"🏥 صحة",
    "DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة","ISRG":"🏥 صحة",
    "DXCM":"🏥 صحة","IDXX":"🏥 صحة","BSX":"🏥 صحة","EW":"🏥 صحة",
    "BIIB":"🏥 صحة","ILMN":"🏥 صحة","IQV":"🏥 صحة","CNC":"🏥 صحة",
    "CVS":"🏥 صحة","CI":"🏥 صحة","HUM":"🏥 صحة","UNH":"🏥 صحة",
    "NVAX":"🏥 صحة","BNTX":"🏥 صحة","TDOC":"🏥 صحة","HIMS":"🏥 صحة",
    "NTRA":"🏥 صحة","INSP":"🏥 صحة","PODD":"🏥 صحة","NVCR":"🏥 صحة",
    # ── طاقة
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة",
    "HAL":"⛽ طاقة","SLB":"⛽ طاقة","HES":"⛽ طاقة","PSX":"⛽ طاقة",
    "PXD":"⛽ طاقة","APA":"⛽ طاقة","MRO":"⛽ طاقة","FANG":"⛽ طاقة",
    "ENPH":"🌱 متجددة","FSLR":"🌱 متجددة","RUN":"🌱 متجددة",
    "BE":"🌱 متجددة","PLUG":"🌱 متجددة","SEDG":"🌱 متجددة",
    # ── استهلاكي حلال
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "EL":"🛒 استهلاكي","ULTA":"🛒 استهلاكي","ONON":"🛒 استهلاكي",
    "SKX":"🛒 استهلاكي","DECK":"🛒 استهلاكي","RH":"🛒 استهلاكي",
    "ROST":"🛒 استهلاكي","TJX":"🛒 استهلاكي","DG":"🛒 استهلاكي",
    "DLTR":"🛒 استهلاكي","BBY":"🛒 استهلاكي","HD":"🛒 استهلاكي",
    "LOW":"🛒 استهلاكي","ETSY":"🛒 استهلاكي","W":"🛒 استهلاكي",
    # ── صناعي
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 صناعي",
    "FDX":"🏭 صناعي","HON":"🏭 صناعي","GE":"🏭 صناعي",
    "EMR":"🏭 صناعي","ETN":"🏭 صناعي","ROK":"🏭 صناعي",
    "PH":"🏭 صناعي","GNRC":"🏭 صناعي","XYL":"🏭 صناعي",
    "DAL":"🏭 صناعي","UAL":"🏭 صناعي","AAL":"🏭 صناعي",
    "LUV":"🏭 صناعي","SAVE":"🏭 صناعي","ALK":"🏭 صناعي",
    "CCL":"🏭 صناعي","RCL":"🏭 صناعي","NCLH":"🏭 صناعي",
    # ── اتصالات وميديا
    "TMUS":"📡 اتصالات","NFLX":"📡 اتصالات","DIS":"📡 اتصالات",
    "WBD":"📡 اتصالات","PARA":"📡 اتصالات","SPOT":"📡 اتصالات",
    "TTWO":"📡 اتصالات","EA":"📡 اتصالات","ATVI":"📡 اتصالات",
    # ── مواد
    "NEM":"⛏ مواد","FCX":"⛏ مواد","ALB":"⛏ مواد","MP":"⛏ مواد",
    "AA":"⛏ مواد","X":"⛏ مواد","CLF":"⛏ مواد","VALE":"⛏ مواد",
    "RIO":"⛏ مواد","BHP":"⛏ مواد","GOLD":"⛏ مواد","KGC":"⛏ مواد",
    # ── سيارات وEV
    "RIVN":"🚗 سيارات","LCID":"🚗 سيارات","NIO":"🚗 سيارات",
    "XPEV":"🚗 سيارات","LI":"🚗 سيارات","F":"🚗 سيارات","GM":"🚗 سيارات",
    # ── عقارات
    "PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات",
    "AMT":"🏢 عقارات","EQIX":"🏢 عقارات","DLR":"🏢 عقارات",
    # ── عملات مشفرة ذات صلة
    "COIN":"🪙 كريبتو","MSTR":"🪙 كريبتو","MARA":"🪙 كريبتو",
    "RIOT":"🪙 كريبتو","HUT":"🪙 كريبتو","CLSK":"🪙 كريبتو",
}


# ═══════════════════════════════════════════════
# إرسال تيليجرام
# ═══════════════════════════════════════════════

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ إرسال: {e}")

# ═══════════════════════════════════════════════
# جلب البيانات
# ═══════════════════════════════════════════════

def get_data(symbol, interval):
    period_map = {
        "1h":  "60d",
        "4h":  "60d",
        "1d":  "2y",
        "1wk": "5y",
    }
    period = period_map.get(interval, "1y")
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

# ═══════════════════════════════════════════════
# المساعدات التحليلية
# ═══════════════════════════════════════════════

def find_key_levels(df, zone_pct=0.003, min_touches=2):
    """
    يلتقط المستويات الأفقية القوية بطريقتين مدمجتين:

    ① القمم والقيعان البارزة (swing highs/lows)
    ② المستويات الأفقية التي لمسها السعر مرات متعددة
       — يبحث في highs و lows عن تجمع أسعار في نطاق ضيق (±0.3%)
       — هذا يلتقط مستويات مثل 161 في RDDT حتى لو مش قمة بارزة

    الشرط: كل مستوى لازم يُلمس مرتين على الأقل
    """
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    closes = df["Close"].squeeze().values
    opens  = df["Open"].squeeze().values
    n = len(highs)

    # ── ① قمم وقيعان بارزة (lookback=10)
    lookback = 10
    raw = []
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback]):
            raw.append(("resistance", float(highs[i])))
        if lows[i] == min(lows[i-lookback:i+lookback]):
            raw.append(("support", float(lows[i])))

    # ── ② مستويات أفقية من تجمع highs و lows
    all_prices = [(float(h), "resistance") for h in highs] +                  [(float(l), "support")    for l in lows]
    all_prices.sort(key=lambda x: x[0])

    # اجمع الأسعار المتقاربة في مستوى واحد
    horizontal = []
    visited = [False] * len(all_prices)
    for i in range(len(all_prices)):
        if visited[i]: continue
        price_i, type_i = all_prices[i]
        zone = price_i * zone_pct
        cluster = [price_i]
        types   = [type_i]
        for j in range(i+1, len(all_prices)):
            if visited[j]: continue
            price_j, type_j = all_prices[j]
            if abs(price_j - price_i) <= zone:
                cluster.append(price_j)
                types.append(type_j)
                visited[j] = True
            elif price_j > price_i + zone:
                break
        visited[i] = True
        if len(cluster) >= min_touches:
            avg_price = sum(cluster) / len(cluster)
            # حدد النوع بالأغلبية
            res_count = types.count("resistance")
            sup_count = types.count("support")
            level_type = "resistance" if res_count >= sup_count else "support"
            horizontal.append((level_type, avg_price))

    # ── دمج النتيجتين وإزالة المكررات
    combined = raw + horizontal
    final = []
    used  = set()
    for i, (lt, lp) in enumerate(combined):
        if i in used: continue
        zone = lp * zone_pct * 2
        group = [(lt, lp)]
        for j, (jt, jp) in enumerate(combined):
            if j <= i or j in used: continue
            if abs(jp - lp) <= zone:
                group.append((jt, jp))
                used.add(j)
        used.add(i)
        # الأغلبية تحدد النوع
        r = sum(1 for t,_ in group if t=="resistance")
        s = sum(1 for t,_ in group if t=="support")
        avg = sum(p for _,p in group) / len(group)
        final.append(("resistance" if r >= s else "support", avg))

    return final

def is_hammer(o, h, l, c):
    body  = abs(c - o)
    total = h - l
    if total == 0: return False
    return (min(o, c) - l) >= 2 * body and (h - max(o, c)) <= body * 0.5 and c > o

def is_bearish_candle(o, h, l, c):
    body  = abs(c - o)
    total = h - l
    if total == 0: return False
    return c < o and body >= total * 0.5

def find_trendline(df, n=30, tol=0.005):
    """
    ابحث عن ترند صاعد (خط يربط القيعان) وهابط (خط يربط القمم).
    يعيد (نوع الترند, السعر_عند_آخر_شمعة, slope, intercept) أو None
    """
    closes = df["Close"].squeeze().values
    lows   = df["Low"].squeeze().values
    highs  = df["High"].squeeze().values
    if len(closes) < n + 5:
        return []

    results = []
    seg_closes = closes[-n:]
    seg_lows   = lows[-n:]
    seg_highs  = highs[-n:]
    x = np.arange(len(seg_closes))

    # ── ترند صاعد: خط الانحدار للقيعان
    slope_l, intercept_l, r_l, _, _ = stats.linregress(x, seg_lows)
    if slope_l > 0 and r_l ** 2 > 0.55:
        trendline_now = intercept_l + slope_l * (len(seg_closes) - 1)
        prev_close    = float(closes[-2])
        curr_close    = float(closes[-1])
        margin        = trendline_now * tol
        # كسر ترند صاعد: السعر كان فوقه وكسره للأسفل
        if prev_close > trendline_now + margin and curr_close < trendline_now - margin:
            results.append(("trendline_break", "bear", trendline_now, curr_close))

    # ── ترند هابط: خط الانحدار للقمم
    slope_h, intercept_h, r_h, _, _ = stats.linregress(x, seg_highs)
    if slope_h < 0 and r_h ** 2 > 0.55:
        trendline_now = intercept_h + slope_h * (len(seg_closes) - 1)
        prev_close    = float(closes[-2])
        curr_close    = float(closes[-1])
        margin        = trendline_now * tol
        # اختراق ترند هابط: السعر كان تحته واخترق للأعلى
        if prev_close < trendline_now - margin and curr_close > trendline_now + margin:
            results.append(("trendline_break", "bull", trendline_now, curr_close))

    return results

# ═══════════════════════════════════════════════
# ① تبادل الأدوار
# ═══════════════════════════════════════════════

def get_role_reversal(df, tf):
    """
    تبادل الأدوار — 3 مراحل:

    المرحلة ① اختراق تاريخي:
      - في نافذة [-60:-20]: السعر كان تحت المستوى ثم اخترقه وصعد 5%+
      - ظل فوق المستوى 5 شمعات على الأقل (تأكيد الاتجاه)

    المرحلة ② تصحيح:
      - في نافذة [-20:-1]: السعر نزل من القمة باتجاه المستوى
      - ما كسر المستوى للأسفل (لا يزال فوقه)

    المرحلة ③ إعادة الاختبار (الشمعة الحالية):
      - C[t-1] > R  (الشمعة السابقة فوق المستوى)
      - L[t]  ≤ R  (ظل الشمعة الحالية لمس المستوى)
      - C[t]  > R  (الإغلاق فوق المستوى = ارتداد ناجح)
    """
    closes = df["Close"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    n = len(closes)
    if n < 65: return []

    c_curr = float(closes.iloc[-1])
    c_prev = float(closes.iloc[-2])
    h_curr = float(highs.iloc[-1])
    l_curr = float(lows.iloc[-1])

    results = []

    for level_type, level_price in find_key_levels(df):
        tol      = level_price * 0.002   # تسامح ±0.2%
        min_move = level_price * 0.05    # 5% ابتعاد بعد الاختراق

        if level_type == "resistance":
            R = level_price

            # ── المرحلة ① اختراق تاريخي في نافذة [-60:-20]
            broke_above    = False
            peak_price     = 0.0
            candles_above  = 0
            for i in range(-60, -20):
                ci = float(closes.iloc[i])
                hi = float(highs.iloc[i])
                if ci > R + tol:
                    broke_above = True
                if broke_above:
                    candles_above += 1
                    if hi > peak_price:
                        peak_price = hi

            if not broke_above: continue
            if candles_above < 5: continue           # لازم يظل فوقه 5+ شمعات
            if peak_price < R + min_move: continue   # لازم يبتعد 5%+

            # ── المرحلة ② تصحيح في نافذة [-20:-1]
            # السعر نزل من القمة لكن ما كسر المستوى
            correction_started = False
            broke_down         = False
            for i in range(-20, -1):
                ci = float(closes.iloc[i])
                if ci < peak_price * 0.98:   # بدأ ينزل من القمة
                    correction_started = True
                if ci < R - tol:             # كسر المستوى = مش تبادل أدوار
                    broke_down = True
                    break

            if not correction_started: continue  # ما فيه تصحيح
            if broke_down: continue              # كسر المستوى = إشارة خاطئة

            # ── المرحلة ③ إعادة الاختبار (الشمعة الحالية)
            # C[t-1] > R  و  L[t] ≤ R+tol  و  C[t] > R
            if (c_prev > R
                    and l_curr <= R + tol
                    and c_curr > R):
                results.append(("role_reversal", "bull", R, c_curr, tf))

        elif level_type == "support":
            S = level_price

            # ── المرحلة ① كسر تاريخي في نافذة [-60:-20]
            broke_below    = False
            trough_price   = float("inf")
            candles_below  = 0
            for i in range(-60, -20):
                ci = float(closes.iloc[i])
                li = float(lows.iloc[i])
                if ci < S - tol:
                    broke_below = True
                if broke_below:
                    candles_below += 1
                    if li < trough_price:
                        trough_price = li

            if not broke_below: continue
            if candles_below < 5: continue
            if trough_price > S - min_move: continue

            # ── المرحلة ② تصحيح (ارتداد من القاع باتجاه المستوى)
            bounce_started = False
            broke_up       = False
            for i in range(-20, -1):
                ci = float(closes.iloc[i])
                if ci > trough_price * 1.02:
                    bounce_started = True
                if ci > S + tol:
                    broke_up = True
                    break

            if not bounce_started: continue
            if broke_up: continue

            # ── المرحلة ③ إعادة الاختبار
            # C[t-1] < S  و  H[t] ≥ S-tol  و  C[t] < S
            if (c_prev < S
                    and h_curr >= S - tol
                    and c_curr < S):
                results.append(("role_reversal", "bear", S, c_curr, tf))

    return results[:1]


# ② اختراق/كسر بزخم عالٍ
# ═══════════════════════════════════════════════

def get_momentum_breakout(df, tf):
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    volumes = df["Volume"].squeeze()
    if len(closes) < 25: return []

    c_prev, c_curr, o_curr = float(closes.iloc[-2]), float(closes.iloc[-1]), float(opens.iloc[-1])
    avg_vol   = float(np.mean(volumes.values[-21:-1]))
    curr_vol  = float(volumes.iloc[-1])
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0

    avg_body   = float(np.mean([abs(float(closes.iloc[j]) - float(opens.iloc[j])) for j in range(-21,-1)]))
    curr_body  = abs(c_curr - o_curr)
    body_ratio = curr_body / avg_body if avg_body > 0 else 0

    if vol_ratio < 1.5 or body_ratio < 1.2: return []

    results = []
    for level_type, level_price in find_key_levels(df):
        margin = level_price * 0.005
        if level_type == "resistance" and c_prev < level_price and c_curr > level_price + margin:
            results.append(("momentum","bull", level_price, c_curr, tf, vol_ratio, body_ratio))
        elif level_type == "support" and c_prev > level_price and c_curr < level_price - margin:
            results.append(("momentum","bear", level_price, c_curr, tf, vol_ratio, body_ratio))
    return results[:1]

# ═══════════════════════════════════════════════
# ③ تقاطع المتوسطات MA50 & MA100
# ═══════════════════════════════════════════════

def get_ma_signals(df, tf):
    closes = df["Close"].squeeze()
    if len(closes) < 105: return []

    ma50  = closes.rolling(50).mean()
    ma100 = closes.rolling(100).mean()

    curr_c, prev_c   = float(closes.iloc[-1]),  float(closes.iloc[-2])
    curr_50,prev_50  = float(ma50.iloc[-1]),     float(ma50.iloc[-2])
    curr_100,prev_100= float(ma100.iloc[-1]),    float(ma100.iloc[-2])

    results = []
    # يجب أن يكون السعر تجاوز كلا المتوسطين معاً في نفس الشمعة
    crossed_up_50  = prev_c < prev_50  and curr_c > curr_50
    crossed_up_100 = prev_c < prev_100 and curr_c > curr_100
    crossed_dn_50  = prev_c > prev_50  and curr_c < curr_50
    crossed_dn_100 = prev_c > prev_100 and curr_c < curr_100

    if crossed_up_50 and curr_c > curr_100:
        results.append(("ma","bull","50+100",curr_50, curr_100, curr_c, tf))
    elif crossed_up_100 and curr_c > curr_50:
        results.append(("ma","bull","50+100",curr_50, curr_100, curr_c, tf))
    elif crossed_dn_50 and curr_c < curr_100:
        results.append(("ma","bear","50+100",curr_50, curr_100, curr_c, tf))
    elif crossed_dn_100 and curr_c < curr_50:
        results.append(("ma","bear","50+100",curr_50, curr_100, curr_c, tf))

    return results

# ═══════════════════════════════════════════════
# ④ كسر / اختراق خط الترند
# ═══════════════════════════════════════════════

def get_trendline_signals(df, tf):
    if len(df) < 35: return []
    signals = find_trendline(df, n=30)
    tagged  = []
    for sig in signals:
        stype, direction, trendline_val, curr_c = sig
        # ابحث عن أقرب مستوى دعم/مقاومة بعده
        levels = find_key_levels(df)
        closes = df["Close"].squeeze().values
        if direction == "bull":
            # المقاومة القادمة (أقرب مقاومة فوق السعر الحالي)
            resistances = sorted([lv for lt, lv in levels if lt == "resistance" and lv > curr_c])
            next_target = resistances[0] if resistances else curr_c * 1.03
        else:
            # الدعم القادم (أقرب دعم تحت السعر الحالي)
            supports = sorted([lv for lt, lv in levels if lt == "support" and lv < curr_c], reverse=True)
            next_target = supports[0] if supports else curr_c * 0.97
        tagged.append(("trendline_break", direction, trendline_val, curr_c, next_target, tf))
    return tagged[:1]

# ═══════════════════════════════════════════════
# ⑤ كلاستر فني
# ═══════════════════════════════════════════════

def find_supply_demand_zones(df, lookback=10, min_move=0.03):
    """
    منطقة طلب (Demand): شمعة صغيرة ثم صعود قوي 3%+ = منطقة شراء قوية
    منطقة عرض (Supply): شمعة صغيرة ثم هبوط قوي 3%+ = منطقة بيع قوية
    """
    closes = df["Close"].squeeze().values
    opens  = df["Open"].squeeze().values
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    n = len(closes)
    zones = []

    for i in range(lookback, n - lookback):
        base_body = abs(closes[i] - opens[i])
        base_range = highs[i] - lows[i]
        if base_range == 0: continue
        is_small = base_body / base_range < 0.4  # شمعة صغيرة (base)

        if not is_small: continue

        # فحص الحركة بعدها
        move_up   = (closes[i+1] - opens[i+1]) / closes[i] if closes[i] > 0 else 0
        move_down = (opens[i+1] - closes[i+1]) / closes[i] if closes[i] > 0 else 0

        zone_price = (highs[i] + lows[i]) / 2

        if move_up >= min_move:
            zones.append(("demand", float(zone_price), float(lows[i]), float(highs[i])))
        elif move_down >= min_move:
            zones.append(("supply", float(zone_price), float(lows[i]), float(highs[i])))

    return zones


def get_trendline_at_price(df, n=30):
    """يعيد سعر خط الترند الصاعد والهابط عند آخر شمعة"""
    from scipy import stats
    closes = df["Close"].squeeze().values
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    if len(closes) < n + 5:
        return None, None

    seg_lows  = lows[-n:]
    seg_highs = highs[-n:]
    x = np.arange(len(seg_lows))

    bull_tl = bear_tl = None

    slope_l, intercept_l, r_l, _, _ = stats.linregress(x, seg_lows)
    if slope_l > 0 and r_l**2 > 0.5:
        bull_tl = intercept_l + slope_l * (len(seg_lows) - 1)

    slope_h, intercept_h, r_h, _, _ = stats.linregress(x, seg_highs)
    if slope_h < 0 and r_h**2 > 0.5:
        bear_tl = intercept_h + slope_h * (len(seg_highs) - 1)

    return bull_tl, bear_tl


def get_cluster_zone(df, tf):
    """
    كلاستر فني حقيقي:
    يبحث عن تجمع عنصرين أو أكثر في نطاق ±1% من السعر الحالي

    عناصر الدعم (طلب):  دعم أفقي | MA50 | MA100 | ترند صاعد | منطقة طلب
    عناصر المقاومة:     مقاومة أفقية | MA50 | MA100 | ترند هابط | منطقة عرض

    الحالة تُحدد بناءً على:
    - إذا السعر اقترب من الأسفل = اختبار دعم = ارتداد محتمل
    - إذا السعر اقترب من الأعلى = اختبار مقاومة = رفض محتمل
    """
    closes = df["Close"].squeeze()
    if len(closes) < 110: return []

    curr_c = float(closes.iloc[-1])
    prev_c = float(closes.iloc[-2])
    margin = curr_c * 0.01  # نطاق ±1%

    ma50  = float(closes.rolling(50).mean().iloc[-1])
    ma100 = float(closes.rolling(100).mean().iloc[-1])
    bull_tl, bear_tl = get_trendline_at_price(df)
    levels = find_key_levels(df)
    sd_zones = find_supply_demand_zones(df)

    # ── بناء قائمة العناصر الداعمة للصعود (قريبة من السعر)
    bull_elements = []
    bear_elements = []

    for lt, lv in levels:
        if abs(lv - curr_c) <= margin * 3:
            if lt == "support":
                bull_elements.append(f"دعم أفقي ${lv:.2f}")
            else:
                bear_elements.append(f"مقاومة أفقية ${lv:.2f}")

    if abs(ma50 - curr_c) <= margin * 3:
        if curr_c >= ma50:
            bull_elements.append(f"MA 50 ${ma50:.2f}")
        else:
            bear_elements.append(f"MA 50 ${ma50:.2f}")

    if abs(ma100 - curr_c) <= margin * 3:
        if curr_c >= ma100:
            bull_elements.append(f"MA 100 ${ma100:.2f}")
        else:
            bear_elements.append(f"MA 100 ${ma100:.2f}")

    if bull_tl and abs(bull_tl - curr_c) <= margin * 3:
        bull_elements.append(f"ترند صاعد ${bull_tl:.2f}")

    if bear_tl and abs(bear_tl - curr_c) <= margin * 3:
        bear_elements.append(f"ترند هابط ${bear_tl:.2f}")

    for ztype, zprice, zlow, zhigh in sd_zones:
        if abs(zprice - curr_c) <= margin * 4:
            if ztype == "demand":
                bull_elements.append(f"منطقة طلب ${zprice:.2f}")
            else:
                bear_elements.append(f"منطقة عرض ${zprice:.2f}")

    # ── اتجاه السعر: من أين جاء؟
    coming_from_below = curr_c > prev_c  # صاعد = يختبر مقاومة
    coming_from_above = curr_c < prev_c  # هابط = يختبر دعم

    results = []

    # كلاستر صعودي: عنصرا دعم أو أكثر + السعر قادم من تحت
    if len(bull_elements) >= 2 and coming_from_above:
        zone_prices = [curr_c]
        results.append(("cluster", "bull",
                        min(zone_prices) * 0.99,
                        max(zone_prices) * 1.01,
                        bull_elements[:4], curr_c, tf))

    # كلاستر هبوطي: عنصرا مقاومة أو أكثر + السعر قادم من فوق
    elif len(bear_elements) >= 2 and coming_from_below:
        zone_prices = [curr_c]
        results.append(("cluster", "bear",
                        min(zone_prices) * 0.99,
                        max(zone_prices) * 1.01,
                        bear_elements[:4], curr_c, tf))

    return results


# ⑥ استراتيجية الدخول (RSI + SMA200 + OBV + ROC + Stochastic)
# ═══════════════════════════════════════════════

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float("inf"))
    return 100 - (100 / (1 + rs))

def calc_obv(closes, volumes):
    obv = [0.0]
    for i in range(1, len(closes)):
        c, pc, v = float(closes.iloc[i]), float(closes.iloc[i-1]), float(volumes.iloc[i])
        obv.append(obv[-1] + (v if c > pc else -v if c < pc else 0))
    return obv

def calc_stoch(closes, highs, lows, k_period=30, smooth_k=5, smooth_d=5):
    low_min  = lows.rolling(k_period).min()
    high_max = highs.rolling(k_period).max()
    raw_k    = 100 * (closes - low_min) / (high_max - low_min + 1e-10)
    k_line   = raw_k.rolling(smooth_k).mean()
    d_line   = k_line.rolling(smooth_d).mean()
    return k_line, d_line

def get_strategy_signal(sym):
    """
    نفس الشروط على 4 فريمات مستقلة: 15د | 30د | ساعة | يومي
    كل فريم يعطي إشارة مستقلة.

    الشروط (AND كلها على نفس الفريم):
      ① RSI(14) > 55 للـ CALL  /  < 45 للـ PUT
      ② السعر فوق/تحت SMA(200) على نفس الفريم
      ③ OBV يخترق قمته السابقة (CALL) / يكسر قاعه (PUT)
      ④ ROC% (5 أيام بوحدة الفريم) > 0 للـ CALL  /  < -8 للـ PUT
      ⑤ Stochastic(30,5,5): تقاطع صعودي تحت 50 (CALL) / هبوطي فوق 50 (PUT)
    """
    # إعدادات كل فريم: (interval, period_yf, tf_name, roc_candles, sma_period)
    timeframes = [
        ("15m", "60d",  "15 دقيقة", 96,  200),   # 96 شمعة 15د ≈ 1 يوم تداول
        ("30m", "60d",  "30 دقيقة", 80,  200),   # 80 شمعة 30د ≈ 5 أيام
        ("1h",  "60d",  "ساعة",     40,  200),   # 40 شمعة ساعة ≈ 5 أيام
        ("1d",  "2y",   "يومي",     5,   200),   # 5 شمعات يومية = أسبوع
    ]

    results = []

    for interval, period, tf_name, roc_candles, sma_p in timeframes:
        try:
            df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True)
            df.dropna(inplace=True)
            if len(df) < sma_p + 20:
                continue

            closes  = df["Close"].squeeze()
            highs   = df["High"].squeeze()
            lows    = df["Low"].squeeze()
            volumes = df["Volume"].squeeze()

            # ① RSI
            rsi_val = float(calc_rsi(closes).iloc[-1])

            # ② SMA 200
            sma_val   = float(closes.rolling(sma_p).mean().iloc[-1])
            price_now = float(closes.iloc[-1])

            # ③ OBV — يكفي أن OBV فوق متوسطه لآخر 20 شمعة (صعودي)
            obv      = calc_obv(closes, volumes)
            obv_curr = obv[-1]
            obv_ma20 = sum(obv[-20:]) / 20 if len(obv) >= 20 else obv_curr
            obv_bull = obv_curr > obv_ma20        # OBV فوق متوسطه = ضغط شراء
            obv_bear = obv_curr < obv_ma20        # OBV تحت متوسطه = ضغط بيع

            # ④ ROC
            if len(closes) > roc_candles:
                roc = (price_now - float(closes.iloc[-roc_candles])) / float(closes.iloc[-roc_candles]) * 100
            else:
                continue

            # ⑤ Stochastic
            k_line, d_line = calc_stoch(closes, highs, lows)
            k_curr = float(k_line.iloc[-1])
            k_prev = float(k_line.iloc[-2])
            d_curr = float(d_line.iloc[-1])
            d_prev = float(d_line.iloc[-2])
            stoch_bull = (k_prev < d_prev and k_curr > d_curr and k_curr < 50 and d_curr < 50)
            stoch_bear = (k_prev > d_prev and k_curr < d_curr and k_curr > 50 and d_curr > 50)

            # ── CALL
            if (rsi_val > 55
                    and price_now > sma_val
                    and obv_bull
                    and roc > 0
                    and stoch_bull):
                results.append(("strategy", "bull", rsi_val, sma_val, roc, k_curr, d_curr, price_now, tf_name))

            # ── PUT
            elif (rsi_val < 45
                    and price_now < sma_val
                    and obv_bear
                    and roc < -8
                    and stoch_bear):
                results.append(("strategy", "bear", rsi_val, sma_val, roc, k_curr, d_curr, price_now, tf_name))

        except Exception as e:
            print(f"    ⚠️ strategy {sym} {tf_name}: {e}")
            continue

    return results



SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━"

def msg_role_reversal(sym, sector, sig):
    _, direction, level, price, tf = sig
    if direction == "bull":
        header = f"🔄 <b>تبادل أدوار — {sym}</b>"
        state  = "🟢 تحوّل إلى مستوى دعم"
        lines  = "━━━ تحوّل لدعم ━━━"
    else:
        header = f"🔄 <b>تبادل أدوار — {sym}</b>"
        state  = "🔴 تحوّل إلى مستوى مقاومة"
        lines  = "▬▬▬ تحوّل لمقاومة ▬▬▬"
    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحالة: {state}\n"
        f"{lines}\n"
        f"المستوى: <b>${level:.2f}</b>\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>"
    )

def msg_momentum(sym, sector, sig):
    _, direction, level, price, tf, vr, br = sig
    if direction == "bull":
        header  = f"🚀 🟢 <b>اختراق بزخم عالٍ — {sym}</b>"
        event   = f"اختراق مقاومة قوية عند <b>${level:.2f}</b>"
        vol_lbl = "⚡⚡ انفجاري" if vr >= 3 else "⚡ عالٍ جداً"
        alert   = "⚠️⚠️⚠️ زخم صعودي قوي"
    else:
        header  = f"⚠️ 🔴 <b>كسر بزخم عالٍ — {sym}</b>"
        event   = f"كسر دعم قوي عند <b>${level:.2f}</b>"
        vol_lbl = "💣💣 بيوع مكثفة" if vr >= 3 else "💣 بيوع عالية"
        alert   = "⚠️⚠️⚠️ ضغط بيعي شديد"
    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحدث: {event}\n"
        f"📊 حجم التداول: <b>{vol_lbl}</b> (x{vr:.1f})\n"
        f"📏 حجم الجسم: x{br:.1f} عن المتوسط\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{alert}"
    )

def msg_ma(sym, sector, sig):
    _, direction, ma_label, ma50_val, ma100_val, price, tf = sig
    if direction == "bull":
        header = f"📈 🟢 <b>تقاطع متوسطات إيجابي — {sym}</b>"
        event  = "السعر يتجاوز MA 50 و MA 100 معاً ✅"
        stars  = "✨✨ إشراق فني ✨✨"
    else:
        header = f"📉 🔴 <b>تقاطع متوسطات سلبي — {sym}</b>"
        event  = "السعر يكسر ويهبط تحت MA 50 و MA 100 معاً ❌"
        stars  = "🌑🌑 تراجع فني 🌑🌑"
    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحدث: {event}\n"
        f"📌 MA 50:  <b>${ma50_val:.2f}</b>\n"
        f"📌 MA 100: <b>${ma100_val:.2f}</b>\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{stars}"
    )

def msg_trendline(sym, sector, sig):
    _, direction, trendline_val, price, next_target, tf = sig
    if direction == "bull":
        header = f"↗️ 🟢 <b>اختراق ترند هابط — {sym}</b>"
        status = f"السعر يخرج من المسار الهابط ↗️\nمستهدفاً المقاومة القادمة: <b>${next_target:.2f}</b>"
        arrow  = "   ↗️ ↗️ ↗️"
    else:
        header = f"↘️ 🔴 <b>كسر ترند صاعد — {sym}</b>"
        status = f"السعر يكسر خط الاتجاه الصاعد ↘️\nالحذر من تراجع إلى الدعم: <b>${next_target:.2f}</b>"
        arrow  = "   ↘️ ↘️ ↘️"
    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"{arrow}\n"
        f"خط الترند عند: <b>${trendline_val:.2f}</b>\n"
        f"{status}\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>"
    )

def msg_cluster(sym, sector, sig):
    _, direction, zone_low, zone_hi, components, price, tf = sig
    if direction == "bull":
        header   = f"🎯 🔲 <b>منطقة كلاستر فني — {sym}</b> 🔲"
        expected = "🟢 ارتداد صاعد محتمل 🟢"
        reaction = "⬆️ السعر يختبر قاع الكلاستر"
    else:
        header   = f"🎯 🔲 <b>منطقة كلاستر فني — {sym}</b> 🔲"
        expected = "🔴 كسر وهبوط عنيف محتمل 🔴"
        reaction = "⬇️ السعر يختبر سقف الكلاستر"
    comp_str = " + ".join(components)
    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"📍 نطاق الكلاستر:\n"
        f"   من: <b>${zone_low:.2f}</b>  →  إلى: <b>${zone_hi:.2f}</b>\n"
        f"🧩 المكونات: {comp_str}\n"
        f"{reaction}\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"الحالة المتوقعة: {expected}"
    )

def msg_strategy(sym, sector, sig):
    _, direction, rsi_val, sma200, roc, k, d, price, tf_name = sig
    if direction == "bull":
        header  = f"🎯 🟢 <b>إشارة دخول CALL — {sym}</b>\n📐 الفريم: <b>{tf_name}</b>"
        action  = "📈 شراء / CALL"
        rsi_lbl = f"🟢 {rsi_val:.1f} (فوق 55)"
        sma_lbl = "🟢 السعر فوق SMA 200"
        roc_lbl = f"🟢 ROC = {roc:.1f}% (إيجابي)"
        obv_lbl = "🟢 OBV يخترق القمة السابقة"
        st_lbl  = f"🟢 Stochastic تقاطع صعودي ({k:.1f}/{d:.1f})"
    else:
        header  = f"🎯 🔴 <b>إشارة دخول PUT — {sym}</b>\n📐 الفريم: <b>{tf_name}</b>"
        action  = "📉 بيع / PUT"
        rsi_lbl = f"🔴 {rsi_val:.1f} (تحت 45)"
        sma_lbl = "🔴 السعر تحت SMA 200"
        roc_lbl = f"🔴 ROC = {roc:.1f}% (سلبي)"
        obv_lbl = "🔴 OBV يكسر القاع السابق"
        st_lbl  = f"🔴 Stochastic تقاطع هبوطي ({k:.1f}/{d:.1f})"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"⚡ {action}\n"
        f"💰 السعر: <b>${price:.2f}</b>\n"
        f"\n<b>✅ الشروط المتحققة:</b>\n"
        f"① RSI(14): {rsi_lbl}\n"
        f"② SMA 200: {sma_lbl}\n"
        f"③ OBV: {obv_lbl}\n"
        f"④ ROC 30د: {roc_lbl}\n"
        f"⑤ Stochastic 30د: {st_lbl}"
    )


# ═══════════════════════════════════════════════
# إشعار تبادل الأدوار + Stochastic
# ═══════════════════════════════════════════════

def find_pivot_highs_lows(df, lookback=10):
    """يلتقط القمم والقيعان البارزة بـ lookback شمعة على كل جانب"""
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    closes = df["Close"].squeeze().values
    opens  = df["Open"].squeeze().values
    n = len(highs)
    pivots = []
    for i in range(lookback, n - lookback):
        # قمة بارزة
        if highs[i] == max(highs[i-lookback:i+lookback]):
            pivots.append(("resistance", float(highs[i]), i))
        # قاع بارز
        if lows[i] == min(lows[i-lookback:i+lookback]):
            pivots.append(("support", float(lows[i]), i))
    return pivots


def is_bullish_reversal(o, h, l, c):
    """
    شمعة انعكاس صعودي:
    - إغلاق فوق الافتتاح (شمعة خضراء) أو
    - ظل سفلي طويل (أكثر من 60% من المدى الكلي)
    """
    body  = abs(c - o)
    total = h - l
    lower_wick = min(o, c) - l
    if total == 0: return False
    return (c > o) or (lower_wick / total >= 0.6)


def is_bearish_reversal(o, h, l, c):
    """
    شمعة انعكاس هبوطي:
    - إغلاق تحت الافتتاح (شمعة حمراء) أو
    - ظل علوي طويل (أكثر من 60% من المدى الكلي)
    """
    body  = abs(c - o)
    total = h - l
    upper_wick = h - max(o, c)
    if total == 0: return False
    return (c < o) or (upper_wick / total >= 0.6)


def get_rr_stoch_signal(df, tf):
    """
    Resistance → Support (Breakout & Retest) — State Machine — Pandas

    State 0: ابحث عن مستوى مقاومة (أعلى High في نافذة 20 شمعة)
    State 1: اختراق — Close فوق res_level بـ 1%+ وثبت فوقه
             إلغاء فوري إذا أغلق تحت res_level
    State 2: Retest — Low دخل buffer zone [res_level, res_level*1.015]
             والإغلاق فوق res_level
             إلغاء فوري إذا أغلق تحت res_level
    State 3: تأكيد — شمعة صاعدة (Close > Open) بعد الـ retest
             ← إشارة حقيقية ✅

    كل الحسابات نسب مئوية (logarithmic-friendly)
    """
    closes = df["Close"].squeeze()
    opens  = df["Open"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    n = len(closes)
    if n < 50: return []

    # ── إعدادات
    PIVOT_WINDOW      = 20      # نافذة البحث عن المقاومة
    BREAKOUT_MIN_PCT  = 0.01    # 1% فوق المستوى للاختراق
    BUFFER_MAX_PCT    = 0.015   # 1.5% Buffer Zone فوق المستوى
    MAX_RETEST_BARS   = 15      # أقصى شمعات انتظار الـ retest
    MIN_BREAKOUT_BARS = 3       # أدنى شمعات فوق المستوى قبل الـ retest

    # ── Stochastic
    k_line, d_line = calc_stoch(closes, highs, lows, k_period=30, smooth_k=5, smooth_d=5)
    k_vals = k_line.values
    d_vals = d_line.values
    k_curr = float(k_vals[-1]) if not np.isnan(k_vals[-1]) else 50
    k_prev = float(k_vals[-2]) if not np.isnan(k_vals[-2]) else 50
    d_curr = float(d_vals[-1]) if not np.isnan(d_vals[-1]) else 50
    d_prev = float(d_vals[-2]) if not np.isnan(d_vals[-2]) else 50
    stoch_bull = (k_prev < d_prev and k_curr > d_curr and k_curr < 50 and d_curr < 50)
    stoch_bear = (k_prev > d_prev and k_curr < d_curr and k_curr > 50 and d_curr > 50)

    c = closes.values
    o = opens.values
    h = highs.values
    l = lows.values

    results = []

    # ── ابحث على نوافذ متحركة لإيجاد مستويات مقاومة
    # نفحص آخر 200 شمعة فقط للكفاءة
    scan_start = max(PIVOT_WINDOW, n - 200)

    for res_idx in range(scan_start, n - MIN_BREAKOUT_BARS - 2):
        # ① مستوى المقاومة = أعلى High في نافذة [res_idx-PIVOT_WINDOW : res_idx]
        window_start = max(0, res_idx - PIVOT_WINDOW)
        res_level    = float(np.max(h[window_start:res_idx + 1]))

        # ── State Machine
        state         = 0
        breakout_idx  = None
        retest_high   = None  # High شمعة الـ retest

        for i in range(res_idx + 1, n):
            ci = float(c[i])
            oi = float(o[i])
            hi = float(h[i])
            li = float(l[i])

            # ── حساب المسافة النسبية من المستوى
            dist_pct = (ci - res_level) / res_level  # موجب = فوق، سالب = تحت

            if state == 0:
                # State 0→1: اختراق واضح بـ 1%+
                if dist_pct >= BREAKOUT_MIN_PCT:
                    state        = 1
                    breakout_idx = i
                # لو أغلق تحت المستوى لا يزال = استمر البحث
                else:
                    continue

            elif state == 1:
                bars_since = i - breakout_idx

                # إلغاء فوري: أغلق تحت res_level
                if ci < res_level:
                    state = 0
                    breakout_idx = None
                    break

                # انتهت المهلة
                if bars_since > MAX_RETEST_BARS:
                    state = 0
                    break

                # انتظر MIN_BREAKOUT_BARS قبل الـ retest
                if bars_since < MIN_BREAKOUT_BARS:
                    continue

                # State 1→2: Low دخل الـ Buffer Zone
                # buffer: [res_level, res_level * (1 + BUFFER_MAX_PCT)]
                in_buffer = (li <= res_level * (1 + BUFFER_MAX_PCT) and
                             li >= res_level * 0.999)

                if in_buffer:
                    # إغلاق فوق res_level = retest ناجح
                    if ci >= res_level:
                        state       = 2
                        retest_high = hi
                    # إغلاق تحت res_level = إلغاء
                    else:
                        state = 0
                        break

            elif state == 2:
                # إلغاء: أغلق تحت res_level
                if ci < res_level:
                    state = 0
                    break

                # State 2→3: تأكيد الارتداد
                # شمعة صاعدة + إغلاق فوق High شمعة الـ retest
                if ci > oi and ci > retest_high:
                    # ✅ إشارة كاملة — فقط إذا كانت آخر شمعة أو قريبة منها
                    if i >= n - 3:  # الإشارة حديثة (آخر 3 شمعات)
                        full = stoch_bull
                        results.append((
                            "rr_stoch", "bull",
                            res_level, ci, tf,
                            full, k_curr, d_curr
                        ))
                    state = 0
                    break

    # ── نفس المنطق للـ Support→Resistance (هبوطي)
    for sup_idx in range(scan_start, n - MIN_BREAKOUT_BARS - 2):
        window_start = max(0, sup_idx - PIVOT_WINDOW)
        sup_level    = float(np.min(l[window_start:sup_idx + 1]))

        state        = 0
        breakdown_idx = None
        retest_low    = None

        for i in range(sup_idx + 1, n):
            ci = float(c[i])
            oi = float(o[i])
            hi = float(h[i])
            li = float(l[i])

            dist_pct = (sup_level - ci) / sup_level

            if state == 0:
                if dist_pct >= BREAKOUT_MIN_PCT:
                    state         = 1
                    breakdown_idx = i
                else:
                    continue

            elif state == 1:
                bars_since = i - breakdown_idx
                if ci > sup_level:
                    state = 0
                    break
                if bars_since > MAX_RETEST_BARS:
                    state = 0
                    break
                if bars_since < MIN_BREAKOUT_BARS:
                    continue

                in_buffer = (hi >= sup_level * (1 - BUFFER_MAX_PCT) and
                             hi <= sup_level * 1.001)
                if in_buffer:
                    if ci <= sup_level:
                        state      = 2
                        retest_low = li
                    else:
                        state = 0
                        break

            elif state == 2:
                if ci > sup_level:
                    state = 0
                    break
                if ci < oi and ci < retest_low:
                    if i >= n - 3:
                        full = stoch_bear
                        results.append((
                            "rr_stoch", "bear",
                            sup_level, ci, tf,
                            full, k_curr, d_curr
                        ))
                    state = 0
                    break

    # أعد أقوى إشارة فقط (الأحدث)
    return results[-1:] if results else []


def msg_rr_stoch(sym, sector, sig):
    _, direction, level, price, tf, full, k, d = sig
    if direction == "bull":
        if full:
            header = f"✅✅ <b>إشارة كاملة CALL — {sym}</b>"
            status = "🟢 تبادل أدوار + Stochastic صعودي"
            stoch  = f"🟢 Stochastic تقاطع صعودي ({k:.1f}/{d:.1f}) تحت 50"
        else:
            header = f"⚠️ <b>تبادل أدوار — {sym}</b>"
            status = "🟢 تبادل أدوار صعودي — تحقق شرط واحد"
            stoch  = f"⏳ Stochastic لم يتقاطع بعد ({k:.1f}/{d:.1f})"
        rr_txt = f"المقاومة تحوّلت دعماً عند <b>${level:.2f}</b>"
    else:
        if full:
            header = f"✅✅ <b>إشارة كاملة PUT — {sym}</b>"
            status = "🔴 تبادل أدوار + Stochastic هبوطي"
            stoch  = f"🔴 Stochastic تقاطع هبوطي ({k:.1f}/{d:.1f}) فوق 50"
        else:
            header = f"⚠️ <b>تبادل أدوار — {sym}</b>"
            status = "🔴 تبادل أدوار هبوطي — تحقق شرط واحد"
            stoch  = f"⏳ Stochastic لم يتقاطع بعد ({k:.1f}/{d:.1f})"
        rr_txt = f"الدعم تحوّل مقاومة عند <b>${level:.2f}</b>"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحالة: {status}\n"
        f"🔄 {rr_txt}\n"
        f"📊 {stoch}\n"
        f"💰 السعر: <b>${price:.2f}</b>"
    )

# ═══════════════════════════════════════════════
# الفحص الرئيسي
# ═══════════════════════════════════════════════

def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص")
    total = 0

    # الفريمات لكل نوع تحليل
    tf_role_mom  = [("1h","ساعة"), ("4h","4 ساعات"), ("1d","يومي")]
    tf_ma        = [("1d","يومي"), ("1wk","أسبوعي")]
    tf_trend     = [("1d","يومي")]
    tf_rr_stoch  = [("30m","30 دقيقة"), ("1h","ساعة"), ("4h","4 ساعات"), ("1d","يومي"), ("1wk","أسبوعي")]

    for sym, sector in STOCKS.items():
        messages_to_send = []
        try:
            # ── فلتر: السهم لازم فوق MA50 و MA100 على اليومي
            try:
                df_f = get_data(sym, "1d")
                if df_f.empty or len(df_f) < 105:
                    print(f"  — {sym}: بيانات غير كافية")
                    continue
                c_f     = df_f["Close"].squeeze()
                ma50_f  = float(c_f.rolling(50).mean().iloc[-1])
                ma100_f = float(c_f.rolling(100).mean().iloc[-1])
                price_f = float(c_f.iloc[-1])
                if price_f < ma50_f or price_f < ma100_f:
                    print(f"  — {sym}: تحت MA50/MA100، تخطي")
                    continue
            except Exception as fe:
                print(f"  — {sym}: خطأ فلتر {fe}")
                continue

            # ① تبادل الأدوار — ساعة / 4ساعات / يومي
            for interval, tf_name in tf_role_mom:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40: continue
                for sig in get_role_reversal(df, tf_name):
                    messages_to_send.append(msg_role_reversal(sym, sector, sig))

            # ② زخم عالٍ — ساعة / 4ساعات / يومي
            for interval, tf_name in tf_role_mom:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40: continue
                for sig in get_momentum_breakout(df, tf_name):
                    messages_to_send.append(msg_momentum(sym, sector, sig))

            # ③ تقاطع متوسطات — يومي + أسبوعي
            for interval, tf_name in tf_ma:
                df = get_data(sym, interval)
                if df.empty or len(df) < 110: continue
                for sig in get_ma_signals(df, tf_name):
                    messages_to_send.append(msg_ma(sym, sector, sig))

            # ④ خط الترند — يومي فقط
            for interval, tf_name in tf_trend:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40: continue
                for sig in get_trendline_signals(df, tf_name):
                    messages_to_send.append(msg_trendline(sym, sector, sig))

            # ⑤ كلاستر — محذوف، استُبدل بفلتر MA50+MA100

            # ⑥ استراتيجية (RSI + SMA200 + OBV + ROC + Stochastic)
            for sig in get_strategy_signal(sym):
                messages_to_send.append(msg_strategy(sym, sector, sig))

            # ⑦ تبادل أدوار + Stochastic
            for interval, tf_name in tf_rr_stoch:
                df = get_data(sym, interval)
                if df.empty or len(df) < 50: continue
                for sig in get_rr_stoch_signal(df, tf_name):
                    messages_to_send.append(msg_rr_stoch(sym, sector, sig))

            # إرسال كل رسالة بشكل منفصل
            if messages_to_send:
                for msg in messages_to_send:
                    send_telegram(msg)
                    time.sleep(0.8)
                print(f"  ✅ {sym} — {len(messages_to_send)} إشعار")
                total += 1
            else:
                print(f"  — {sym}: لا إشارات")

        except Exception as e:
            print(f"  ❌ {sym}: {e}")

    # رسالة ملخص
    summary = (
        f"🔍 <b>انتهى الفحص</b>\n"
        f"{SEPARATOR}\n"
        f"📦 الأسهم: {len(STOCKS)}\n"
        f"🕐 الفريمات: 1h + 4h + يومي + أسبوعي\n"
        f"✅ أسهم فيها إشارات: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ أسهم فيها إشارات: {total}")

# ═══════════════════════════════════════════════
# التشغيل
# ═══════════════════════════════════════════════

print("🚀 مراقبة الأسهم — النسخة المتقدمة v2")
print(f"الأسهم: {len(STOCKS)} | الفريمات: 1h + 4h + يومي + أسبوعي")
print("الإشعارات: تبادل أدوار | زخم | متوسطات | ترند | كلاستر")
print(f"وضع التشغيل: {'فحص واحد (--once)' if RUN_ONCE else 'مستمر (كل ساعة)'}\n")

check_all()

if not RUN_ONCE:
    schedule.every(1).hours.do(check_all)
    while True:
        schedule.run_pending()
        time.sleep(60)
