import yfinance as yf
import requests
import time
import numpy as np
import os
import sys
from scipy import stats

TOKEN    = os.environ.get("TG_TOKEN",  "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4")
_chats   = os.environ.get("TG_CHATS", "615265045,7775490993,5574232437")
CHAT_IDS = [c.strip() for c in _chats.split(",") if c.strip()]
RUN_ONCE = "--once" in sys.argv

# ═══════════════════════════════════════════════
# الأسهم — الأكثر تداولاً في الأوبشن
# ═══════════════════════════════════════════════
STOCKS = {
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
    "RBLX":"💻 تكنولوجيا","HUBS":"💻 تكنولوجيا","BILL":"💻 تكنولوجيا",
    "TWLO":"💻 تكنولوجيا","ZM":"💻 تكنولوجيا","DOCU":"💻 تكنولوجيا",
    "HOOD":"💻 تكنولوجيا","RDDT":"💻 تكنولوجيا","AFRM":"💻 تكنولوجيا",
    "SOFI":"💻 تكنولوجيا","UPST":"💻 تكنولوجيا","PLTR":"💻 تكنولوجيا",
    "AI":"💻 تكنولوجيا","SOUN":"💻 تكنولوجيا","IONQ":"💻 تكنولوجيا",
    "RGTI":"💻 تكنولوجيا","ACHR":"💻 تكنولوجيا","JOBY":"💻 تكنولوجيا",
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر",
    "XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر","XLV":"📊 مؤشر",
    "XLI":"📊 مؤشر","XLP":"📊 مؤشر","XLY":"📊 مؤشر","XLB":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","GDX":"📊 مؤشر","TLT":"📊 مؤشر",
    "TQQQ":"📊 مؤشر","SQQQ":"📊 مؤشر","SOXL":"📊 مؤشر","ARKK":"📊 مؤشر",
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة","TMO":"🏥 صحة",
    "DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة","ISRG":"🏥 صحة",
    "DXCM":"🏥 صحة","BSX":"🏥 صحة","BIIB":"🏥 صحة","HIMS":"🏥 صحة",
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة","OXY":"⛽ طاقة",
    "HAL":"⛽ طاقة","SLB":"⛽ طاقة","HES":"⛽ طاقة","PSX":"⛽ طاقة",
    "ENPH":"🌱 متجددة","FSLR":"🌱 متجددة","BE":"🌱 متجددة","PLUG":"🌱 متجددة",
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "ROST":"🛒 استهلاكي","TJX":"🛒 استهلاكي","HD":"🛒 استهلاكي",
    "LOW":"🛒 استهلاكي","ETSY":"🛒 استهلاكي","ULTA":"🛒 استهلاكي",
    "CAT":"🏭 صناعي","DE":"🏭 صناعي","UPS":"🏭 صناعي","FDX":"🏭 صناعي",
    "HON":"🏭 صناعي","GE":"🏭 صناعي","ETN":"🏭 صناعي","EMR":"🏭 صناعي",
    "DAL":"🏭 صناعي","UAL":"🏭 صناعي","AAL":"🏭 صناعي","CCL":"🏭 صناعي",
    "TMUS":"📡 اتصالات","NFLX":"📡 اتصالات","DIS":"📡 اتصالات","SPOT":"📡 اتصالات",
    "NEM":"⛏ مواد","FCX":"⛏ مواد","ALB":"⛏ مواد","AA":"⛏ مواد",
    "RIVN":"🚗 سيارات","LCID":"🚗 سيارات","NIO":"🚗 سيارات","F":"🚗 سيارات","GM":"🚗 سيارات",
    "COIN":"🪙 كريبتو","MSTR":"🪙 كريبتو","MARA":"🪙 كريبتو","RIOT":"🪙 كريبتو",
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
    period_map = {"15m":"60d","30m":"60d","1h":"60d","4h":"60d","1d":"2y","1wk":"5y"}
    period = period_map.get(interval, "1y")
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

# ═══════════════════════════════════════════════
# تبادل الأدوار الهيكلي الصارم
# ═══════════════════════════════════════════════
def detect_role_reversal(df, tf):
    """
    State Machine — تبادل الأدوار الهيكلي

    شروط القمة الهيكلية الصارمة:
    ① أعلى High مقارنة بـ 15 شمعة قبلها و15 شمعة بعدها (Pivot High حقيقي)
    ② فجوة زمنية لا تقل عن 20 شمعة بين القمة والاختراق
    ③ وادٍ واضح بين القمة والاختراق — هبوط 5%+ (يمنع التوحد الضيق)
    ④ الـ Retest لا يكون قبل 5 شمعات من الاختراق

    معادلة تبادل الأدوار (نسب مئوية):
    - اختراق: Close > res * 1.01 (1%+) وشمعة صاعدة
    - Retest:  Low في نطاق [res*0.992 , res*1.015]
               والإغلاق فوق res
    - تأكيد:  شمعة صاعدة تغلق فوق High شمعة الـ retest
    - إلغاء:  أي إغلاق تحت res في State 1 أو 2
    """
    closes = df["Close"].squeeze()
    opens  = df["Open"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    n      = len(closes)

    PIVOT_SIDE        = 15     # ① شمعات على كل جانب للـ pivot
    MIN_GAP_BARS      = 20     # ② فجوة زمنية بين القمة والاختراق
    VALLEY_DROP_PCT   = 0.05   # ③ هبوط 5%+ بين القمة والاختراق
    MIN_RETEST_BARS   = 5      # ④ أدنى شمعات بعد الاختراق للـ retest
    MAX_RETEST_BARS   = 20     # أقصى شمعات انتظار الـ retest
    BREAKOUT_MIN_PCT  = 0.010  # اختراق 1%+
    BUFFER_LOW_PCT    = 0.992  # حد أدنى الـ retest (0.8% تحت المستوى)
    BUFFER_HIGH_PCT   = 1.015  # حد أعلى الـ retest (1.5% فوق المستوى)

    if n < PIVOT_SIDE * 2 + MIN_GAP_BARS + MIN_RETEST_BARS + 5:
        return []

    c = closes.values
    o = opens.values
    h = highs.values
    l = lows.values

    results = []

    # ── ابحث عن Pivot Highs هيكلية
    for pi in range(PIVOT_SIDE, n - PIVOT_SIDE - MIN_GAP_BARS - 1):
        res = float(h[pi])

        # ① أعلى High بـ 15 شمعة يمين ويسار
        left_max  = float(np.max(h[pi - PIVOT_SIDE: pi]))
        right_max = float(np.max(h[pi + 1: pi + PIVOT_SIDE + 1]))
        if res <= left_max or res <= right_max:
            continue

        # ── State Machine بعد الـ pivot
        state          = 0
        breakout_idx   = None
        breakout_close = None
        retest_high    = None
        retest_close   = None
        valley_min     = res  # أدنى سعر بين القمة والاختراق

        for i in range(pi + 1, n):
            ci = float(c[i])
            oi = float(o[i])
            hi = float(h[i])
            li = float(l[i])

            if state == 0:
                # تتبع الوادي
                if li < valley_min:
                    valley_min = li

                # ② فجوة 20+ شمعة بين القمة والاختراق
                if i - pi < MIN_GAP_BARS:
                    continue

                # ③ لازم يكون في وادٍ واضح 5%+
                valley_drop = (res - valley_min) / res
                if valley_drop < VALLEY_DROP_PCT:
                    continue

                # اختراق: إغلاق فوق res بـ 1%+ وشمعة صاعدة
                dist = (ci - res) / res
                if dist >= BREAKOUT_MIN_PCT and ci > oi:
                    state          = 1
                    breakout_idx   = i
                    breakout_close = ci

                # إذا أغلق تحت القمة بكثير = الوادي يتعمق (عادي)
                elif ci < res * 0.85:
                    # القمة أصبحت قديمة جداً، توقف
                    break

            elif state == 1:
                bs = i - breakout_idx

                # إلغاء فوري: إغلاق تحت المستوى
                if ci < res:
                    state = 0; break

                # انتهت المهلة
                if bs > MAX_RETEST_BARS:
                    state = 0; break

                # ④ انتظر 5 شمعات على الأقل قبل الـ retest
                if bs < MIN_RETEST_BARS:
                    continue

                # Retest: Low دخل النطاق العازل
                in_buffer = (res * BUFFER_LOW_PCT <= li <= res * BUFFER_HIGH_PCT)
                if in_buffer:
                    if ci >= res:  # إغلاق فوق المستوى = retest ناجح
                        state        = 2
                        retest_close = ci
                        retest_high  = hi
                    else:          # إغلاق تحت = إلغاء
                        state = 0; break

            elif state == 2:
                # إلغاء
                if ci < res:
                    state = 0; break

                # تأكيد: شمعة صاعدة تغلق فوق High الـ retest
                if ci > oi and ci > retest_high:
                    if i >= n - 3:  # الإشارة حديثة (آخر 3 شمعات)
                        dist_r = abs(retest_close - res) / res * 100
                        valley_drop_pct = (res - valley_min) / res * 100
                        results.append({
                            "direction":      "bull",
                            "level":          res,
                            "valley_min":     valley_min,
                            "valley_drop":    valley_drop_pct,
                            "breakout_price": breakout_close,
                            "retest_price":   retest_close,
                            "current_price":  ci,
                            "dist_pct":       dist_r,
                            "tf":             tf,
                            "gap_bars":       breakout_idx - pi,
                        })
                    state = 0; break

    # ── نفس المنطق للـ Support → Resistance (هبوطي)
    for pi in range(PIVOT_SIDE, n - PIVOT_SIDE - MIN_GAP_BARS - 1):
        sup = float(l[pi])

        left_min  = float(np.min(l[pi - PIVOT_SIDE: pi]))
        right_min = float(np.min(l[pi + 1: pi + PIVOT_SIDE + 1]))
        if sup >= left_min or sup >= right_min:
            continue

        state          = 0
        breakdown_idx  = None
        breakout_close = None
        retest_low     = None
        retest_close   = None
        peak_max       = sup

        for i in range(pi + 1, n):
            ci = float(c[i])
            oi = float(o[i])
            hi = float(h[i])
            li = float(l[i])

            if state == 0:
                if hi > peak_max:
                    peak_max = hi

                if i - pi < MIN_GAP_BARS:
                    continue

                peak_rise = (peak_max - sup) / sup
                if peak_rise < VALLEY_DROP_PCT:
                    continue

                dist = (sup - ci) / sup
                if dist >= BREAKOUT_MIN_PCT and ci < oi:
                    state          = 1
                    breakdown_idx  = i
                    breakout_close = ci
                elif ci > sup * 1.15:
                    break

            elif state == 1:
                bs = i - breakdown_idx
                if ci > sup:
                    state = 0; break
                if bs > MAX_RETEST_BARS:
                    state = 0; break
                if bs < MIN_RETEST_BARS:
                    continue

                in_buffer = (sup * (2 - BUFFER_HIGH_PCT) <= hi <= sup * (2 - BUFFER_LOW_PCT))
                if in_buffer:
                    if ci <= sup:
                        state        = 2
                        retest_close = ci
                        retest_low   = li
                    else:
                        state = 0; break

            elif state == 2:
                if ci > sup:
                    state = 0; break
                if ci < oi and ci < retest_low:
                    if i >= n - 3:
                        dist_r     = abs(retest_close - sup) / sup * 100
                        peak_rise  = (peak_max - sup) / sup * 100
                        results.append({
                            "direction":      "bear",
                            "level":          sup,
                            "valley_min":     peak_max,
                            "valley_drop":    peak_rise,
                            "breakout_price": breakout_close,
                            "retest_price":   retest_close,
                            "current_price":  ci,
                            "dist_pct":       dist_r,
                            "tf":             tf,
                            "gap_bars":       breakdown_idx - pi,
                        })
                    state = 0; break

    return results[-1:] if results else []


def msg_role_reversal(sym, sector, sig):
    d   = sig["direction"]
    tf  = sig["tf"]
    lv  = sig["level"]
    bp  = sig["breakout_price"]
    rp  = sig["retest_price"]
    cp  = sig["current_price"]
    dist= sig["dist_pct"]
    vd  = sig["valley_drop"]
    gap = sig["gap_bars"]

    if d == "bull":
        header = f"✅ <b>تبادل أدوار صعودي — {sym}</b>"
        status = "🟢 مقاومة هيكلية → دعم"
        icon   = "🟢"
    else:
        header = f"✅ <b>تبادل أدوار هبوطي — {sym}</b>"
        status = "🔴 دعم هيكلي → مقاومة"
        icon   = "🔴"

    return (
        f"{header}\n"
        f"🏷 {sector}\n"
        f"📐 الفريم: <b>{tf}</b>\n"
        f"الحالة: {status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 المستوى الهيكلي: <b>${lv:.2f}</b>\n"
        f"🏔 عمق الوادي: <b>{vd:.1f}%</b> | فجوة: <b>{gap} شمعة</b>\n"
        f"🚀 سعر الاختراق:   <b>${bp:.2f}</b>\n"
        f"🔄 سعر الـ Retest: <b>${rp:.2f}</b>\n"
        f"💰 السعر الحالي:   <b>${cp:.2f}</b>\n"
        f"📏 البعد: <b>{dist:.2f}%</b>"
    )


# ═══════════════════════════════════════════════
# الفحص الرئيسي
# ═══════════════════════════════════════════════
def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')} — بدء الفحص")
    total = 0

    TIMEFRAMES = [
        ("15m",  "15 دقيقة"),
        ("30m",  "30 دقيقة"),
        ("1h",   "ساعة"),
        ("4h",   "4 ساعات"),
        ("1d",   "يومي"),
        ("1wk",  "أسبوعي"),
    ]

    for sym, sector in STOCKS.items():
        messages_to_send = []
        try:
            for interval, tf_name in TIMEFRAMES:
                df = get_data(sym, interval)
                if df.empty or len(df) < 80:
                    continue
                for sig in detect_role_reversal(df, tf_name):
                    messages_to_send.append(msg_role_reversal(sym, sector, sig))

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

    summary = (
        f"🔍 <b>انتهى الفحص</b>\n"
        f"الأسهم: {len(STOCKS)} | الفريمات: 15د + 30د + 1h + 4h + يومي + أسبوعي\n"
        f"✅ أسهم فيها إشارات: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ أسهم فيها إشارات: {total}")


print("🚀 بوت تبادل الأدوار الهيكلي")
print(f"الأسهم: {len(STOCKS)} | الفريمات: 15د + 30د + 1h + 4h + يومي + أسبوعي\n")

check_all()

if not RUN_ONCE:
    import schedule
    schedule.every(1).hours.do(check_all)
    while True:
        schedule.run_pending()
        time.sleep(60)
