import yfinance as yf
import requests
import schedule
import time
import numpy as np

TOKEN    = "8751470715:AAGqx90Zho44N7pzr42XHZs3Y0gcDZKP_V4"
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

STOCKS = {
    # تكنولوجيا
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
    # مالية
    "JPM":"🏦 مالية","BAC":"🏦 مالية","GS":"🏦 مالية","MS":"🏦 مالية",
    "WFC":"🏦 مالية","C":"🏦 مالية","BLK":"🏦 مالية","AXP":"🏦 مالية",
    "V":"🏦 مالية","MA":"🏦 مالية","COF":"🏦 مالية","DFS":"🏦 مالية",
    "PYPL":"🏦 مالية","SQ":"🏦 مالية","COIN":"🏦 مالية","HOOD":"🏦 مالية",
    "SPGI":"🏦 مالية","MCO":"🏦 مالية","ICE":"🏦 مالية","CME":"🏦 مالية",
    "NDAQ":"🏦 مالية","CBOE":"🏦 مالية","MSCI":"🏦 مالية","FDS":"🏦 مالية",
    "USB":"🏦 مالية","PNC":"🏦 مالية","TFC":"🏦 مالية","SCHW":"🏦 مالية",
    # صحة
    "JNJ":"🏥 صحة","PFE":"🏥 صحة","MRK":"🏥 صحة","ABBV":"🏥 صحة",
    "LLY":"🏥 صحة","BMY":"🏥 صحة","AMGN":"🏥 صحة","GILD":"🏥 صحة",
    "BIIB":"🏥 صحة","VRTX":"🏥 صحة","REGN":"🏥 صحة","MRNA":"🏥 صحة",
    "TMO":"🏥 صحة","DHR":"🏥 صحة","ABT":"🏥 صحة","MDT":"🏥 صحة",
    "SYK":"🏥 صحة","BSX":"🏥 صحة","ISRG":"🏥 صحة","EW":"🏥 صحة",
    "DXCM":"🏥 صحة","IDXX":"🏥 صحة","BDX":"🏥 صحة","ZBH":"🏥 صحة",
    "HOLX":"🏥 صحة","ILMN":"🏥 صحة","EXAS":"🏥 صحة",
    # طاقة
    "XOM":"⛽ طاقة","CVX":"⛽ طاقة","COP":"⛽ طاقة","EOG":"⛽ طاقة",
    "PXD":"⛽ طاقة","DVN":"⛽ طاقة","MPC":"⛽ طاقة","VLO":"⛽ طاقة",
    "PSX":"⛽ طاقة","HES":"⛽ طاقة","OXY":"⛽ طاقة","APA":"⛽ طاقة",
    "FANG":"⛽ طاقة","HAL":"⛽ طاقة","SLB":"⛽ طاقة","BKR":"⛽ طاقة",
    # استهلاكي
    "WMT":"🛒 استهلاكي","TGT":"🛒 استهلاكي","COST":"🛒 استهلاكي",
    "KR":"🛒 استهلاكي","DG":"🛒 استهلاكي","DLTR":"🛒 استهلاكي",
    "MCD":"🛒 استهلاكي","SBUX":"🛒 استهلاكي","CMG":"🛒 استهلاكي",
    "YUM":"🛒 استهلاكي","DPZ":"🛒 استهلاكي","QSR":"🛒 استهلاكي",
    "NKE":"🛒 استهلاكي","LULU":"🛒 استهلاكي","UAA":"🛒 استهلاكي",
    "KO":"🛒 استهلاكي","PEP":"🛒 استهلاكي","PM":"🛒 استهلاكي",
    "MO":"🛒 استهلاكي","STZ":"🛒 استهلاكي","MNST":"🛒 استهلاكي",
    "CELH":"🛒 استهلاكي","EL":"🛒 استهلاكي","CL":"🛒 استهلاكي",
    "PG":"🛒 استهلاكي","KMB":"🛒 استهلاكي",
    # صناعي
    "BA":"🏭 صناعي","LMT":"🏭 صناعي","RTX":"🏭 صناعي","NOC":"🏭 صناعي",
    "GD":"🏭 صناعي","TDG":"🏭 صناعي","HWM":"🏭 صناعي","CAT":"🏭 صناعي",
    "DE":"🏭 صناعي","EMR":"🏭 صناعي","ETN":"🏭 صناعي","PH":"🏭 صناعي",
    "ROK":"🏭 صناعي","AME":"🏭 صناعي","CARR":"🏭 صناعي","TT":"🏭 صناعي",
    "UPS":"🏭 صناعي","FDX":"🏭 صناعي","DAL":"🏭 صناعي","UAL":"🏭 صناعي",
    "AAL":"🏭 صناعي","LUV":"🏭 صناعي","GE":"🏭 صناعي","HON":"🏭 صناعي",
    # اتصالات وعقارات
    "AMT":"📡 اتصالات","CCI":"📡 اتصالات","EQIX":"📡 اتصالات",
    "T":"📡 اتصالات","VZ":"📡 اتصالات","TMUS":"📡 اتصالات",
    "PLD":"🏢 عقارات","O":"🏢 عقارات","SPG":"🏢 عقارات",
    "AVB":"🏢 عقارات","EQR":"🏢 عقارات","DLR":"🏢 عقارات",
    # مؤشرات
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

def get_data(sym, interval, period):
    df = yf.download(sym, period=period, interval=interval,
                     progress=False, auto_adjust=True)
    df.dropna(inplace=True)
    return df

def is_trending_up(sym):
    """
    الفلتر الرئيسي — السهم لازم يكون فوق:
    MA10 شهري + MA20 أسبوعي + MA50 يومي + MA200 ساعي
    """
    try:
        # MA10 شهري
        df_mo = get_data(sym, "1mo", "5y")
        if df_mo.empty or len(df_mo) < 11: return False
        c_mo  = float(df_mo["Close"].squeeze().iloc[-1])
        ma10  = float(df_mo["Close"].squeeze().rolling(10).mean().iloc[-1])
        if c_mo <= ma10: return False

        # MA20 أسبوعي
        df_wk = get_data(sym, "1wk", "2y")
        if df_wk.empty or len(df_wk) < 21: return False
        c_wk  = float(df_wk["Close"].squeeze().iloc[-1])
        ma20  = float(df_wk["Close"].squeeze().rolling(20).mean().iloc[-1])
        if c_wk <= ma20: return False

        # MA50 يومي
        df_1d = get_data(sym, "1d", "1y")
        if df_1d.empty or len(df_1d) < 51: return False
        c_1d  = float(df_1d["Close"].squeeze().iloc[-1])
        ma50  = float(df_1d["Close"].squeeze().rolling(50).mean().iloc[-1])
        if c_1d <= ma50: return False

        # MA200 ساعي
        df_1h = get_data(sym, "1h", "60d")
        if df_1h.empty or len(df_1h) < 201: return False
        c_1h  = float(df_1h["Close"].squeeze().iloc[-1])
        ma200 = float(df_1h["Close"].squeeze().rolling(200).mean().iloc[-1])
        if c_1h <= ma200: return False

        return True

    except:
        return False

def check_4h_ma50_bounce(sym, sector):
    """
    على فريم 4 ساعات:
    - السعر لمس MA50 (اقترب منه بـ 1%)
    - الشمعة الأخيرة ارتدت منه للأعلى (close > open و close > MA50)
    """
    try:
        df = get_data(sym, "4h", "60d")
        if df.empty or len(df) < 55: return None

        closes = df["Close"].squeeze()
        opens  = df["Open"].squeeze()
        lows   = df["Low"].squeeze()
        highs  = df["High"].squeeze()

        ma50 = closes.rolling(50).mean()

        c0   = float(closes.iloc[-1])
        o0   = float(opens.iloc[-1])
        l0   = float(lows.iloc[-1])
        h0   = float(highs.iloc[-1])
        ma0  = float(ma50.iloc[-1])
        ma1  = float(ma50.iloc[-2])
        c1   = float(closes.iloc[-2])
        l1   = float(lows.iloc[-2])

        if np.isnan(ma0): return None

        # شرط 1: شمعة سابقة أو حالية لمست MA50 (low قريب من MA50)
        touched_ma = (abs(l0 - ma0) / ma0 < 0.01) or (abs(l1 - ma1) / ma1 < 0.01)

        # شرط 2: الشمعة الحالية صاعدة (ارتداد)
        bullish_candle = c0 > o0

        # شرط 3: الإغلاق فوق MA50
        above_ma = c0 > ma0

        # شرط 4: الشمعة السابقة كانت تحت أو عند MA50
        prev_near = c1 <= ma1 * 1.005

        if touched_ma and bullish_candle and above_ma and prev_near:
            # حساب نسبة الارتداد
            bounce_pct = ((c0 - l0) / l0) * 100

            # حجم التداول
            volumes  = df["Volume"].squeeze()
            avg_vol  = float(volumes.iloc[-21:-1].mean())
            curr_vol = float(volumes.iloc[-1])
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0
            vol_label = "🔺 عالي" if vol_ratio >= 1.5 else "عادي"

            msg = (
                f"🟢 <b>ارتداد من MA50 — ${sym}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🏷 {sector}\n"
                f"📊 الفريم: 4 ساعات\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ <b>فلتر الاتجاه الصاعد محقق</b>\n"
                f"  📈 فوق MA10 شهري\n"
                f"  📈 فوق MA20 أسبوعي\n"
                f"  📈 فوق MA50 يومي\n"
                f"  📈 فوق MA200 ساعي\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🔄 <b>الإشارة</b>\n"
                f"  السعر لمس MA50 على 4H وارتد\n"
                f"  MA50 (4H): ${ma0:.2f}\n"
                f"  💰 السعر الحالي: ${c0:.2f}\n"
                f"  📏 الارتداد: {bounce_pct:.1f}%\n"
                f"  📦 الحجم: {vol_label} (x{vol_ratio:.1f})\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎯 فرصة دخول محتملة مع الاتجاه"
            )
            return msg

        return None

    except Exception as e:
        print(f"    خطأ {sym}: {e}")
        return None

def check_all():
    print(f"\n⏰ {time.strftime('%H:%M:%S')}")
    total = 0

    for sym, sector in STOCKS.items():
        try:
            print(f"  فحص {sym}...")

            # الفلتر الأول — الاتجاه الصاعد
            if not is_trending_up(sym):
                print(f"    ↳ فلتر الاتجاه: ❌")
                continue
            print(f"    ↳ فلتر الاتجاه: ✅")

            # الإشارة — ارتداد من MA50 على 4H
            msg = check_4h_ma50_bounce(sym, sector)
            if msg:
                send_telegram(msg)
                print(f"    ↳ إشارة ✅ أُرسلت")
                total += 1
                time.sleep(1)
            else:
                print(f"    ↳ لا ارتداد من MA50 الآن")

        except Exception as e:
            print(f"  ❌ {sym}: {e}")

    send_telegram(
        f"🔍 <b>انتهى الفحص</b>\n"
        f"الأسهم: {len(STOCKS)}\n"
        f"إشارات مرسلة: {total}\n"
        f"⏱ {time.strftime('%H:%M:%S')}"
    )
    print(f"\nإجمالي: {total}")

print(f"🚀 بوت MA Bounce")
print(f"الأسهم: {len(STOCKS)}")
print("الفحص كل ساعة\n")

check_all()
schedule.every(1).hours.do(check_all)
while True:
    schedule.run_pending()
    time.sleep(60)
