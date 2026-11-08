import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعدادات الصفحة
st.set_page_config(page_title="EGX Radar Ultimate", page_icon="🎯", layout="wide")

st.title("🎯 EGX Radar Ultimate")
st.caption("مستشار البورصة المصرية الذكي - التحليل الفني والمالي وإدارة المخاطر")

# قاعدة بيانات المؤشرات وصناديق الاستثمار في البورصة المصرية
EGX_ASSETS = {
    "EGX 30 (المؤشر الرئيسي)": {
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
    },
    "EGX 70 (الأسهم الصغيرة والمتوسطة)": {
        "BINV.CA": "بي إنفستمنتس القابضة",
        "DSCW.CA": "دايس للملابس الجاهزة",
        "ASCM.CA": "أسيك للتعدين",
        "CCAP.CA": "القلعة للاستشارات",
        "EGTS.CA": "المصرية للمنتجعات",
        "ELSH.CA": "الشمس للإسكان",
        "MPRC.CA": "مدينة الإنتاج الإعلامي",
        "OFH.CA": "أوراسكوم المالية"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF.CA": "صندوق مؤشر EGX 30",
        "BTFH.CA": "بلتون القابضة (صناديق الذهب والدخل)",
        "HRHO.CA": "إي إف جي القابضة (صناديق الاستثمار)",
        "ACTF.CA": "أكت فاينانشال"
    }
}

# شريط اختيار المؤشر
selected_category = st.selectbox("📌 اختر المؤشر أو الفئة:", list(EGX_ASSETS.keys()))
current_assets = EGX_ASSETS[selected_category]

st.divider()
# شريط التنقل المستقل لكل قسم
page = st.radio(
    "اختر القسم المطلوب:",
    [
        "🎯 1. التوصيات والتوقيتات",
        "⚖️ 2. حاسبة المخاطر والفرصة البديلة",
        "📈 3. الرسم البياني المتقدم",
        "🏦 4. الصناديق والتحليل المالي"
    ],
    horizontal=True
)
st.divider()

# دالة حساب المؤشرات الفنية (سريعة ومؤمّنة)
def add_technical_indicators(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()
    return df

# محرك التوصيات
def generate_recommendation(last, prev, vol_ratio):
    score = 50
    reasons = []
    
    if last['RSI'] < 30:
        score += 25
        reasons.append("تشبع بيعي حاد (فرصة ارتداد)")
    elif 30 <= last['RSI'] <= 45:
        score += 15
        reasons.append("منطقة تجميع جيدة")
    elif last['RSI'] > 75:
        score -= 25
        reasons.append("تشبع شرائي مرتفع")
    elif 65 < last['RSI'] <= 75:
        score -= 10
        reasons.append("اقتراب من القمة")

    if last['Close'] > last['SMA_20'] and last['SMA_20'] > last['SMA_50']:
        score += 15
        reasons.append("اتجاه صاعد مؤكد")
    elif last['Close'] < last['SMA_20'] and last['Close'] < last['SMA_50']:
        score -= 15
        reasons.append("اتجاه هابط")

    if last['MACD'] > last['Signal_Line'] and prev['MACD'] <= prev['Signal_Line']:
        score += 20
        reasons.append("تقاطع MACD إيجابي")
    elif last['MACD'] < last['Signal_Line'] and prev['MACD'] >= prev['Signal_Line']:
        score -= 20
        reasons.append("تقاطع MACD سلبي")

    if vol_ratio > 1.4 and last['Close'] > prev['Close']:
        score += 10
        reasons.append("سيولة شرائية قوية")

    score = max(0, min(100, score))
    
    if score >= 75:
        action = "شراء قوي (توقيت مثالي) 🟢"
    elif score >= 60:
        action = "تجميع / شراء تدريجي 🔵"
    elif score >= 45:
        action = "انتظار / احتفاظ ⚪"
    elif score >= 30:
        action = "جني أرباح / تخفيف 🟠"
    else:
        action = "بيع / تجنب الدخول 🔴"
        
    timing_note = " + ".join(reasons) if reasons else "حركة عرضية مستقرة"
    return score, action, timing_note

# دالة المسح السريع باستخدام yf.download
@st.cache_data(ttl=900)
def scan_assets_fast(assets_dict):
    results = []
    for symbol, name in assets_dict.items():
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df.empty or len(df) < 30:
                continue
            
            df = add_technical_indicators(df)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            change_pct = ((float(last['Close']) - float(prev['Close'])) / float(prev['Close'])) * 100
            vol_ratio = float(last['Volume']) / float(last['Vol_Avg']) if float(last['Vol_Avg']) > 0 else 1.0
            score, action, timing_note = generate_recommendation(last, prev, vol_ratio)
            
            suggested_stop = round(float(last['Close'] - (1.5 * last['ATR'])), 2)
            suggested_target = round(float(last['Close'] + (3.0 * last['ATR'])), 2)

            results.append({
                "الرمز": symbol.replace(".CA", ""),
                "الاسم": name,
                "السعر": round(float(last['Close']), 2),
                "التغير %": round(change_pct, 2),
                "التقييم (100)": int(score),
                "التوصية والقرار": action,
                "سبب التوقيت": timing_note,
                "وقف خسارة مقترح": suggested_stop,
                "هدف بيع مقترح": suggested_target,
                "RSI": round(float(last['RSI']), 1)
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# ==========================================
# القسم 1: التوصيات والتوقيتات
# ==========================================
if page == "🎯 1. التوصيات والتوقيتات":
    st.subheader(f"توصيات الشراء والبيع - {selected_category}")
    with st.spinner("جاري فحص الأسهم بسرعة..."):
        df_assets = scan_assets_fast(current_assets)
        
    if not df_assets.empty:
        df_sorted = df_assets.sort_values(by="التقييم (100)", ascending=False).reset_index(drop=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("أفضل فرصة حالياً", str(df_sorted.loc[0, "الاسم"]), f"تقييم: {df_sorted.loc[0, 'التقييم (100)']}/100")
        c2.metric("توصيات الشراء والتجميع", int(len(df_sorted[df_sorted["التقييم (100)"] >= 60])))
        c3.metric("توصيات البيع وجني الأرباح", int(len(df_sorted[df_sorted["التقييم (100)"] < 45])))

        st.dataframe(df_sorted, use_container_width=True, hide_index=True)
    else:
        st.warning("تعذر جلب البيانات حالياً.")

# ==========================================
# القسم 2: حاسبة المخاطر وتكلفة الفرصة البديلة
# ==========================================
elif page == "⚖️ 2. حاسبة المخاطر والفرصة البديلة":
    st.subheader("⚖️ أداة إدارة المخاطر وتكلفة الفرصة البديلة")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        capital = st.number_input("إجمالي رأس مال المحفظة (جنيه مصري):", min_value=1000.0, value=100000.0, step=5000.0)
        risk_pct = st.slider("نسبة المخاطرة المقبولة في الصفقة (%):", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
        risk_free_annual = st.number_input("العائد السنوي للفرصة البديلة الآمنة (%):", min_value=5.0, max_value=40.0, value=25.0, step=0.5)
        holding_days = st.number_input("المدة المتوقعة للاحتفاظ بالسهم (أيام):", min_value=1, max_value=365, value=30)

    with col_in2:
        entry_price = st.number_input("سعر الشراء المستهدف (جنيه):", min_value=0.1, value=50.0, step=0.5)
        stop_loss = st.number_input("سعر وقف الخسارة (جنيه):", min_value=0.1, value=47.0, step=0.5)
        target_price = st.number_input("سعر البيع المستهدف (جنيه):", min_value=0.1, value=58.0, step=0.5)

    if entry_price > stop_loss and target_price > entry_price:
        max_risk_egp = capital * (risk_pct / 100)
        risk_per_share = entry_price - stop_loss
        reward_per_share = target_price - entry_price
        
        recommended_shares = int(max_risk_egp // risk_per_share)
        position_value = recommended_shares * entry_price
        expected_profit = recommended_shares * reward_per_share
        rr_ratio = reward_per_share / risk_per_share
        
        opportunity_cost_egp = position_value * (risk_free_annual / 100) * (holding_days / 365)
        net_alpha = expected_profit - opportunity_cost_egp

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("الكمية المثالية للشراء", f"{recommended_shares} سهم", f"بقيمة {position_value:,.0f} ج.م")
        m2.metric("نسبة العائد للمخاطرة", f"1 : {rr_ratio:.2f}")
        m3.metric("الربح المتوقع", f"{expected_profit:,.0f} ج.م")
        m4.metric("تكلفة الفرصة البديلة", f"{opportunity_cost_egp:,.0f} ج.م")

        if net_alpha > 0 and rr_ratio >= 1.5:
            st.success(f"✅ صفقة مجدية: تتفوق على العائد الآمن بصافي ميزة **{net_alpha:,.0f} جنيه**.")
        else:
            st.warning(f"⚠️ تنبيه: العائد المتوقع أقل من الفرصة البديلة أو المخاطرة مرتفعة (الفرق: {net_alpha:,.0f} جنيه).")

# ==========================================
# القسم 3: الرسم البياني المتقدم (مستقل وسريع)
# ==========================================
elif page == "📈 3. الرسم البياني المتقدم":
    st.subheader("📈 الرسم البياني الفني والشموع اليابانية")
    asset_map = {f"{v} ({k.replace('.CA', '')})": k for k, v in current_assets.items()}
