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
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا",
    "GOOGL":"💻 تكنولوجيا","META":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا",
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
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية",
    "WFC":"🏦 مالية","C":"🏦 مالية","BLK":"🏦 مالية","AXP":"🏦 مالية",
    "V":"🏦 مالية","MA":"🏦 مالية","COF":"🏦 مالية","PYPL":"🏦 مالية",
    "SQ":"🏦 مالية","COIN":"🏦 مالية","SPGI":"🏦 مالية","ICE":"🏦 مالية",
    "CME":"🏦 مالية","NDAQ":"🏦 مالية",
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة","TMO":"🏥 صحة",
    "DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة","ISRG":"🏥 صحة",
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "PXD":"⛽ طاقة","DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة",
    "OXY":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة","HES":"⛽ طاقة",
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","KO":"🛒 استهلاكي",
    "PEP":"🛒 استهلاكي","PM":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "BA":"🏭 صناعي","LMT":"🏭 صناعي","RTX":"🏭 صناعي","CAT":"🏭 صناعي",
    "DE":"🏭 صناعي","UPS":"🏭 صناعي","FDX":"🏭 صناعي","HON":"🏭 صناعي",
    "GE":"🏭 صناعي","NOC":"🏭 صناعي","GD":"🏭 صناعي",
    "AMT":"📡 اتصالات","T":"📡 اتصالات","VZ":"📡 اتصالات","TMUS":"📡 اتصالات",
    "PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات",
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","GLD":"📊 مؤشر",
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

def find_key_levels(df, lookback=15):
    highs = df["High"].squeeze().values
    lows  = df["Low"].squeeze().values
    levels = []
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback]):
            levels.append(("resistance", float(highs[i])))
        if lows[i] == min(lows[i-lookback:i+lookback]):
            levels.append(("support", float(lows[i])))
    return levels

def get_fibonacci_levels(df):
    """احسب مستويات فيبوناتشي على آخر موجة"""
    closes = df["Close"].squeeze().values
    if len(closes) < 50:
        return []
    window = closes[-50:]
    high = float(np.max(window))
    low  = float(np.min(window))
    diff = high - low
    ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
    fibs = []
    for r in ratios:
        fibs.append(("fib", round(r * 100, 1), high - diff * r))
    return fibs

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
    closes = df["Close"].squeeze()
    opens  = df["Open"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    if len(closes) < 30: return []

    c0,o0,h0,l0 = float(closes.iloc[-1]),float(opens.iloc[-1]),float(highs.iloc[-1]),float(lows.iloc[-1])
    c1,c2       = float(closes.iloc[-2]),float(closes.iloc[-3])
    results = []

    for level_type, level_price in find_key_levels(df):
        margin = level_price * 0.008
        if level_type == "resistance":
            if c2 < level_price and c1 > level_price + margin \
                    and abs(c0 - level_price) <= margin * 2:
                results.append(("role_reversal","bull", level_price, c0, tf))
        elif level_type == "support":
            if c2 > level_price and c1 < level_price - margin \
                    and abs(c0 - level_price) <= margin * 2:
                results.append(("role_reversal","bear", level_price, c0, tf))
    return results[:1]

# ═══════════════════════════════════════════════
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

def get_cluster_zone(df, tf):
    """
    يبحث عن تقاطع ≥ 2 عناصر فنية في نطاق سعري ضيق (±1%).
    العناصر: مستوى أفقي + MA50 + MA100 + فيبوناتشي
    """
    closes = df["Close"].squeeze()
    if len(closes) < 105: return []

    curr_c = float(closes.iloc[-1])
    margin = curr_c * 0.01  # نطاق ±1%

    levels  = find_key_levels(df)
    fibs    = get_fibonacci_levels(df)
    ma50    = float(closes.rolling(50).mean().iloc[-1])
    ma100   = float(closes.rolling(100).mean().iloc[-1])

    # اجمع كل المستويات الفنية مع تسمياتها
    all_levels = []
    for lt, lv in levels:
        label = "مقاومة أفقية" if lt == "resistance" else "دعم أفقي"
        all_levels.append((lv, label))
    for _, ratio, lv in fibs:
        all_levels.append((lv, f"فيبوناتشي {ratio}%"))
    all_levels.append((ma50,  "MA 50"))
    all_levels.append((ma100, "MA 100"))

    # ابحث عن المستويات القريبة من السعر الحالي
    nearby = [(lv, lbl) for lv, lbl in all_levels if abs(lv - curr_c) <= margin * 3]

    if len(nearby) < 2: return []

    # احسب النطاق
    prices   = [lv for lv, _ in nearby]
    zone_low = min(prices)
    zone_hi  = max(prices)
    labels   = [lbl for _, lbl in nearby]

    # تحديد الاتجاه المتوقع
    if curr_c > (zone_low + zone_hi) / 2:
        direction = "bear"  # سعر اقترب من أعلى الكلاستر = احتمال رفض
    else:
        direction = "bull"  # سعر اقترب من أسفل الكلاستر = احتمال ارتداد

    return [("cluster", direction, zone_low, zone_hi, labels[:4], curr_c, tf)]

# ═══════════════════════════════════════════════
# بناء رسائل منفصلة لكل نوع
# ═══════════════════════════════════════════════

SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━"

def msg_role_reversal(sym, sector, sig):
    _, direction, level, price, tf = sig
    if direction == "bull":
        header  = f"🔄 <b>تبادل أدوار — {sym}</b>"
        state   = "🟢 تحوّل إلى مستوى دعم"
        candle  = "🔨 شمعة هامر تأكيدية"
        lines_h = "▬▬▬ مقاومة سابقة ▬▬▬"
        lines_s = "━━━ تحوّل لدعم ━━━"
    else:
        header  = f"🔄 <b>تبادل أدوار — {sym}</b>"
        state   = "🔴 تحوّل إلى مستوى مقاومة"
        candle  = "🕯 شمعة حمراء تأكيدية"
        lines_h = "━━━ دعم سابق ━━━"
        lines_s = "▬▬▬ تحوّل لمقاومة ▬▬▬"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"{SEPARATOR}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحالة: {state}\n"
        f"{candle}\n"
        f"{SEPARATOR}\n"
        f"{lines_h}\n"
        f"   المستوى: <b>${level:.2f}</b>\n"
        f"{lines_s}\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{SEPARATOR}"
    )

def msg_momentum(sym, sector, sig):
    _, direction, level, price, tf, vr, br = sig
    if direction == "bull":
        header = f"🚀 🟢 <b>اختراق بزخم عالٍ — {sym}</b>"
        event  = f"اختراق مقاومة قوية عند <b>${level:.2f}</b>"
        vol_lbl = "⚡⚡ انفجاري" if vr >= 3 else "⚡ عالٍ جداً"
        alert = "⚠️⚠️⚠️ زخم صعودي قوي"
    else:
        header = f"⚠️ 🔴 <b>كسر بزخم عالٍ — {sym}</b>"
        event  = f"كسر دعم قوي عند <b>${level:.2f}</b>"
        vol_lbl = "💣💣 بيوع مكثفة" if vr >= 3 else "💣 بيوع عالية"
        alert = "⚠️⚠️⚠️ ضغط بيعي شديد"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"{SEPARATOR}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحدث: {event}\n"
        f"{SEPARATOR}\n"
        f"📊 حجم التداول: <b>{vol_lbl}</b> (x{vr:.1f})\n"
        f"📏 حجم الجسم:   x{br:.1f} عن المتوسط\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{SEPARATOR}\n"
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
        f"{SEPARATOR}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحدث: {event}\n"
        f"{SEPARATOR}\n"
        f"📌 MA 50:  <b>${ma50_val:.2f}</b>\n"
        f"📌 MA 100: <b>${ma100_val:.2f}</b>\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{SEPARATOR}\n"
        f"{stars}"
    )

def msg_trendline(sym, sector, sig):
    _, direction, trendline_val, price, next_target, tf = sig
    if direction == "bull":
        header = f"↗️ 🟢 <b>اختراق ترند هابط — {sym}</b>"
        status = f"السعر يخرج من المسار الهابط ↗️\nمستهدفاً المقاومة القادمة: <b>${next_target:.2f}</b>"
        arrow_art = "   ↗️ ↗️ ↗️"
    else:
        header = f"↘️ 🔴 <b>كسر ترند صاعد — {sym}</b>"
        status = f"السعر يكسر خط الاتجاه الصاعد ↘️\nالحذر من تراجع إلى الدعم: <b>${next_target:.2f}</b>"
        arrow_art = "   ↘️ ↘️ ↘️"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"{SEPARATOR}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"{arrow_art}\n"
        f"خط الترند عند: <b>${trendline_val:.2f}</b>\n"
        f"{SEPARATOR}\n"
        f"{status}\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{SEPARATOR}"
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
        f"╔══════════════════╗\n"
        f"║  🔲 CLUSTER ZONE  ║\n"
        f"╚══════════════════╝\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"{SEPARATOR}\n"
        f"📍 نطاق الكلاستر:\n"
        f"   من: <b>${zone_low:.2f}</b>  →  إلى: <b>${zone_hi:.2f}</b>\n"
        f"{SEPARATOR}\n"
        f"🧩 المكونات:\n"
        f"   {comp_str}\n"
        f"{SEPARATOR}\n"
        f"{reaction}\n"
        f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
        f"{SEPARATOR}\n"
        f"الحالة المتوقعة: {expected}"
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
