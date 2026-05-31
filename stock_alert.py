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

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ: {e}")

def get_data(symbol, interval):
    period = "60d" if interval == "4h" else ("2y" if interval == "1wk" else "1y")
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

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
    body = abs(c - o)
    total = h - l
    if total == 0: return False
    return (min(o,c)-l) >= 2*body and (h-max(o,c)) <= body*0.5 and c > o

def is_bearish_candle(o, h, l, c):
    body = abs(c - o)
    total = h - l
    if total == 0: return False
    return c < o and body >= total * 0.5

# ─────────────────────────────────────────────
# النماذج
# ─────────────────────────────────────────────

def get_role_reversal(df, tf):
    closes = df["Close"].squeeze()
    opens  = df["Open"].squeeze()
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    n = len(closes)
    if n < 30: return []
    c0,o0,h0,l0 = float(closes.iloc[-1]),float(opens.iloc[-1]),float(highs.iloc[-1]),float(lows.iloc[-1])
    c1,c2 = float(closes.iloc[-2]),float(closes.iloc[-3])
    results = []
    for level_type, level_price in find_key_levels(df):
        margin = level_price * 0.008
        if level_type == "resistance":
            if c2 < level_price and c1 > level_price+margin and abs(l0-level_price) <= margin*2 and is_hammer(o0,h0,l0,c0):
                results.append(("role_reversal","bull", level_price, c0, tf))
        elif level_type == "support":
            if c2 > level_price and c1 < level_price-margin and abs(h0-level_price) <= margin*2 and is_bearish_candle(o0,h0,l0,c0):
                results.append(("role_reversal","bear", level_price, c0, tf))
    return results[:1]

def get_momentum_breakout(df, tf):
    closes  = df["Close"].squeeze()
    opens   = df["Open"].squeeze()
    volumes = df["Volume"].squeeze()
    n = len(closes)
    if n < 25: return []
    c_prev,c_curr,o_curr = float(closes.iloc[-2]),float(closes.iloc[-1]),float(opens.iloc[-1])
    avg_vol  = float(np.mean(volumes.values[-21:-1]))
    curr_vol = float(volumes.iloc[-1])
    vol_ratio = curr_vol/avg_vol if avg_vol > 0 else 0
    avg_body  = float(np.mean([abs(float(closes.iloc[j])-float(opens.iloc[j])) for j in range(-21,-1)]))
    curr_body = abs(c_curr-o_curr)
    body_ratio = curr_body/avg_body if avg_body > 0 else 0
    if vol_ratio < 2.0 or body_ratio < 1.5: return []
    results = []
    for level_type, level_price in find_key_levels(df):
        margin = level_price * 0.005
        if level_type == "resistance" and c_prev < level_price and c_curr > level_price+margin:
            results.append(("momentum","bull", level_price, c_curr, tf, vol_ratio, body_ratio))
        elif level_type == "support" and c_prev > level_price and c_curr < level_price-margin:
            results.append(("momentum","bear", level_price, c_curr, tf, vol_ratio, body_ratio))
    return results[:1]

def get_ma_signals(df, tf):
    closes = df["Close"].squeeze()
    if len(closes) < 105: return []
    results = []
    for ma in [50, 100]:
        ma_series = closes.rolling(ma).mean()
        curr_ma = float(ma_series.iloc[-1])
        prev_ma = float(ma_series.iloc[-2])
        curr_c  = float(closes.iloc[-1])
        prev_c  = float(closes.iloc[-2])
        if prev_c < prev_ma and curr_c > curr_ma:
            results.append(("ma","bull", ma, curr_ma, curr_c, tf))
        elif prev_c > prev_ma and curr_c < curr_ma:
            results.append(("ma","bear", ma, curr_ma, curr_c, tf))
    return results

# ─────────────────────────────────────────────
# بناء الرسائل
# ─────────────────────────────────────────────

def build_message(sym, sector, signals):
    """يبني رسالة واحدة لكل أنواع الإشارات للسهم"""

    role   = [s for s in signals if s[0]=="role_reversal"]
    mom    = [s for s in signals if s[0]=="momentum"]
    ma_sig = [s for s in signals if s[0]=="ma"]

    is_cluster = sum([len(role)>0, len(mom)>0, len(ma_sig)>0]) >= 2

    lines = []

    # ── رأس الرسالة
    if is_cluster:
        lines.append(f"🔥🔥 <b>كلاستر إشارات — ${sym}</b> 🔥🔥")
    else:
        lines.append(f"<b>${sym}</b>")

    lines.append(f"🏷 {sector}")
    lines.append("─────────────────")

    # ── تبادل الأدوار
    if role:
        lines.append("🔄 <b>تبادل الأدوار</b>")
        for s in role:
            _, direction, level, price, tf = s
            arrow = "🟢" if direction == "bull" else "🔴"
            desc  = "صعودي 🔨 هامر" if direction == "bull" else "هبوطي 🕯 شمعة حمراء"
            lines.append(f"  {arrow} {desc}")
            lines.append(f"  📊 {tf} | المستوى: ${level:.2f}")
            lines.append(f"  💰 السعر: ${price:.2f}")

    # ── اختراق بزخم
    if mom:
        if role: lines.append("─────────────────")
        lines.append("⚡ <b>اختراق بزخم</b>")
        for s in mom:
            _, direction, level, price, tf, vr, br = s
            arrow = "🟢" if direction == "bull" else "🔴"
            action = "اختراق مقاومة" if direction == "bull" else "كسر دعم"
            lines.append(f"  {arrow} {action}")
            lines.append(f"  📊 {tf} | المستوى: ${level:.2f}")
            lines.append(f"  📈 حجم x{vr:.1f} | جسم x{br:.1f}")
            lines.append(f"  💰 السعر: ${price:.2f}")

    # ── المتوسطات
    if ma_sig:
        if role or mom: lines.append("─────────────────")
        lines.append("📉 <b>المتوسطات المتحركة</b>")
        for s in ma_sig:
            _, direction, ma, ma_val, price, tf = s
            arrow = "🟢" if direction == "bull" else "🔴"
            action = f"اختراق MA{ma} للأعلى" if direction == "bull" else f"كسر MA{ma} للأسفل"
            lines.append(f"  {arrow} {action}")
            lines.append(f"  📊 {tf} | MA{ma}: ${ma_val:.2f}")
            lines.append(f"  💰 السعر: ${price:.2f}")

    return "\n".join(lines)

# ─────────────────────────────────────────────
# الفحص الرئيسي
# ─────────────────────────────────────────────

def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')}")
    total = 0
    timeframes = [("4h","4 ساعات"), ("1d","يومي"), ("1wk","أسبوعي")]

    for sym, sector in STOCKS.items():
        all_signals = []
        try:
            for interval, tf_name in timeframes:
                df = get_data(sym, interval)
                if df.empty or len(df) < 40: continue
                all_signals += get_role_reversal(df, tf_name)
                all_signals += get_momentum_breakout(df, tf_name)
                all_signals += get_ma_signals(df, tf_name)

            if all_signals:
                msg = build_message(sym, sector, all_signals)
                send_telegram(msg)
                print(f"  ✅ {sym} — {len(all_signals)} إشارة")
                total += 1
                time.sleep(1)
            else:
                print(f"  — {sym}: لا إشارات")

        except Exception as e:
            print(f"  ❌ {sym}: {e}")

    send_telegram(
        f"🔍 انتهى الفحص\n"
        f"الأسهم: {len(STOCKS)} | 4h + يومي + أسبوعي\n"
        f"أسهم فيها إشارات: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\nأسهم فيها إشارات: {total}")

print("🚀 مراقبة الأسهم")
print(f"الأسهم: {len(STOCKS)} | الفريمات: 4h + يومي + أسبوعي")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)
while True:
    schedule.run_pending()
    time.sleep(60)
