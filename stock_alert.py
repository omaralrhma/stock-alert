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

# ═══════════════════════════════════════════════
# أسهم حلال فقط — محذوف: بنوك، تأمين، كحول، تبغ، أسلحة
# ═══════════════════════════════════════════════
STOCKS = {
    # ── تكنولوجيا ──
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا",
    "GOOGL":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا","TSLA":"💻 تكنولوجيا",
    "AMD":"💻 تكنولوجيا","INTC":"💻 تكنولوجيا","CRM":"💻 تكنولوجيا",
    "ORCL":"💻 تكنولوجيا","ADBE":"💻 تكنولوجيا","QCOM":"💻 تكنولوجيا",
    "TXN":"💻 تكنولوجيا","AMAT":"💻 تكنولوجيا","MU":"💻 تكنولوجيا",
    "LRCX":"💻 تكنولوجيا","KLAC":"💻 تكنولوجيا","SNPS":"💻 تكنولوجيا",
    "CDNS":"💻 تكنولوجيا","PANW":"💻 تكنولوجيا","CRWD":"💻 تكنولوجيا",
    "ZS":"💻 تكنولوجيا","FTNT":"💻 تكنولوجيا","NET":"💻 تكنولوجيا",
    "SNOW":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا","MDB":"💻 تكنولوجيا",
    "TEAM":"💻 تكنولوجيا","NOW":"💻 تكنولوجيا","SHOP":"💻 تكنولوجيا",
    "PLTR":"💻 تكنولوجيا","AVGO":"💻 تكنولوجيا","MRVL":"💻 تكنولوجيا",
    "ARM":"💻 تكنولوجيا","SMCI":"💻 تكنولوجيا","UBER":"💻 تكنولوجيا",
    "ABNB":"💻 تكنولوجيا","DASH":"💻 تكنولوجيا","RBLX":"💻 تكنولوجيا",
    "U":"💻 تكنولوجيا","GTLB":"💻 تكنولوجيا","HUBS":"💻 تكنولوجيا",

    # ── صحة وأدوية (بدون كحول أو تبغ) ──
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة","TMO":"🏥 صحة",
    "DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة","ISRG":"🏥 صحة",
    "DXCM":"🏥 صحة","IDXX":"🏥 صحة","BSX":"🏥 صحة","EW":"🏥 صحة",
    "ZBH":"🏥 صحة","PODD":"🏥 صحة","INSP":"🏥 صحة","NTRA":"🏥 صحة",

    # ── طاقة (نفط وغاز وطاقة متجددة) ──
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة",
    "HAL":"⛽ طاقة","SLB":"⛽ طاقة","HES":"⛽ طاقة",
    "ENPH":"🌱 طاقة متجددة","FSLR":"🌱 طاقة متجددة","RUN":"🌱 طاقة متجددة",
    "BE":"🌱 طاقة متجددة","PLUG":"🌱 طاقة متجددة","SEDG":"🌱 طاقة متجددة",

    # ── استهلاكي حلال (بدون كحول وتبغ) ──
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "EL":"🛒 استهلاكي","ULTA":"🛒 استهلاكي","ONON":"🛒 استهلاكي",
    "SKX":"🛒 استهلاكي","DECK":"🛒 استهلاكي","RH":"🛒 استهلاكي",

    # ── صناعي (بدون أسلحة) ──
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 صناعي",
    "FDX":"🏭 صناعي","HON":"🏭 صناعي","GE":"🏭 صناعي",
    "EMR":"🏭 صناعي","ETN":"🏭 صناعي","ROK":"🏭 صناعي",
    "PH":"🏭 صناعي","GNRC":"🏭 صناعي","XYL":"🏭 صناعي",

    # ── اتصالات ──
    "TMUS":"📡 اتصالات","NFLX":"📡 اتصالات","DIS":"📡 اتصالات",
    "WBD":"📡 اتصالات","PARA":"📡 اتصالات","SPOT":"📡 اتصالات",

    # ── مواد خام ──
    "NEM":"⛏ مواد","FCX":"⛏ مواد","ALB":"⛏ مواد","MP":"⛏ مواد",
    "AA":"⛏ مواد","X":"⛏ مواد","CLF":"⛏ مواد",

    # ── مؤشرات وذهب ──
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLE":"📊 مؤشر","GLD":"📊 مؤشر","SLV":"📊 مؤشر",
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

def find_key_levels(df, lookback=20, min_touches=2, zone_pct=0.008):
    """
    يلتقط فقط المستويات القوية والواضحة:
    - قمة أو قاع بارز (lookback=20 شمعة على كل جانب)
    - لمسه السعر مرتين على الأقل
    - الارتداد عنه واضح (body كبير)
    """
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    closes = df["Close"].squeeze().values
    opens  = df["Open"].squeeze().values
    n = len(highs)
    raw_levels = []

    # ① التقط القمم والقيعان البارزة
    for i in range(lookback, n - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback]):
            # تأكد أن الارتداد عنها قوي (جسم شمعة كبير)
            body = abs(closes[i] - opens[i])
            total = highs[i] - lows[i]
            if total > 0 and body / total >= 0.3:
                raw_levels.append(("resistance", float(highs[i]), i))
        if lows[i] == min(lows[i-lookback:i+lookback]):
            body = abs(closes[i] - opens[i])
            total = highs[i] - lows[i]
            if total > 0 and body / total >= 0.3:
                raw_levels.append(("support", float(lows[i]), i))

    # ② احتسب عدد مرات اللمس لكل مستوى
    strong_levels = []
    used = set()
    for idx, (ltype, lprice, li) in enumerate(raw_levels):
        if idx in used:
            continue
        zone = lprice * zone_pct
        touches = 1
        for jdx, (jtype, jprice, ji) in enumerate(raw_levels):
            if jdx == idx or jdx in used:
                continue
            if jtype == ltype and abs(jprice - lprice) <= zone:
                touches += 1
                used.add(jdx)
        # فقط المستويات التي لمسها السعر مرتين أو أكثر
        if touches >= min_touches:
            strong_levels.append((ltype, lprice))
        used.add(idx)

    return strong_levels

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
        tol      = level_price * 0.005   # تسامح ±0.5%
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

def get_strategy_signal(sym):
    """
    شروط CALL (AND كلها):
      ① RSI(14) يومي > 55
      ② السعر فوق SMA(200) يومي
      ③ OBV يومي فوق أعلى قمة OBV سابقة (breakout)
      ④ ROC% 30د (5 أيام) > 0

    شروط PUT (AND كلها):
      ① RSI(14) يومي < 45
      ② السعر تحت SMA(200) يومي
      ③ OBV يومي تحت أدنى قاع OBV سابق
      ④ ROC% 30د (5 أيام) < -8  (نسبة سلبية)

    شرط الدخول (OR — يضاف للفلتر):
      Stochastic(30, K=5, D=5) على 30د
      CALL: %K يتقاطع فوق %D وكلاهما تحت 50
      PUT:  %K يتقاطع تحت %D وكلاهما فوق 50
    """
    try:
        # ── جلب البيانات
        df_1d  = yf.download(sym, period="1y",  interval="1d",  progress=False, auto_adjust=True)
        df_30m = yf.download(sym, period="60d", interval="30m", progress=False, auto_adjust=True)
        df_1d.dropna(inplace=True)
        df_30m.dropna(inplace=True)

        if len(df_1d) < 210 or len(df_30m) < 50:
            return []

        closes_1d  = df_1d["Close"].squeeze()
        volume_1d  = df_1d["Volume"].squeeze()
        closes_30m = df_30m["Close"].squeeze()
        highs_30m  = df_30m["High"].squeeze()
        lows_30m   = df_30m["Low"].squeeze()

        # ── ① RSI يومي
        delta = closes_1d.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, float("inf"))
        rsi   = 100 - (100 / (1 + rs))
        rsi_val = float(rsi.iloc[-1])

        # ── ② SMA 200 يومي
        sma200    = float(closes_1d.rolling(200).mean().iloc[-1])
        price_1d  = float(closes_1d.iloc[-1])

        # ── ③ OBV يومي
        obv = [0.0]
        for i in range(1, len(closes_1d)):
            c  = float(closes_1d.iloc[i])
            pc = float(closes_1d.iloc[i-1])
            v  = float(volume_1d.iloc[i])
            obv.append(obv[-1] + (v if c > pc else -v if c < pc else 0))
        obv_curr     = obv[-1]
        obv_prev_max = max(obv[:-5])   # أعلى قمة OBV سابقة
        obv_prev_min = min(obv[:-5])   # أدنى قاع OBV سابق
        obv_breakout_bull = obv_curr > obv_prev_max
        obv_breakout_bear = obv_curr < obv_prev_min

        # ── ④ ROC% على 30 دقيقة (5 أيام = ~80 شمعة 30د)
        roc_period = 80
        if len(closes_30m) > roc_period:
            roc = (float(closes_30m.iloc[-1]) - float(closes_30m.iloc[-roc_period])) / float(closes_30m.iloc[-roc_period]) * 100
        else:
            return []

        # ── ⑤ Stochastic على 30 دقيقة (period=30, K_smooth=5, D_smooth=5)
        k_period = 30
        low_min  = lows_30m.rolling(k_period).min()
        high_max = highs_30m.rolling(k_period).max()
        raw_k    = 100 * (closes_30m - low_min) / (high_max - low_min + 1e-10)
        k_line   = raw_k.rolling(5).mean()    # Smooth K
        d_line   = k_line.rolling(5).mean()   # Smooth D

        k_curr = float(k_line.iloc[-1])
        k_prev = float(k_line.iloc[-2])
        d_curr = float(d_line.iloc[-1])
        d_prev = float(d_line.iloc[-2])

        # تقاطع %K فوق %D (ذيل ذهبي تحت 50)
        stoch_cross_bull = (k_prev < d_prev and k_curr > d_curr and k_curr < 50 and d_curr < 50)
        # تقاطع %K تحت %D (ذيل ميت فوق 50)
        stoch_cross_bear = (k_prev > d_prev and k_curr < d_curr and k_curr > 50 and d_curr > 50)

        price_30m = float(closes_30m.iloc[-1])
        results   = []

        # ── CALL: كل الشروط الـ4 + تقاطع ستوكاستك
        if (rsi_val > 55
                and price_1d > sma200
                and obv_breakout_bull
                and roc > 0
                and stoch_cross_bull):
            results.append(("strategy", "bull", rsi_val, sma200, roc, k_curr, d_curr, price_30m))

        # ── PUT: كل الشروط الـ4 + تقاطع ستوكاستك
        elif (rsi_val < 45
                and price_1d < sma200
                and obv_breakout_bear
                and roc < -8
                and stoch_cross_bear):
            results.append(("strategy", "bear", rsi_val, sma200, roc, k_curr, d_curr, price_30m))

        return results

    except Exception as e:
        print(f"    ⚠️ strategy error {sym}: {e}")
        return []


def msg_strategy(sym, sector, sig):
    _, direction, rsi_val, sma200, roc, k, d, price = sig
    if direction == "bull":
        header  = f"🎯 🟢 <b>إشارة دخول CALL — {sym}</b>"
        action  = "📈 شراء / CALL"
        rsi_lbl = f"🟢 {rsi_val:.1f} (فوق 55)"
        sma_lbl = "🟢 السعر فوق SMA 200"
        roc_lbl = f"🟢 ROC = {roc:.1f}% (إيجابي)"
        obv_lbl = "🟢 OBV يخترق القمة السابقة"
        st_lbl  = f"🟢 Stochastic تقاطع صعودي ({k:.1f}/{d:.1f})"
    else:
        header  = f"🎯 🔴 <b>إشارة دخول PUT — {sym}</b>"
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
# الفحص الرئيسي
# ═══════════════════════════════════════════════

def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص")
    total = 0

    # الفريمات لكل نوع تحليل
    tf_role_mom = [("1h","ساعة"), ("4h","4 ساعات"), ("1d","يومي")]
    tf_ma       = [("1d","يومي"), ("1wk","أسبوعي")]
    tf_trend    = [("1d","يومي")]
    tf_cluster  = [("1d","يومي")]

    for sym, sector in STOCKS.items():
        messages_to_send = []
        try:
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

            # ⑤ كلاستر فني — يومي فقط
            for interval, tf_name in tf_cluster:
                df = get_data(sym, interval)
                if df.empty or len(df) < 110: continue
                for sig in get_cluster_zone(df, tf_name):
                    messages_to_send.append(msg_cluster(sym, sector, sig))

            # ⑥ استراتيجية (RSI + SMA200 + OBV + ROC + Stochastic)
            for sig in get_strategy_signal(sym):
                messages_to_send.append(msg_strategy(sym, sector, sig))

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
