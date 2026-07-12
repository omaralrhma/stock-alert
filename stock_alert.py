import yfinance as yf
import requests
import schedule
import time
import numpy as np

TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

STOCKS = {
    # ── تكنولوجيا
    "AAPL":"💻 تكنولوجيا","MSFT":"💻 تكنولوجيا","NVDA":"💻 تكنولوجيا",
    "GOOGL":"💻 تكنولوجيا","META":"💻 تكنولوجيا","AMZN":"💻 تكنولوجيا",
    "TSLA":"💻 تكنولوجيا","AMD":"💻 تكنولوجيا","INTC":"💻 تكنولوجيا",
    "CRM":"💻 تكنولوجيا","ORCL":"💻 تكنولوجيا","ADBE":"💻 تكنولوجيا",
    "QCOM":"💻 تكنولوجيا","AMAT":"💻 تكنولوجيا","MU":"💻 تكنولوجيا",
    "LRCX":"💻 تكنولوجيا","KLAC":"💻 تكنولوجيا","PANW":"💻 تكنولوجيا",
    "CRWD":"💻 تكنولوجيا","ZS":"💻 تكنولوجيا","FTNT":"💻 تكنولوجيا",
    "NET":"💻 تكنولوجيا","SNOW":"💻 تكنولوجيا","DDOG":"💻 تكنولوجيا",
    "PLTR":"💻 تكنولوجيا","AVGO":"💻 تكنولوجيا","MRVL":"💻 تكنولوجيا",
    "ARM":"💻 تكنولوجيا","NOW":"💻 تكنولوجيا","SMCI":"💻 تكنولوجيا",
    "TXN":"💻 تكنولوجيا","SNPS":"💻 تكنولوجيا","CDNS":"💻 تكنولوجيا",
    "TEAM":"💻 تكنولوجيا","MDB":"💻 تكنولوجيا","SHOP":"💻 تكنولوجيا",
    "ADSK":"💻 تكنولوجيا","ANSS":"💻 تكنولوجيا","ROP":"💻 تكنولوجيا",
    "ENPH":"💻 تكنولوجيا","FSLR":"💻 تكنولوجيا",
    # ── مالية
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية",
    "WFC":"🏦 مالية","C":"🏦 مالية","BLK":"🏦 مالية","AXP":"🏦 مالية",
    "V":"🏦 مالية","MA":"🏦 مالية","COF":"🏦 مالية","DFS":"🏦 مالية",
    "PYPL":"🏦 مالية","SQ":"🏦 مالية","COIN":"🏦 مالية","HOOD":"🏦 مالية",
    "SPGI":"🏦 مالية","MCO":"🏦 مالية","ICE":"🏦 مالية","CME":"🏦 مالية",
    "NDAQ":"🏦 مالية","CBOE":"🏦 مالية","MSCI":"🏦 مالية","FDS":"🏦 مالية",
    "USB":"🏦 مالية","PNC":"🏦 مالية","TFC":"🏦 مالية","SCHW":"🏦 مالية",
    # ── صحة
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "BIIB":"🏥 صحة","VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة",
    "TMO":"🏥 صحة","DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة",
    "SYK":"🏥 صحة","BSX":"🏥 صحة","ISRG":"🏥 صحة","EW":"🏥 صحة",
    "DXCM":"🏥 صحة","IDXX":"🏥 صحة","BDX":"🏥 صحة","ZBH":"🏥 صحة",
    "HOLX":"🏥 صحة","ILMN":"🏥 صحة","EXAS":"🏥 صحة",
    # ── طاقة
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "PXD":"⛽ طاقة","DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة",
    "PSX":"⛽ طاقة","HES":"⛽ طاقة","OXY":"⛽ طاقة","APA":"⛽ طاقة",
    "FANG":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة","BKR":"⛽ طاقة",
    # ── استهلاكي
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "KR":"🛒 استهلاكي","DG":"🛒 استهلاكي","DLTR":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "YUM":"🛒 استهلاكي","DPZ":"🛒 استهلاكي","QSR":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","UAA":"🛒 استهلاكي",
    "KO":"🛒 استهلاكي","PEP":"🛒 استهلاكي","PM":"🛒 استهلاكي",
    "MO":"🛒 استهلاكي","STZ":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "CELH":"🛒 استهلاكي","EL":"🛒 استهلاكي","CL":"🛒 استهلاكي",
    "PG":"🛒 استهلاكي","KMB":"🛒 استهلاكي",
    # ── صناعي
    "BA":"🏭 صناعي","LMT":"🏭 صناعي","RTX":"🏭 صناعي","NOC":"🏭 صناعي",
    "GD":"🏭 صناعي","TDG":"🏭 صناعي","HWM":"🏭 صناعي","CAT":"🏭 صناعي",
    "DE":"🏭 صناعي","EMR":"🏭 صناعي","ETN":"🏭 صناعي","PH":"🏭 صناعي",
    "ROK":"🏭 صناعي","AME":"🏭 صناعي","CARR":"🏭 صناعي","TT":"🏭 صناعي",
    "UPS":"🏭 صناعي","FDX":"🏭 صناعي","DAL":"🏭 صناعي","UAL":"🏭 صناعي",
    "AAL":"🏭 صناعي","LUV":"🏭 صناعي","GE":"🏭 صناعي","HON":"🏭 صناعي",
    # ── اتصالات وعقارات
    "AMT":"📡 اتصالات","CCI":"📡 اتصالات","EQIX":"📡 اتصالات",
    "T":"📡 اتصالات","VZ":"📡 اتصالات","TMUS":"📡 اتصالات",
    "PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات",
    "AVB":"🏢 عقارات","EQR":"🏢 عقارات","DLR":"🏢 عقارات",
    # ── مؤشرات وETF
    "SPY":"📊 مؤشر","QQQ":"📊 مؤشر","IWM":"📊 مؤشر","DIA":"📊 مؤشر",
    "VTI":"📊 مؤشر","XLK":"📊 مؤشر","XLF":"📊 مؤشر","XLE":"📊 مؤشر",
    "XLV":"📊 مؤشر","XLI":"📊 مؤشر","XLY":"📊 مؤشر","XLP":"📊 مؤشر",
    "GLD":"📊 مؤشر","SLV":"📊 مؤشر","TLT":"📊 مؤشر","HYG":"📊 مؤشر",
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"})
            time.sleep(0.3)
        except Exception as e:
            print(f"خطأ: {e}")

def get_data(symbol, interval, period):
    df = yf.download(symbol, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def get_stochastic(df, k=14, d=3):
    highs  = df["High"].squeeze()
    lows   = df["Low"].squeeze()
    closes = df["Close"].squeeze()
    if len(closes) < k + d:
        return None, None
    lowest_low   = lows.rolling(k).min()
    highest_high = highs.rolling(k).max()
    denom = (highest_high - lowest_low).replace(0, np.nan)
    k_line = 100 * (closes - lowest_low) / denom
    d_line = k_line.rolling(d).mean()
    return float(k_line.iloc[-1]), float(d_line.iloc[-1])

def find_sr_levels(df, lookback=20):
    highs  = df["High"].squeeze().values
    lows   = df["Low"].squeeze().values
    levels = []
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i-lookback:i+lookback]):
            lp = float(highs[i])
            touches = sum(1 for h in highs if abs(h - lp)/lp < 0.01)
            levels.append(("resistance", lp, touches))
        if lows[i] == min(lows[i-lookback:i+lookback]):
            lp = float(lows[i])
            touches = sum(1 for l in lows if abs(l - lp)/lp < 0.01)
            levels.append(("support", lp, touches))
    levels.sort(key=lambda x: -x[2])
    return levels

def get_gamma_levels(sym, current_price):
    try:
        ticker = yf.Ticker(sym)
        expirations = ticker.options
        if not expirations:
            return [], None
        all_calls_oi = {}
        all_puts_oi  = {}
        for exp in expirations[:2]:
            chain = ticker.option_chain(exp)
            for _, row in chain.calls.iterrows():
                strike = float(row["strike"])
                oi = float(row["openInterest"]) if row["openInterest"] else 0
                all_calls_oi[strike] = all_calls_oi.get(strike, 0) + oi
            for _, row in chain.puts.iterrows():
                strike = float(row["strike"])
                oi = float(row["openInterest"]) if row["openInterest"] else 0
                all_puts_oi[strike] = all_puts_oi.get(strike, 0) + oi
        all_strikes = set(all_calls_oi.keys()) | set(all_puts_oi.keys())
        margin = current_price * 0.15
        nearby = [s for s in all_strikes if current_price-margin <= s <= current_price+margin]
        if not nearby:
            return [], None
        gex_data = []
        for strike in nearby:
            call_oi = all_calls_oi.get(strike, 0)
            put_oi  = all_puts_oi.get(strike, 0)
            total   = call_oi + put_oi
            net_gex = call_oi - put_oi
            gex_data.append((strike, call_oi, put_oi, total, net_gex))
        gex_data.sort(key=lambda x: -x[3])
        top_levels = gex_data[:5]
        nearby_2pct = [g for g in gex_data if abs(g[0]-current_price)/current_price < 0.02]
        if nearby_2pct:
            total_net = sum(g[4] for g in nearby_2pct)
            if total_net > 0:
                return top_levels, ("🟢 إيجابية", "positive")
            elif total_net < 0:
                return top_levels, ("🔴 سلبية", "negative")
            else:
                return top_levels, ("⚪ محايدة", "neutral")
        return top_levels, None
    except:
        return [], None

def check_symbol(sym, sector):
    df_1d = get_data(sym, "1d", "1y")
    if df_1d.empty or len(df_1d) < 60:
        return []

    current_price = float(df_1d["Close"].squeeze().iloc[-1])

    sr_levels = find_sr_levels(df_1d)
    near_level = None
    level_type_found = None
    level_touches = 0

    for ltype, lp, touches in sr_levels:
        dist_pct = abs(current_price - lp) / lp * 100
        if dist_pct <= 1.5:
            near_level       = lp
            level_type_found = ltype
            level_touches    = touches
            break

    if near_level is None:
        return []

    timeframes = [
        ("30m", "30 دقيقة", "60d"),
        ("1h",  "ساعة",     "60d"),
        ("4h",  "4 ساعات",  "60d"),
        ("1d",  "يومي",     "1y"),
    ]

    stoch_results = []
    for interval, tf_name, period in timeframes:
        try:
            df_tf = get_data(sym, interval, period)
            if df_tf.empty or len(df_tf) < 20:
                continue
            k, d = get_stochastic(df_tf)
            if k is None:
                continue
            if k < 25 and d < 25:
                stoch_results.append((tf_name, "bull", k, d))
            elif k > 75 and d > 75:
                stoch_results.append((tf_name, "bear", k, d))
        except:
            continue

    if not stoch_results:
        return []

    gamma_levels, gamma_overall = get_gamma_levels(sym, current_price)
    gamma_label = gamma_overall[0] if gamma_overall else None
    gamma_dir   = gamma_overall[1] if gamma_overall else None

    key_gamma_str = ""
    if gamma_levels:
        lines = []
        for strike, call_oi, put_oi, total, net in gamma_levels[:3]:
            bias = "🟢C" if net > 0 else "🔴P"
            lines.append(f"  ${strike:.0f} {bias} (OI:{total/1000:.0f}k)")
        key_gamma_str = "\n".join(lines)

    level_emoji = "🛡 دعم" if level_type_found == "support" else "🔒 مقاومة"
    dist_pct    = abs(current_price - near_level) / near_level * 100

    bull_count = sum(1 for r in stoch_results if r[1] == "bull")
    bear_count = sum(1 for r in stoch_results if r[1] == "bear")
    dominant   = "bull" if bull_count >= bear_count else "bear"

    if level_type_found == "support" and dominant == "bull":
        strength = "🔥🔥 إشارة قوية — دعم + تشبع بيع"
    elif level_type_found == "resistance" and dominant == "bear":
        strength = "🔥🔥 إشارة قوية — مقاومة + تشبع شراء"
    else:
        strength = "⚡ إشارة متعارضة"

    gamma_note = ""
    if gamma_dir == "positive" and dominant == "bull":
        gamma_note = "✅ الغاما تدعم الصعود"
    elif gamma_dir == "negative" and dominant == "bear":
        gamma_note = "✅ الغاما تدعم الهبوط"
    elif gamma_dir == "positive" and dominant == "bear":
        gamma_note = "⚠️ الغاما تعاكس الهبوط — انتبه"
    elif gamma_dir == "negative" and dominant == "bull":
        gamma_note = "⚠️ الغاما تعاكس الصعود — انتبه"

    stoch_str = ""
    for tf_name, sdir, k, d in stoch_results:
        emoji = "🟢" if sdir == "bull" else "🔴"
        label = "تشبع بيع" if sdir == "bull" else "تشبع شراء"
        stoch_str += f"  {emoji} {tf_name}: {label} (K:{k:.0f} D:{d:.0f})\n"

    msg = (
        f"📍 <b>${sym} — عند {level_emoji}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🏷 {sector}\n"
        f"💰 السعر: ${current_price:.2f}\n"
        f"📌 المستوى: ${near_level:.2f} ({level_emoji})\n"
        f"📏 البُعد: {dist_pct:.1f}% | اختُبر {level_touches}x\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Stochastic</b>\n"
        f"{stoch_str}"
        f"━━━━━━━━━━━━━━━━\n"
    )
    if gamma_label:
        msg += f"🎯 <b>Gamma</b>: {gamma_label}\n"
    if key_gamma_str:
        msg += f"أهم مستويات:\n{key_gamma_str}\n"
    if gamma_note:
        msg += f"{gamma_note}\n"
    msg += f"━━━━━━━━━━━━━━━━\n{strength}"

    return [msg]

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

print(f"🚀 بوت دعم/مقاومة + Stochastic + Gamma")
print(f"الأسهم: {len(STOCKS)}")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)
while True:
    schedule.run_pending()
    time.sleep(60)
