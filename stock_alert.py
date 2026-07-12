import yfinance as yf
import requests
import schedule
import time
import numpy as np

TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

STOCKS = {
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا",
    "GOOGL":"💻 تكنولوجيا","META":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا",
    "TSLA":"💻 تكنولوجيا","AMD":"💻 تكنولوجيا","INTC":"💻 تكنولوجيا",
    "CRM":"💻 تكنولوجيا","ORCL":"💻 تكنولوجيا","ADBE":"💻 تكنولوجيا",
    "QCOM":"💻 تكنولوجيا","AMAT":"💻 تكنولوجيا","MU":"💻 تكنولوجيا",
    "PANW":"💻 تكنولوجيا","CRWD":"💻 تكنولوجيا","NET":"💻 تكنولوجيا",
    "SNOW":"💻 تكنولوجيا","PLTR":"💻 تكنولوجيا","AVGO":"💻 تكنولوجيا",
    "ARM":"💻 تكنولوجيا","NOW":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا",
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية",
    "WFC":"🏦 مالية","V":"🏦 مالية","MA":"🏦 مالية","PYPL":"🏦 مالية",
    "COIN":"🏦 مالية","SPGI":"🏦 مالية","CME":"🏦 مالية",
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","AMGN":"🏥 صحة","VRTX":"🏥 صحة","ISRG":"🏥 صحة",
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","OXY":"⛽ طاقة",
    "SLB":"⛽ طاقة","MPC":"⛽ طاقة",
    "WMT":"🛒 استهلاكي","COST":"🛒 استهلاكي","MCD":"🛒 استهلاكي",
    "SBUX":"🛒 استهلاكي","NKE":"🛒 استهلاكي","KO":"🛒 استهلاكي",
    "BA":"🏭 صناعي","LMT":"🏭 صناعي","CAT":"🏭 صناعي","GE":"🏭 صناعي",
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","GLD":"📊 مؤشر",
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ: {e}")

def get_data(symbol, interval="1d"):
    period = "1y" if interval == "1d" else "2y"
    df = yf.download(symbol, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def get_stochastic(df, k=14, d=3):
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    closes = df["Close"].squeeze()
    lowest_low   = lows.rolling(k).min()
    highest_high = highs.rolling(k).max()
    k_line = 100 * (closes - lowest_low) / (highest_high - lowest_low)
    d_line = k_line.rolling(d).mean()
    return float(k_line.iloc[-1]), float(d_line.iloc[-1])

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

def get_gamma_exposure(sym, current_price):
    """
    يحسب Gamma Exposure تقريبي من Open Interest
    إيجابي = Calls > Puts عند المستوى (دعم للسعر)
    سلبي   = Puts > Calls عند المستوى (ضغط على السعر)
    """
    try:
        ticker = yf.Ticker(sym)
        expirations = ticker.options
        if not expirations:
            return None, None

        # أقرب انتهاء صلاحية
        exp = expirations[0]
        chain = ticker.option_chain(exp)
        calls = chain.calls
        puts  = chain.puts

        # فلتر الـ strikes القريبة من السعر الحالي (±5%)
        margin = current_price * 0.05
        calls_near = calls[
            (calls["strike"] >= current_price - margin) &
            (calls["strike"] <= current_price + margin)
        ]
        puts_near = puts[
            (puts["strike"] >= current_price - margin) &
            (puts["strike"] <= current_price + margin)
        ]

        total_call_oi = float(calls_near["openInterest"].sum())
        total_put_oi  = float(puts_near["openInterest"].sum())

        if total_call_oi + total_put_oi == 0:
            return None, None

        # نسبة Put/Call
        pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 999

        if pc_ratio < 0.7:
            gamma_dir = "positive"
            gamma_label = "🟢 إيجابية (Calls مسيطرة)"
        elif pc_ratio > 1.3:
            gamma_dir = "negative"
            gamma_label = "🔴 سلبية (Puts مسيطرة)"
        else:
            gamma_dir = "neutral"
            gamma_label = "⚪ محايدة"

        return gamma_dir, gamma_label

    except Exception:
        return None, None

def check_symbol(sym, sector):
    results = []

    # جلب البيانات
    df_1d = get_data(sym, "1d")
    if df_1d.empty or len(df_1d) < 50:
        return []

    closes = df_1d["Close"].squeeze()
    current_price = float(closes.iloc[-1])

    # Stochastic
    k, d = get_stochastic(df_1d)

    # تشبع بيع (oversold) أو شراء (overbought)
    oversold  = k < 25 and d < 25
    overbought = k > 75 and d > 75

    if not oversold and not overbought:
        return []

    stoch_dir = "bull" if oversold else "bear"
    stoch_label = f"🟢 تشبع بيع (K:{k:.0f} D:{d:.0f})" if oversold else f"🔴 تشبع شراء (K:{k:.0f} D:{d:.0f})"

    # هل السعر قريب من دعم أو مقاومة؟
    levels = find_key_levels(df_1d)
    near_level = None
    level_type_found = None

    for level_type, lp in levels:
        distance_pct = abs(current_price - lp) / lp * 100
        if distance_pct <= 2.0:  # قريب من المستوى بـ 2%
            near_level = lp
            level_type_found = level_type
            break

    if near_level is None:
        return []

    # Gamma Exposure
    gamma_dir, gamma_label = get_gamma_exposure(sym, current_price)

    # بناء الرسالة
    level_emoji = "🛡 دعم" if level_type_found == "support" else "🔒 مقاومة"

    # توافق الاتجاه
    if level_type_found == "support" and stoch_dir == "bull":
        signal_strength = "🔥 إشارة قوية — دعم + تشبع بيع"
    elif level_type_found == "resistance" and stoch_dir == "bear":
        signal_strength = "🔥 إشارة قوية — مقاومة + تشبع شراء"
    else:
        signal_strength = "⚡ إشارة متعارضة — راجع بنفسك"

    # توافق الغاما مع الاتجاه
    gamma_note = ""
    if gamma_dir == "positive" and stoch_dir == "bull":
        gamma_note = "✅ الغاما تدعم الصعود"
    elif gamma_dir == "negative" and stoch_dir == "bear":
        gamma_note = "✅ الغاما تدعم الهبوط"
    elif gamma_dir == "positive" and stoch_dir == "bear":
        gamma_note = "⚠️ الغاما تعاكس الهبوط"
    elif gamma_dir == "negative" and stoch_dir == "bull":
        gamma_note = "⚠️ الغاما تعاكس الصعود"

    msg = (
        f"📍 <b>${sym} — عند {level_emoji}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🏷 {sector}\n"
        f"💰 السعر: ${current_price:.2f}\n"
        f"📌 المستوى: ${near_level:.2f} ({level_emoji})\n"
        f"📊 Stochastic: {stoch_label}\n"
    )

    if gamma_label:
        msg += f"🎯 Gamma Exposure: {gamma_label}\n"
    if gamma_note:
        msg += f"{gamma_note}\n"

    msg += (
        f"━━━━━━━━━━━━━━━━\n"
        f"{signal_strength}"
    )

    results.append(msg)
    return results

def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')}")
    total = 0

    for sym, sector in STOCKS.items():
        try:
            msgs = check_symbol(sym, sector)
            for msg in msgs:
                send_telegram(msg)
                print(f"  ✅ {sym}")
                total += 1
                time.sleep(1)
            if not msgs:
                print(f"  — {sym}: لا إشارة")
        except Exception as e:
            print(f"  ❌ {sym}: {e}")

    send_telegram(
        f"🔍 <b>انتهى الفحص</b>\n"
        f"الأسهم: {len(STOCKS)}\n"
        f"إشارات: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\nإجمالي: {total}")

print("🚀 بوت دعم/مقاومة + Stochastic + Gamma")
print(f"الأسهم: {len(STOCKS)}")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)
while True:
    schedule.run_pending()
    time.sleep(60)
