import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# إعدادات الصفحة لتتناسب مع شاشة الهاتف
st.set_page_config(page_title="EGX Radar", page_icon="📈", layout="wide")

st.title("📈 EGX Radar - رادار البورصة المصرية")
st.markdown("فحص فني آلي لأهم أسهم البورصة المصرية لاكتشاف فرص الدخول ومناطق السيولة.")

# قائمة بأبرز أسهم البورصة المصرية (تنتهي بـ .CA في ياهو فاينانس)
EGX_STOCKS = {
    "COMI.CA": "التجاري الدولي",
    "TMGH.CA": "طلعت مصطفى",
    "EAST.CA": "الشرقية للدخان",
    "ABUK.CA": "أبو قير للأسمدة",
    "MFPC.CA": "موبكو للأسمدة",
    "SWDY.CA": "السويدي إليكتريك",
    "HRHO.CA": "هيرميس القابضة",
    "FWRY.CA": "فوري",
    "ETEL.CA": "المصرية للاتصالات",
    "ORAS.CA": "أوراسكوم كونستراكشن",
    "ESRS.CA": "حديد عز",
    "HELI.CA": "مصر الجديدة للإسكان",
    "PHDC.CA": "بالم هيلز",
    "EKHO.CA": "القابضة المصرية الكويتية",
    "AMOC.CA": "أموك للزيوت"
}

# دالة حساب مؤشر القوة النسبية RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# دالة جلب البيانات وتحليل الأسهم
@st.cache_data(ttl=900)  # تحديث البيانات كل 15 دقيقة لتسريع التطبيق
def scan_market():
    results = []
    for symbol, name in EGX_STOCKS.items():
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty or len(df) < 20:
                continue
            
            # معالجة تعدد مستويات الأعمدة في بعض نسخ yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['RSI'] = calculate_rsi(df)
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()

            last_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            change_pct = ((last_close - prev_close) / prev_close) * 100
            last_rsi = float(df['RSI'].iloc[-1])
            last_sma20 = float(df['SMA_20'].iloc[-1])
            last_vol = float(df['Volume'].iloc[-1])
            avg_vol = float(df['Vol_Avg'].iloc[-1])

            # تحديد إشارة الرادار
            signal = "حيادي ⚪"
            if last_rsi < 35:
                signal = "تشبع بيعي (فرصة ارتداد) 🟢"
            elif last_rsi > 70:
                signal = "تشبع شرائي (حذر) 🔴"
            elif last_close > last_sma20 and last_vol > (avg_vol * 1.3):
                signal = "اختراق مع سيولة عالية 🚀"
            elif last_close > last_sma20:
                signal = "اتجاه صاعد (فوق متوسط 20) 🔵"

            results.append({
                "الرمز": symbol.replace(".CA", ""),
                "اسم السهم": name,
                "آخر سعر": round(last_close, 2),
                "التغير %": round(change_pct, 2),
                "مؤشر RSI": round(last_rsi, 1),
                "نسبة السيولة": f"{round(last_vol / avg_vol, 1)}x" if avg_vol > 0 else "1.0x",
                "إشارة الرادار": signal
            })
        except Exception:
            continue

    return pd.DataFrame(results)

# زر التحديث اليدوي
if st.button("🔄 تحديث بيانات السوق الآن", use_container_width=True):
    st.cache_data.clear()

with st.spinner("جاري مسح أسهم البورصة المصرية وتحليل المؤشرات..."):
    df_results = scan_market()

if not df_results.empty:
    # فلتر سريع للإشارات
    filter_option = st.selectbox(
        "تصفية النتائج حسب الإشارة:",
        ["الكل", "إيجابية فقط (فرص وسيولة)", "تشبع بيعي (RSI < 35)", "تشبع شرائي (RSI > 70)"]
    )

    if filter_option == "إيجابية فقط (فرص وسيولة)":
        filtered_df = df_results[df_results["إشارة الرادار"].str.contains("🟢|🚀|🔵")]
    elif filter_option == "تشبع بيعي (RSI < 35)":
        filtered_df = df_results[df_results["مؤشر RSI"] < 35]
    elif filter_option == "تشبع شرائي (RSI > 70)":
        filtered_df = df_results[df_results["مؤشر RSI"] > 70]
    else:
        filtered_df = df_results

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.warning("تعذر جلب البيانات حالياً. يرجى المحاولة بعد قليل.")

st.caption("⚠️ تنبيه: البيانات للتحليل الفني والتعليم فقط وليست توصية مباشرة بالبيع أو الشراء.")
