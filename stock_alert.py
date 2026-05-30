import yfinance as yf
import requests
import schedule
import time
import numpy as np

TOKEN   = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_ID = "615265045"

STOCKS = [
    # تكنولوجيا كبرى
    "AAPL","MSFT","NVDA","GOOGL","META","AMZN","TSLA","AMD","INTC","CRM",
    "ORCL","ADBE","QCOM","TXN","AMAT","MU","LRCX","KLAC","SNPS","CDNS",
    "PANW","CRWD","ZS","FTNT","NET","SNOW","DDOG","MDB","TEAM","NOW",
    "SHOP","SQ","PYPL","COIN","HOOD","RBLX","U","UNITY","PLTR","AI",
    "SMCI","ARM","AVGO","MRVL","ON","WOLF","ENPH","FSLR","SEDG","RUN",
    # مالية
    "JPM","BAC","GS","MS","WFC","C","BLK","AXP","V","MA",
    "COF","DFS","SYF","ALLY","SOFI","AFRM","UPST","LC","NRDS","OPEN",
    "ICE","CME","NDAQ","CBOE","SPGI","MCO","FDS","MSCI","BR","NTRS",
    # صحة وأدوية
    "JNJ","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","BIIB","VRTX",
    "REGN","MRNA","BNTX","NVAX","SGEN","ALNY","IONS","EXAS","ILMN","TMO",
    "DHR","ABT","MDT","SYK","BSX","EW","ISRG","ZBH","HOLX","DXCM",
    # طاقة
    "XOM","CVX","COP","EOG","PXD","DVN","MPC","VLO","PSX","HES",
    "OXY","APA","FANG","HAL","SLB","BKR","NOV","FTI","PTEN","RIG",
    # استهلاكي
    "WMT","TGT","COST","KR","DG","DLTR","EBAY","ETSY","W","CHWY",
    "MCD","SBUX","CMG","YUM","DPZ","QSR","JACK","DRI","TXRH","CAKE",
    "NKE","LULU","UAA","PVH","RL","TPR","CPRI","VFC","HBI","GIL",
    "KO","PEP","PM","MO","STZ","BUD","TAP","SAM","MNST","CELH",
    # صناعي ونقل
    "BA","LMT","RTX","NOC","GD","L3H","HII","TDG","HWM","SPR",
    "CAT","DE","EMR","ETN","PH","ROK","AME","CARR","TT","JCI",
    "UPS","FDX","DAL","UAL","AAL","LUV","JBLU","ALK","SAVE","HA",
    # عقارات واتصالات
    "AMT","CCI","EQIX","DLR","PLD","O","SPG","AVB","EQR","MAA",
    "T","VZ","TMUS","DISH","LUMN","FYBR","ATUS","CABO","WOW","CNSL",
    # ETF مؤشرات وقطاعات
    "SPY","QQQ","IWM","DIA","VTI","VOO","XLK","XLF","XLE","XLV",
    "XLI","XLY","XLP","XLU","XLB","XLRE","GLD","SLV","TLT","HYG",
]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

def get_data(symbol, interval):
    period = "60d" if interval == "1h" else "1y"
    df = yf.download(symbol, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def find_key_levels(df, lookback=15):
    closes = df["Close"].squeeze().values
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    levels = []
    for i in range(lookback, len(closes) - lookback):
        # قمة محلية (مقاومة)
        if highs[i] == max(highs[i-lookback:i+lookback]):
            levels.append(("resistance", float(highs[i])))
        # قاع محلي (دعم)
        if lows[i] == min(lows[i-lookback:i+lookback]):
            levels.append(("support", float(lows[i])))
    return levels

def is_hammer(o, h, l, c):
    """شمعة هامر — ذيل سفلي طويل وجسم صغير في الأعلى"""
    body   = abs(c - o)
    total  = h - l
    if total == 0:
        return False
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    return (lower_wick >= 2 * body and
            upper_wick <= body * 0.5 and
            c > o and
            total > 0)

def is_bearish_candle(o, h, l, c):
    """شمعة هبوطية واضحة — جسم أحمر كبير"""
    body  = abs(c - o)
    total = h - l
    if total == 0:
        return False
    return (c < o and
            body >= total * 0.5)

def is_high_momentum_breakout(df, level, direction, idx):
    """اختراق بزخم عالي — حجم أعلى من المتوسط وشمعة كبيرة"""
    volumes = df["Volume"].squeeze().values
    closes  = df["Close"].squeeze().values
    opens   = df["Open"].squeeze().values

    if idx < 20:
        return False, 0, 0

    avg_vol   = float(np.mean(volumes[idx-20:idx]))
    curr_vol  = float(volumes[idx])
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0

    candle_body = abs(float(closes[idx]) - float(opens[idx]))
    avg_body    = float(np.mean([abs(closes[j] - opens[j])
                                 for j in range(idx-20, idx)]))
    body_ratio  = candle_body / avg_body if avg_body > 0 else 0

    is_momentum = vol_ratio >= 1.5 and body_ratio >= 1.3
    return is_momentum, round(vol_ratio, 1), round(body_ratio, 1)

def check_role_reversal_pro(df, symbol, tf_name):
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    highs   = df["High"].squeeze()
    lows    = df["Low"].squeeze()
    volumes = df["Volume"].squeeze()
    alerts  = []
    levels  = find_key_levels(df)

    n = len(closes)
    if n < 30:
        return alerts

    # آخر 3 شمعات
    c0 = float(closes.iloc[-1]);  o0 = float(opens.iloc[-1])
    h0 = float(highs.iloc[-1]);   l0 = float(lows.iloc[-1])
    c1 = float(closes.iloc[-2]);  c2 = float(closes.iloc[-3])

    for level_type, level_price in levels:
        margin = level_price * 0.008  # 0.8%

        # ══════════════════════════════════════════════
        # تبادل إيجابي:
        # 1) اختراق المقاومة للأعلى (شمعة قبل أخيرة)
        # 2) رجع للمستوى (شمعة أخيرة قريبة منه)
        # 3) شمعة الهامر تؤكد الارتداد الصعودي
        # ══════════════════════════════════════════════
        if level_type == "resistance":
            broke_up   = c2 < level_price and c1 > level_price + margin
            touched_back = abs(l0 - level_price) <= margin * 2
            hammer     = is_hammer(o0, h0, l0, c0)

            if broke_up and touched_back and hammer:
                is_mom, vr, br = is_high_momentum_breakout(df, level_price, "up", n-2)
                alerts.append(
                    f"🟢 <b>تبادل أدوار صعودي — {symbol}</b>\n"
                    f"📊 الفريم: {tf_name}\n"
                    f"📍 المستوى: ${level_price:.2f}\n"
                    f"✅ اخترق المقاومة ← رجع ← هامر\n"
                    f"🔨 شمعة هامر تؤكد الدعم الجديد\n"
                    f"💰 السعر: ${c0:.2f}"
                    + (f"\n⚡ زخم الاختراق: حجم x{vr} | جسم x{br}" if is_mom else "")
                )

        # ══════════════════════════════════════════════
        # تبادل سلبي:
        # 1) كسر الدعم للأسفل
        # 2) رجع للمستوى
        # 3) شمعة هبوطية تؤكد المقاومة الجديدة
        # ══════════════════════════════════════════════
        elif level_type == "support":
            broke_down   = c2 > level_price and c1 < level_price - margin
            touched_back = abs(h0 - level_price) <= margin * 2
            bearish      = is_bearish_candle(o0, h0, l0, c0)

            if broke_down and touched_back and bearish:
                is_mom, vr, br = is_high_momentum_breakout(df, level_price, "down", n-2)
                alerts.append(
                    f"🔴 <b>تبادل أدوار هبوطي — {symbol}</b>\n"
                    f"📊 الفريم: {tf_name}\n"
                    f"📍 المستوى: ${level_price:.2f}\n"
                    f"❌ كسر الدعم ← رجع ← شمعة هبوطية\n"
                    f"🕯 شمعة حمراء تؤكد المقاومة الجديدة\n"
                    f"💰 السعر: ${c0:.2f}"
                    + (f"\n⚡ زخم الاختراق: حجم x{vr} | جسم x{br}" if is_mom else "")
                )

    return alerts[-1:] if alerts else []

def check_momentum_breakout(df, symbol, tf_name):
    """اختراقات بزخم عالي فقط — بدون شرط الرجوع"""
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    volumes = df["Volume"].squeeze()
    alerts  = []
    n = len(closes)
    if n < 25:
        return alerts

    levels = find_key_levels(df)
    c_prev = float(closes.iloc[-2])
    c_curr = float(closes.iloc[-1])
    o_curr = float(opens.iloc[-1])

    avg_vol  = float(np.mean(volumes.values[-21:-1]))
    curr_vol = float(volumes.iloc[-1])
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0

    avg_body = float(np.mean([abs(float(closes.iloc[j]) - float(opens.iloc[j]))
                               for j in range(-21, -1)]))
    curr_body = abs(c_curr - o_curr)
    body_ratio = curr_body / avg_body if avg_body > 0 else 0

    if vol_ratio < 2.0 or body_ratio < 1.5:
        return alerts

    for level_type, level_price in levels:
        margin = level_price * 0.005
        if level_type == "resistance" and c_prev < level_price and c_curr > level_price + margin:
            alerts.append(
                f"⚡ <b>اختراق بزخم عالي — {symbol}</b>\n"
                f"📊 الفريم: {tf_name}\n"
                f"📍 اخترق مقاومة: ${level_price:.2f}\n"
                f"📈 حجم x{vol_ratio:.1f} من المتوسط\n"
                f"💪 جسم الشمعة x{body_ratio:.1f} من المتوسط\n"
                f"💰 السعر: ${c_curr:.2f}"
            )
        elif level_type == "support" and c_prev > level_price and c_curr < level_price - margin:
            alerts.append(
                f"⚡ <b>كسر بزخم عالي — {symbol}</b>\n"
                f"📊 الفريم: {tf_name}\n"
                f"📍 كسر دعم: ${level_price:.2f}\n"
                f"📉 حجم x{vol_ratio:.1f} من المتوسط\n"
                f"💪 جسم الشمعة x{body_ratio:.1f} من المتوسط\n"
                f"💰 السعر: ${c_curr:.2f}"
            )

    return alerts[:1]

def check_all():
    print(f"\n⏰ جاري الفحص... {time.strftime('%H:%M:%S')}")
    total = 0
    timeframes = [("1h", "ساعة"), ("1d", "يومي")]

    for sym in STOCKS:
        for interval, tf_name in timeframes:
            try:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40:
                    continue

                alerts = []
                alerts += check_role_reversal_pro(df, sym, tf_name)
                alerts += check_momentum_breakout(df, sym, tf_name)

                for alert in alerts:
                    send_telegram(alert)
                    print(f"  ✅ {sym} ({tf_name})")
                    total += 1
                    time.sleep(1)

                if not alerts:
                    print(f"  — {sym} ({tf_name}): لا إشارة")

            except Exception as e:
                print(f"  ❌ {sym} ({tf_name}): {e}")

    send_telegram(
        f"🔍 انتهى الفحص\n"
        f"الأسهم: {len(STOCKS)} | ساعة + يومي\n"
        f"إشارات مرسلة: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\nإجمالي الإشارات: {total}")

print("🚀 مراقبة تبادل الأدوار الاحترافي")
print(f"الأسهم: {len(STOCKS)} | الفريمات: ساعة + يومي")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)

while True:
    schedule.run_pending()
    time.sleep(60)
