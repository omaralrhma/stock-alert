import yfinance as yf
import requests
import schedule
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ==================== الإعدادات ====================
TOKEN    = "YOUR_BOT_TOKEN_HERE"  # غيّر التوكن من BotFather — القديم مكشوف
CHAT_IDS = ["615265045", "7775490993", "5574232437"]

TIMEFRAMES = {
    "30m": {"interval": "30m", "period": "60d",  "name": "30 دقيقة"},
    "1h":  {"interval": "1h",  "period": "90d",  "name": "ساعة"},
    "4h":  {"interval": "4h",  "period": "120d", "name": "4 ساعات"},
    "1d":  {"interval": "1d",  "period": "2y",   "name": "يومي"},
    "1wk": {"interval": "1wk", "period": "5y",   "name": "أسبوعي"},
}

# ===== إعدادات تريدينق فيو =====
PIVOT_MINOR   = 3      # عدد الشموع للقمة/القاع العادي
PIVOT_MAJOR   = 7      # عدد الشموع للقمة/القاع الأقوى
PROX_PCT      = 1.5    # نسبة التقارب لدمج المستويات (%)
PCT_THRESH    = 3.0    # نسبة الاختراق/الكسر المطلوبة (%)
MIN_BARS      = 3      # عدد الشموع المطلوبة فوق/تحت بعد الكسر
RETEST_MARGIN = 0.5    # نسبة السماح بالاقتراب من مستوى الكسر (%)

sent_signals = {}

# ==================== قائمة الأسهم (نفس قائمتك) ====================
STOCKS = {
    # ... الصق قائمتك كاملة هنا كما هي ...
}

# ==================== دوال مساعدة ====================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for cid in CHAT_IDS:
        try:
            requests.post(url, data={"chat_id": cid, "text": msg, "parse_mode": "HTML"}, timeout=12)
            time.sleep(0.35)
        except Exception as e:
            print(f"خطأ تيليجرام: {e}")

def get_data(sym, interval, period):
    try:
        df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        return df
    except Exception:
        return None

def pivot_highs(highs, left, right):
    """مكافئ ta.pivothigh"""
    n = len(highs)
    out = [np.nan] * n
    for i in range(left, n - right):
        window = highs[i - left : i + right + 1]
        if highs[i] == max(window):
            out[i] = highs[i]
    return out

def pivot_lows(lows, left, right):
    """مكافئ ta.pivotlow"""
    n = len(lows)
    out = [np.nan] * n
    for i in range(left, n - right):
        window = lows[i - left : i + right + 1]
        if lows[i] == min(window):
            out[i] = lows[i]
    return out

# ==================== منطق تبادل الأدوار (من تريدينق فيو) ====================
def check_role_reversal(sym, sector, tf_key, tf_info):
    """
    يحاكي مؤشر Pine شمعة بشمعة ويرجع رسالة إذا آخر شمعة أعطت إشارة شراء أو بيع.
    """
    try:
        df = get_data(sym, tf_info["interval"], tf_info["period"])
        if df is None or len(df) < PIVOT_MAJOR * 3 + 20:
            return None

        highs   = df["High"].values.astype(float)
        lows    = df["Low"].values.astype(float)
        closes  = df["Close"].values.astype(float)
        n = len(df)

        maj_ph = pivot_highs(highs, PIVOT_MAJOR, PIVOT_MAJOR)
        min_ph = pivot_highs(highs, PIVOT_MINOR, PIVOT_MINOR)
        maj_pl = pivot_lows(lows, PIVOT_MAJOR, PIVOT_MAJOR)
        min_pl = pivot_lows(lows, PIVOT_MINOR, PIVOT_MINOR)

        last_major_ph = np.nan
        last_major_pl = np.nan

        # حالة القمة (شراء)
        ph_state = 0
        curr_ph = np.nan
        ph_broken = False
        bars_above_ph = 0

        # حالة القاع (بيع)
        pl_state = 0
        curr_pl = np.nan
        pl_broken = False
        bars_below_pl = 0

        buy_signal  = False
        sell_signal = False
        signal_level = None
        signal_type  = None

        for i in range(n):
            buy_signal  = False
            sell_signal = False

            # تحديث آخر قمة/قاع أقوى
            if not np.isnan(maj_ph[i]):
                last_major_ph = maj_ph[i]
            if not np.isnan(maj_pl[i]):
                last_major_pl = maj_pl[i]

            # ---- تحديد قمة جديدة ----
            setup_new_ph = False
            target_ph = np.nan
            if not np.isnan(maj_ph[i]):
                target_ph = maj_ph[i]
                setup_new_ph = True
            elif not np.isnan(min_ph[i]):
                if not np.isnan(last_major_ph) and abs(min_ph[i] - last_major_ph) / last_major_ph <= (PROX_PCT / 100):
                    target_ph = last_major_ph
                else:
                    target_ph = min_ph[i]
                setup_new_ph = True

            if setup_new_ph:
                curr_ph = target_ph
                ph_state = 1
                ph_broken = False
                bars_above_ph = 0

            # ---- تحديد قاع جديد ----
            setup_new_pl = False
            target_pl = np.nan
            if not np.isnan(maj_pl[i]):
                target_pl = maj_pl[i]
                setup_new_pl = True
            elif not np.isnan(min_pl[i]):
                if not np.isnan(last_major_pl) and abs(min_pl[i] - last_major_pl) / last_major_pl <= (PROX_PCT / 100):
                    target_pl = last_major_pl
                else:
                    target_pl = min_pl[i]
                setup_new_pl = True

            if setup_new_pl:
                curr_pl = target_pl
                pl_state = 1
                pl_broken = False
                bars_below_pl = 0

            # ---- شروط الشراء (إعادة اختبار قمة مخترقة) ----
            if ph_state > 0 and not np.isnan(curr_ph):
                if highs[i] >= curr_ph * (1 + PCT_THRESH / 100):
                    ph_broken = True

                if ph_state == 1:
                    if closes[i] > curr_ph:
                        ph_state = 2
                        bars_above_ph = 1
                elif ph_state == 2:
                    ph_retest = curr_ph * (1 + RETEST_MARGIN / 100)
                    if lows[i] <= ph_retest:
                        if ph_broken and bars_above_ph > MIN_BARS:
                            buy_signal = True
                            signal_level = curr_ph
                            signal_type = "buy"
                        ph_state = 0
                    else:
                        bars_above_ph += 1

            # ---- شروط البيع (إعادة اختبار قاع مكسور) ----
            if pl_state > 0 and not np.isnan(curr_pl):
                if lows[i] <= curr_pl * (1 - PCT_THRESH / 100):
                    pl_broken = True

                if pl_state == 1:
                    if closes[i] < curr_pl:
                        pl_state = 2
                        bars_below_pl = 1
                elif pl_state == 2:
                    pl_retest = curr_pl * (1 - RETEST_MARGIN / 100)
                    if highs[i] >= pl_retest:
                        if pl_broken and bars_below_pl > MIN_BARS:
                            sell_signal = True
                            signal_level = curr_pl
                            signal_type = "sell"
                        pl_state = 0
                    else:
                        bars_below_pl += 1

        # إشارة فقط إذا حدثت على آخر شمعة
        if not buy_signal and not sell_signal:
            return None

        price = closes[-1]
        if signal_type == "buy":
            msg = (
                f"🟢 <b>تبادل أدوار — شراء</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 قمة مخترقة: <b>${signal_level:.2f}</b>\n"
                f"📈 اختراق مطلوب: ≥ {PCT_THRESH}%\n"
                f"⏱️ شموع فوق المستوى: > {MIN_BARS}\n"
                f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ اختراق 3% + بقاء + إعادة اختبار قمة"
            )
        else:
            msg = (
                f"🔴 <b>تبادل أدوار — بيع</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"<b>${sym}</b>  |  {sector}\n"
                f"📊 الفريم: <b>{tf_info['name']}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📍 قاع مكسور: <b>${signal_level:.2f}</b>\n"
                f"📉 كسر مطلوب: ≥ {PCT_THRESH}%\n"
                f"⏱️ شموع تحت المستوى: > {MIN_BARS}\n"
                f"💰 السعر الحالي: <b>${price:.2f}</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"✅ كسر 3% + بقاء + إعادة اختبار قاع"
            )
        return msg

    except Exception:
        return None

# ==================== الفحص الرئيسي ====================
def check_all():
    print(f"\n{'='*55}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")
    total_signals = 0

    for sym, sector in STOCKS.items():
        print(f"▶️ {sym}", end=" ")
        found = False
        for tf_key, tf_info in TIMEFRAMES.items():
            key = f"{sym}_{tf_key}"
            if key in sent_signals and datetime.now() - sent_signals[key] < timedelta(hours=8):
                continue
            msg = check_role_reversal(sym, sector, tf_key, tf_info)
            if msg:
                send_telegram(msg)
                sent_signals[key] = datetime.now()
                print(f"→ ✅ إشارة على {tf_info['name']}")
                total_signals += 1
                found = True
                time.sleep(1.1)
                break
        if not found:
            print("→ لا شيء")
        time.sleep(0.35)

    summary = (
        f"🔍 <b>انتهى الفحص</b>\n"
        f"إشارات صحيحة: {total_signals}\n"
        f"⏱️ {datetime.now().strftime('%H:%M:%S')}"
    )
    send_telegram(summary)
    print(f"\n✅ إجمالي الإشارات: {total_signals}")

if __name__ == "__main__":
    print("🚀 بوت تبادل الأدوار — منطق تريدينق فيو (شراء + بيع)")
    print(f"الإعدادات: pivot {PIVOT_MINOR}/{PIVOT_MAJOR} | اختراق {PCT_THRESH}% | min_bars {MIN_BARS} | retest {RETEST_MARGIN}%")
    check_all()
    schedule.every(90).minutes.do(check_all)
    while True:
        schedule.run_pending()
        time.sleep(50)
