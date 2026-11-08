import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعدادات الصفحة
st.set_page_config(page_title="EGX Radar Ultimate", page_icon="🎯", layout="wide")

st.title("🎯 EGX Radar Ultimate - مستشار البورصة المصرية الذكي")
st.markdown("تحليل فني ومالي متكامل، صناديق الاستثمار، وحاسبة المخاطر وتكلفة الفرصة البديلة.")

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
        "AMOC.CA": "أموك للزيوت",
        "SKPC.CA": "سيدي كرير للبتروكيماويات",
        "ADIB.CA": "مصرف أبوظبي الإسلامي",
        "EFIH.CA": "إي فاينانس"
    },
    "EGX 70 (الأسهم الصغيرة والمتوسطة)": {
        "BINV.CA": "بي إنفستمنتس القابضة",
        "DSCW.CA": "دايس للملابس الجاهزة",
        "ASCM.CA": "أسيك للتعدين",
        "CCAP.CA": "القلعة للاستشارات",
        "EGTS.CA": "المصرية للمنتجعات",
        "ELSH.CA": "الشمس للإسكان",
        "MPRC.CA": "مدينة الإنتاج الإعلامي",
        "OFH.CA": "أوراسكوم المالية",
        "RACC.CA": "راية لخدمات مراكز الاتصالات"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF.CA": "صندوق مؤشر EGX 30 (وثائق مؤشرات)",
        "CIB.CA": "وثائق وصناديق بنك CIB / أصول",
        "BTFH.CA": "بلتون القابضة (صناديق الذهب والدخل الثابت)",
        "HRHO.CA": "إي إف جي القابضة (صناديق الدخل والأسهم)",
        "ACTF.CA": "أكت فاينانشال (صناديق واستثمار)"
    }
}

# القائمة الجانبية
st.sidebar.header("⚙️ لوحة التحكم")
selected_category = st.sidebar.selectbox("اختر الفئة أو المؤشر:", list(EGX_ASSETS.keys()))
current_assets = EGX_ASSETS[selected_category]

if st.sidebar.button("🔄 تحديث أسعار السوق", use_container_width=True):
    st.cache_data.clear()

# حساب المؤشرات الفنية
def add_technical_indicators(df):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['BB_Std'] * 2)
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    # حساب التذبذب اليومي (ATR مبسط) لتحديد وقف الخسارة المقترح
    df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()
    return df

# محرك التوصيات والتوقيتات الذكي
def generate_recommendation(last, prev, vol_ratio):
    score = 50  # نقطة البداية الحيادية
    reasons = []
    
    # 1. تحليل RSI
    if last['RSI'] < 30:
        score += 25
        reasons.append("تشبع بيعي حاد (فرصة ارتداد)")
    elif 30 <= last['RSI'] <= 45:
        score += 15
        reasons.append("منطقة تجميع جيدة")
    elif last['RSI'] > 75:
        score -= 25
        reasons.append("تشبع شرائي مرتفع (احتمال جني أرباح)")
    elif 65 < last['RSI'] <= 75:
        score -= 10
        reasons.append("اقتراب من القمة")

    # 2. تحليل الاتجاه والمتوسطات
    if last['Close'] > last['SMA_20'] and last['SMA_20'] > last['SMA_50']:
        score += 15
        reasons.append("اتجاه صاعد مؤكد")
    elif last['Close'] < last['SMA_20'] and last['Close'] < last['SMA_50']:
        score -= 15
        reasons.append("اتجاه هابط")

    # 3. تحليل MACD
    if last['MACD'] > last['Signal_Line'] and prev['MACD'] <= prev['Signal_Line']:
        score += 20
        reasons.append("تقاطع MACD إيجابي جديد")
    elif last['MACD'] < last['Signal_Line'] and prev['MACD'] >= prev['Signal_Line']:
        score -= 20
        reasons.append("تقاطع MACD سلبي")

    # 4. تحليل السيولة
    if vol_ratio > 1.4 and last['Close'] > prev['Close']:
        score += 10
        reasons.append("دخول سيولة شرائية قوية")

    score = max(0, min(100, score))
    
    if score >= 75:
        action = "شراء قوي (توقيت دخول مثالي) 🟢"
    elif score >= 60:
        action = "تجميع / شراء تدريجي 🔵"
    elif score >= 45:
        action = "انتظار / احتفاظ ⚪"
    elif score >= 30:
        action = "تخفيف مراكز / جني أرباح 🟠"
    else:
        action = "بيع / تجنب الدخول حالياً 🔴"
        
    timing_note = " + ".join(reasons) if reasons else "حركة عرضية مستقرة"
    return score, action, timing_note

@st.cache_data(ttl=900)
def scan_assets(assets_dict):
    results = []
    for symbol, name in assets_dict.items():
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval="1d")
            if df.empty or len(df) < 30:
                continue
            
            df = add_technical_indicators(df)
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            change_pct = ((last['Close'] - prev['Close']) / prev['Close']) * 100
            vol_ratio = last['Volume'] / last['Vol_Avg'] if last['Vol_Avg'] > 0 else 1.0
            score, action, timing_note = generate_recommendation(last, prev, vol_ratio)
            
            # مستويات مقترحة للصفقة بناء على ATR
            suggested_stop = round(last['Close'] - (1.5 * last['ATR']), 2)
            suggested_target = round(last['Close'] + (3.0 * last['ATR']), 2)

            info = ticker.info
            pe_ratio = info.get('trailingPE', None)
            eps = info.get('trailingEps', None)

            results.append({
                "الرمز": symbol.replace(".CA", ""),
                "الاسم": name,
                "السعر": round(last['Close'], 2),
                "التغير %": round(change_pct, 2),
                "التقييم (100)": score,
                "التوصية والقرار": action,
                "سبب التوقيت": timing_note,
                "وقف خسارة مقترح": suggested_stop,
                "هدف بيع مقترح": suggested_target,
                "RSI": round(last['RSI'], 1),
                "P/E": round(pe_ratio, 2) if pe_ratio else "-",
                "EPS": round(eps, 2) if eps else "-"
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# التبويبات الأربعة الرئيسية
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 التوصيات والتوقيتات",
    "⚖️ حاسبة المخاطر والفرصة البديلة",
    "📈 الرسم البياني المتقدم",
    "🏦 الصناديق والتحليل المالي"
])

with st.spinner("جاري تحليل السوق وحساب التوصيات..."):
    df_assets = scan_assets(current_assets)

# --- التبويب الأول: التوصيات والتوقيتات ---
with tab1:
    st.subheader(f"توصيات الشراء والبيع وتوقيتات الدخول - {selected_category}")
    if not df_assets.empty:
        df_sorted = df_assets.sort_values(by="التقييم (100)", ascending=False)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("أفضل فرصة حالياً", df_sorted.iloc[0]["الاسم"], f"تقييم: {df_sorted.iloc[0]['التقييم (100)']}/100")
        c2.metric("توصيات الشراء والتجميع", len(df_sorted[df_sorted["التقييم (100)"] >= 60]))
        c3.metric("توصيات البيع وجني الأرباح", len(df_sorted[df_sorted["التقييم (100)"] < 45]))

        st.dataframe(
            df_sorted[["الرمز", "الاسم", "السعر", "التغير %", "التقييم (100)", "التوصية والقرار", "سبب التوقيت", "وقف خسارة مقترح", "هدف بيع مقترح"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("لا توجد بيانات متاحة حالياً.")

# --- التبويب الثاني: حاسبة المخاطر وتكلفة الفرصة البديلة ---
with tab2:
    st.subheader("⚖️ أداة إدارة المخاطر وتكلفة الفرصة البديلة")
    st.markdown("قيّم جدوى الصفقة قبل الدخول وقارن عائدها المتوقع بالعائد الخالي من المخاطر (أذون الخزانة وصناديق الدخل الثابت).")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        capital = st.number_input("إجمالي رأس مال المحفظة (جنيه مصري):", min_value=1000.0, value=100000.0, step=5000.0)
        risk_pct = st.slider("نسبة المخاطرة المقبولة في الصفقة الواحدة (%):", min_value=0.5, max_value=5.0, value=2.0, step=0.5)
        risk_free_annual = st.number_input("العائد السنوي للفرصة البديلة الآمنة (أذون خزانة / دخل ثابت %):", min_value=5.0, max_value=40.0, value=25.0, step=0.5)
        holding_days = st.number_input("المدة المتوقعة للاحتفاظ بالسهم (بالأيام):", min_value=1, max_value=365, value=30)

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
        expected_return_pct = (reward_per_share / entry_price) * 100
        rr_ratio = reward_per_share / risk_per_share
        
        # حساب تكلفة الفرصة البديلة لنفس المبلغ ونفس المدة
        opportunity_cost_egp = position_value * (risk_free_annual / 100) * (holding_days / 365)
