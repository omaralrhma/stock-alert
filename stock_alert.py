import yfinance as yf
import requests
import schedule
import time
import numpy as np

TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

# السهم: (القطاع)
STOCKS = {
    # تكنولوجيا
    "AAPL":  "💻 تكنولوجيا", "MSFT":  "💻 تكنولوجيا", "NVDA":  "💻 تكنولوجيا",
    "GOOGL": "💻 تكنولوجيا", "META":  "💻 تكنولوجيا", "AMZN":  "💻 تكنولوجيا",
    "TSLA":  "💻 تكنولوجيا", "AMD":   "💻 تكنولوجيا", "INTC":  "💻 تكنولوجيا",
    "CRM":   "💻 تكنولوجيا", "ORCL":  "💻 تكنولوجيا", "ADBE":  "💻 تكنولوجيا",
    "QCOM":  "💻 تكنولوجيا", "TXN":   "💻 تكنولوجيا", "AMAT":  "💻 تكنولوجيا",
    "MU":    "💻 تكنولوجيا", "LRCX":  "💻 تكنولوجيا", "KLAC":  "💻 تكنولوجيا",
    "SNPS":  "💻 تكنولوجيا", "CDNS":  "💻 تكنولوجيا", "PANW":  "💻 تكنولوجيا",
    "CRWD":  "💻 تكنولوجيا", "ZS":    "💻 تكنولوجيا", "FTNT":  "💻 تكنولوجيا",
    "NET":   "💻 تكنولوجيا", "SNOW":  "💻 تكنولوجيا", "DDOG":  "💻 تكنولوجيا",
    "MDB":   "💻 تكنولوجيا", "TEAM":  "💻 تكنولوجيا", "NOW":   "💻 تكنولوجيا",
    "SHOP":  "💻 تكنولوجيا", "PLTR":  "💻 تكنولوجيا", "AVGO":  "💻 تكنولوجيا",
    "MRVL":  "💻 تكنولوجيا", "ARM":   "💻 تكنولوجيا", "SMCI":  "💻 تكنولوجيا",
    # مالية
    "JPM":   "🏦 مالية", "BAC":   "🏦 مالية", "GS":    "🏦 مالية",
    "MS":    "🏦 مالية", "WFC":   "🏦 مالية", "C":     "🏦 مالية",
    "BLK":   "🏦 مالية", "AXP":   "🏦 مالية", "V":     "🏦 مالية",
    "MA":    "🏦 مالية", "COF":   "🏦 مالية", "DFS":   "🏦 مالية",
    "PYPL":  "🏦 مالية", "SQ":    "🏦 مالية", "COIN":  "🏦 مالية",
    "SPGI":  "🏦 مالية", "MCO":   "🏦 مالية", "ICE":   "🏦 مالية",
    "CME":   "🏦 مالية", "NDAQ":  "🏦 مالية",
    # صحة
    "JNJ":   "🏥 صحة", "PFE":   "🏥 صحة", "MRK":   "🏥 صحة",
    "ABBV":  "🏥 صحة", "LLY":   "🏥 صحة", "BMY":   "🏥 صحة",
    "AMGN":  "🏥 صحة", "GILD":  "🏥 صحة", "BIIB":  "🏥 صحة",
    "VRTX":  "🏥 صحة", "REGN":  "🏥 صحة", "MRNA":  "🏥 صحة",
    "TMO":   "🏥 صحة", "DHR":   "🏥 صحة", "ABT":   "🏥 صحة",
    "MDT":   "🏥 صحة", "SYK":   "🏥 صحة", "ISRG":  "🏥 صحة",
    "DXCM":  "🏥 صحة", "EW":    "🏥 صحة",
    # طاقة
    "XOM":   "⛽ طاقة", "CVX":   "⛽ طاقة", "COP":   "⛽ طاقة",
    "EOG":   "⛽ طاقة", "PXD":   "⛽ طاقة", "DVN":   "⛽ طاقة",
    "MPC":   "⛽ طاقة", "VLO":   "⛽ طاقة", "PSX":   "⛽ طاقة",
    "OXY":   "⛽ طاقة", "HAL":   "⛽ طاقة", "SLB":   "⛽ طاقة",
    "HES":   "⛽ طاقة", "FANG":  "⛽ طاقة", "APA":   "⛽ طاقة",
    # استهلاكي
    "WMT":   "🛒 استهلاكي", "TGT":   "🛒 استهلاكي", "COST":  "🛒 استهلاكي",
    "MCD":   "🛒 استهلاكي", "SBUX":  "🛒 استهلاكي", "CMG":   "🛒 استهلاكي",
    "NKE":   "🛒 استهلاكي", "LULU":  "🛒 استهلاكي", "KO":    "🛒 استهلاكي",
    "PEP":   "🛒 استهلاكي", "PM":    "🛒 استهلاكي", "MNST":  "🛒 استهلاكي",
    "DG":    "🛒 استهلاكي", "DLTR":  "🛒 استهلاكي", "YUM":   "🛒 استهلاكي",
    # صناعي
    "BA":    "🏭 صناعي", "LMT":   "🏭 صناعي", "RTX":   "🏭 صناعي",
    "CAT":   "🏭 صناعي", "DE":    "🏭 صناعي", "EMR":   "🏭 صناعي",
    "ETN":   "🏭 صناعي", "UPS":   "🏭 صناعي", "FDX":   "🏭 صناعي",
    "HON":   "🏭 صناعي", "GE":    "🏭 صناعي", "MMM":   "🏭 صناعي",
    "NOC":   "🏭 صناعي", "GD":    "🏭 صناعي", "TDG":   "🏭 صناعي",
    # اتصالات وعقارات
    "AMT":   "📡 اتصالات", "T":     "📡 اتصالات", "VZ":    "📡 اتصالات",
    "TMUS":  "📡 اتصالات", "CCI":   "📡 اتصالات", "EQIX":  "📡 اتصالات",
    "DLR":   "📡 اتصالات", "PLD":   "🏢 عقارات", "O":     "🏢 عقارات",
    "SPG":   "🏢 عقارات", "AVB":   "🏢 عقارات",
    # مؤشرات
    "SPY":   "📊 مؤشر", "QQQ":   "📊 مؤشر", "IWM":   "📊 مؤشر",
    "DIA":   "📊 مؤشر", "XLK":   "📊 مؤشر", "XLF":   "📊 مؤشر",
    "XLE":   "📊 مؤشر", "XLV":   "📊 مؤشر", "GLD":   "📊 مؤشر",
    "TLT":   "📊 مؤشر",
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ في الإرسال: {e}")

def get_data(symbol, interval):
    period = "60d" if interval == "1h" else ("2y" if interval == "1wk" else "1y")
    df = yf.download(symbol, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def above_ma(df, ma):
    closes = df["Close"].squeeze()
    if len(closes) < ma + 1:
        return False
    ma_val = closes.rolling(ma).mean().iloc[-1]
    return float(closes.iloc[-1]) > float(ma_val)

def check_ma_breakout(df, symbol, sector, tf_name, interval):
    """أسهم فوق MA50 و MA100 على اليومي والأسبوعي"""
    closes = df["Close"].squeeze()
    alerts = []
    if len(closes) < 105:
        return alerts

    ma50  = float(closes.rolling(50).mean().iloc[-1])
    ma100 = float(closes.rolling(100).mean().iloc[-1])
    prev50  = float(closes.rolling(50).mean().iloc[-2])
    prev100 = float(closes.rolling(100).mean().iloc[-2])
    curr  = float(closes.iloc[-1])
    prev  = float(closes.iloc[-2])

    # اختراق MA50 للأعلى
    if prev < prev50 and curr > ma50:
        alerts.append(
            f"🟢 <b>اختراق MA50 — {symbol}</b>\n"
            f"📊 الفريم: {tf_name}\n"
            f"🏷 القطاع: {sector}\n"
            f"📈 السهم كسر المتوسط 50\n"
            f"💰 السعر: ${curr:.2f} | MA50: ${ma50:.2f}"
        )
    # اختراق MA100 للأعلى
    if prev < prev100 and curr > ma100:
        alerts.append(
            f"🟢 <b>اختراق MA100 — {symbol}</b>\n"
            f"📊 الفريم: {tf_name}\n"
            f"🏷 القطاع: {sector}\n"
            f"📈 السهم كسر المتوسط 100\n"
            f"💰 السعر: ${curr:.2f} | MA100: ${ma100:.2f}"
        )
    # كسر MA50 للأسفل
    if prev > prev50 and curr < ma50:
        alerts.append(
            f"🔴 <b>كسر MA50 — {symbol}</b>\n"
            f"📊 الفريم: {tf_name}\n"
            f"🏷 القطاع: {sector}\n"
            f"📉 السهم كسر المتوسط 50 للأسفل\n"
            f"💰 السعر: ${curr:.2f} | MA50: ${ma50:.2f}"
        )
    # كسر MA100 للأسفل
    if prev > prev100 and curr < ma100:
        alerts.append(
            f"🔴 <b>كسر MA100 — {symbol}</b>\n"
            f"📊 الفريم: {tf_name}\n"
            f"🏷 القطاع: {sector}\n"
            f"📉 السهم كسر المتوسط 100 للأسفل\n"
            f"💰 السعر: ${curr:.2f} | MA100: ${ma100:.2f}"
        )
    return alerts

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

def is_hammer(o, h, l, c):
    body  = abs(c - o)
    total = h - l
    if total == 0: return False
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    return lower_wick >= 2 * body and upper_wick <= body * 0.5 and c > o

def is_bearish_candle(o, h, l, c):
    body  = abs(c - o)
    total = h - l
    if total == 0: return False
    return c < o and body >= total * 0.5

def check_role_reversal(df, symbol, sector, tf_name):
    closes = df["Close"].squeeze()
    opens  = df["Open"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    alerts = []
    n = len(closes)
    if n < 30: return alerts

    c0 = float(closes.iloc[-1]); o0 = float(opens.iloc[-1])
    h0 = float(highs.iloc[-1]);  l0 = float(lows.iloc[-1])
    c1 = float(closes.iloc[-2]); c2 = float(closes.iloc[-3])
    levels = find_key_levels(df)

    for level_type, level_price in levels:
        margin = level_price * 0.008
        if level_type == "resistance":
            broke_up     = c2 < level_price and c1 > level_price + margin
            touched_back = abs(l0 - level_price) <= margin * 2
            hammer       = is_hammer(o0, h0, l0, c0)
            if broke_up and touched_back and hammer:
                alerts.append(
                    f"🟢 <b>تبادل أدوار صعودي — {symbol}</b>\n"
                    f"📊 الفريم: {tf_name}\n"
                    f"🏷 القطاع: {sector}\n"
                    f"📍 المستوى: ${level_price:.2f}\n"
                    f"✅ اخترق المقاومة ← رجع ← هامر 🔨\n"
                    f"💰 السعر: ${c0:.2f}"
                )
        elif level_type == "support":
            broke_down   = c2 > level_price and c1 < level_price - margin
            touched_back = abs(h0 - level_price) <= margin * 2
            bearish      = is_bearish_candle(o0, h0, l0, c0)
            if broke_down and touched_back and bearish:
                alerts.append(
                    f"🔴 <b>تبادل أدوار هبوطي — {symbol}</b>\n"
                    f"📊 الفريم: {tf_name}\n"
                    f"🏷 القطاع: {sector}\n"
                    f"📍 المستوى: ${level_price:.2f}\n"
                    f"❌ كسر الدعم ← رجع ← شمعة هبوطية 🕯\n"
                    f"💰 السعر: ${c0:.2f}"
                )
    return alerts[-1:] if alerts else []

def check_momentum_breakout(df, symbol, sector, tf_name):
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    volumes = df["Volume"].squeeze()
    alerts  = []
    n = len(closes)
    if n < 25: return alerts

    levels   = find_key_levels(df)
    c_prev   = float(closes.iloc[-2])
    c_curr   = float(closes.iloc[-1])
    o_curr   = float(opens.iloc[-1])
    avg_vol  = float(np.mean(volumes.values[-21:-1]))
    curr_vol = float(volumes.iloc[-1])
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0
    avg_body  = float(np.mean([abs(float(closes.iloc[j]) - float(opens.iloc[j])) for j in range(-21, -1)]))
    curr_body = abs(c_curr - o_curr)
    body_ratio = curr_body / avg_body if avg_body > 0 else 0

    if vol_ratio < 2.0 or body_ratio < 1.5: return alerts

    for level_type, level_price in levels:
        margin = level_price * 0.005
        if level_type == "resistance" and c_prev < level_price and c_curr > level_price + margin:
            alerts.append(
                f"🟢 <b>اختراق بزخم — {symbol}</b>\n"
                f"📊 الفريم: {tf_name}\n"
                f"🏷 القطاع: {sector}\n"
                f"📍 كسر مقاومة: ${level_price:.2f}\n"
                f"📈 حجم x{vol_ratio:.1f} | جسم x{body_ratio:.1f}\n"
                f"💰 السعر: ${c_curr:.2f}"
            )
        elif level_type == "support" and c_prev > level_price and c_curr < level_price - margin:
            alerts.append(
                f"🔴 <b>كسر بزخم — {symbol}</b>\n"
                f"📊 الفريم: {tf_name}\n"
                f"🏷 القطاع: {sector}\n"
                f"📍 كسر دعم: ${level_price:.2f}\n"
                f"📉 حجم x{vol_ratio:.1f} | جسم x{body_ratio:.1f}\n"
                f"💰 السعر: ${c_curr:.2f}"
            )
    return alerts[:1]

def check_all():
    print(f"\n⏰ جاري الفحص... {time.strftime('%H:%M:%S')}")
    total = 0

    timeframes = [("1d", "يومي"), ("1wk", "أسبوعي")]

    for sym, sector in STOCKS.items():
        for interval, tf_name in timeframes:
            try:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40:
                    continue

                alerts = []
                alerts += check_role_reversal(df, sym, sector, tf_name)
                alerts += check_momentum_breakout(df, sym, sector, tf_name)
                alerts += check_ma_breakout(df, sym, sector, tf_name, interval)

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
        f"الأسهم: {len(STOCKS)} | يومي + أسبوعي\n"
        f"إشارات: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\nإجمالي: {total}")

print("🚀 مراقبة الأسهم — يومي وأسبوعي")
print(f"الأسهم: {len(STOCKS)}")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)
while True:
    schedule.run_pending()
    time.sleep(60)
