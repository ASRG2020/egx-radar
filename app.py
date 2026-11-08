import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعدادات الصفحة
st.set_page_config(page_title="EGX Radar Pro", page_icon="📊", layout="wide")

st.title("📊 EGX Radar Pro - رادار البورصة المصرية الشامل")
st.markdown("منصة التحليل الفني والمالي التفاعلي لمؤشرات وأسهم البورصة المصرية.")

# قاعدة بيانات المؤشرات والأسهم التابعة لها
EGX_INDICES = {
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
        "EFIH.CA": "إي فاينانس",
        "ORHD.CA": "أوراسكوم للتنمية",
        "JUFO.CA": "جهينة للصناعات الغذائية"
    },
    "EGX 70 (الأسهم الصغيرة والمتوسطة)": {
        "BINV.CA": "بي إنفستمنتس القابضة",
        "DSCW.CA": "دايس للملابس الجاهزة",
        "ASCM.CA": "أسيك للتعدين",
        "CCAP.CA": "القلعة للاستشارات",
        "EGTS.CA": "المصرية للمنتجعات",
        "ELSH.CA": "الشمس للإسكان",
        "ISMA.CA": "الإسماعيلية مصر للدواجن",
        "MPRC.CA": "مدينة الإنتاج الإعلامي",
        "OFH.CA": "أوراسكوم المالية",
        "RACC.CA": "راية لخدمات مراكز الاتصالات",
        "SDTI.CA": "شارم دريمز",
        "UEGC.CA": "الصعيد العامة للمقاولات"
    }
}

# القائمة الجانبية للتحكم
st.sidebar.header("⚙️ إعدادات الرادار")
selected_index = st.sidebar.selectbox("اختر مؤشر البورصة:", list(EGX_INDICES.keys()))
current_stocks = EGX_INDICES[selected_index]

if st.sidebar.button("🔄 تحديث البيانات الحية", use_container_width=True):
    st.cache_data.clear()

# دوال حساب المؤشرات الفنية
def add_technical_indicators(df):
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # المتوسطات المتحركة
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # بولينجر باند
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['SMA_20'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['SMA_20'] - (df['BB_Std'] * 2)
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # متوسط السيولة
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    return df

# جلب بيانات المسح الشامل للمؤشر المختار
@st.cache_data(ttl=900)
def scan_index(stocks_dict):
    results = []
    for symbol, name in stocks_dict.items():
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
            
            # تحليل الإشارة المركبة
            signals = []
            if last['RSI'] < 35:
                signals.append("تشبع بيعي 🟢")
            elif last['RSI'] > 70:
                signals.append("تشبع شرائي 🔴")
                
            if last['MACD'] > last['Signal_Line'] and prev['MACD'] <= prev['Signal_Line']:
                signals.append("تقاطع MACD إيجابي 🚀")
                
            if last['Close'] > last['SMA_20'] and vol_ratio > 1.3:
                signals.append("اختراق بسيولة 🔥")
                
            final_signal = " | ".join(signals) if signals else ("اتجاه صاعد 🔵" if last['Close'] > last['SMA_20'] else "حيادي / هابط ⚪")

            # جلب البيانات المالية الأساسية
            info = ticker.info
            pe_ratio = info.get('trailingPE', None)
            eps = info.get('trailingEps', None)
            mkt_cap = info.get('marketCap', None)

            results.append({
                "الرمز": symbol.replace(".CA", ""),
                "اسم السهم": name,
                "السعر": round(last['Close'], 2),
                "التغير %": round(change_pct, 2),
                "RSI": round(last['RSI'], 1),
                "السيولة": f"{round(vol_ratio, 1)}x",
                "مضاعف الربحية P/E": round(pe_ratio, 2) if pe_ratio else "غير متاح",
                "ربحية السهم EPS": round(eps, 2) if eps else "غير متاح",
                "القيمة السوقية (مليار)": round(mkt_cap / 1e9, 2) if mkt_cap else "غير متاح",
                "الإشارة الفنية": final_signal
            })
        except Exception:
            continue
    return pd.DataFrame(results)

# تقسيم الواجهة إلى 3 تبويبات تفاعلية
tab1, tab2, tab3 = st.tabs(["📡 رادار الفرص الشامل", "📈 التحليل الفني والرسم البياني", "💰 التحليل المالي ومقارنة الأسهم"])

with st.spinner("جاري جلب وتحليل بيانات المؤشر..."):
    df_market = scan_index(current_stocks)

# --- التبويب الأول: رادار السوق ---
with tab1:
    st.subheader(f"ملخص حركة أسهم {selected_index}")
    if not df_market.empty:
        # بطاقات إحصائية سريعة
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("الأسهم المفحوصة", len(df_market))
        col2.metric("أسهم صاعدة اليوم", len(df_market[df_market["التغير %"] > 0]))
        col3.metric("فرص تشبع بيعي (RSI<35)", len(df_market[df_market["RSI"] < 35]))
        col4.metric("إشارات اختراق/MACD", len(df_market[df_market["الإشارة الفنية"].str.contains("🚀|🔥")]))

        # أزرار تصفية سريعة
        filter_type = st.radio(
            "تصفية الجدول:",
            ["الكل", "الفرص الإيجابية فقط", "الأسهم الأرخص مالياً (P/E أقل من 15)"],
            horizontal=True
        )
        
        display_df = df_market.copy()
        if filter_type == "الفرص الإيجابية فقط":
            display_df = display_df[display_df["الإشارة الفنية"].str.contains("🟢|🚀|🔥|🔵")]
        elif filter_type == "الأسهم الأرخص مالياً (P/E أقل من 15)":
            display_df = display_df[pd.to_numeric(display_df["مضاعف الربحية P/E"], errors='coerce') < 15]

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("لا توجد بيانات متاحة حالياً لهذا المؤشر.")

# --- التبويب الثاني: الرسم البياني التفاعلي ---
with tab2:
    st.subheader("الرسم البياني التفاعلي والمؤشرات الفنية")
    stock_names = {f"{v} ({k.replace('.CA', '')})": k for k, v in current_stocks.items()}
    selected_label = st.selectbox("اختر السهم لعرض الرسم البياني:", list(stock_names.keys()))
    selected_symbol = stock_names[selected_label]
    
    period = st.select_slider("الفترة الزمنية:", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    
    df_chart = yf.Ticker(selected_symbol).history(period=period, interval="1d")
    if not df_chart.empty:
        df_chart = add_technical_indicators(df_chart)
        
        # إنشاء رسم بياني من 3 طبقات (الشموع + البولينجر، RSI، MACD)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.55, 0.22, 0.23],
                            subplot_titles=("حركة السعر ونطاقات بولينجر", "مؤشر القوة النسبية (RSI)", "مؤشر الماكد (MACD)"))

        # الشموع اليابانية
        fig.add_trace(go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
                                     low=df_chart['Low'], close=df_chart['Close'], name="السعر"), row=1, col=1)
        # المتوسطات وبولينجر
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['SMA_20'], line=dict(color='orange', width=1.5), name="متوسط 20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Upper'], line=dict(color='gray', dash='dot'), name="بولينجر علوي"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['BB_Lower'], line=dict(color='gray', dash='dot'), name="بولينجر سفلي"), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], line=dict(color='purple', width=2), name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MACD'], line=dict(color='blue', width=1.5), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Signal_Line'], line=dict(color='red', width=1.5), name="Signal"), row=3, col=1)

        fig.update_layout(height=750, xaxis_rangeslider_visible=False, template="plotly_dark", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# --- التبويب الثالث: التحليل المالي ---
with tab3:
    st.subheader("البيانات المالية والتقييم الأساسي للسهم")
    if not df_market.empty:
        fin_cols = ["الرمز", "اسم السهم", "السعر", "مضاعف الربحية P/E", "ربحية السهم EPS", "القيمة السوقية (مليار)"]
        st.dataframe(df_market[fin_cols], use_container_width=True, hide_index=True)
        
        st.info("💡 **دليل القراءة المالية السريع:**\n"
                "- **مضاعف الربحية (P/E):** كلما انخفض الرقم (أقل من 10-12 في السوق المصري) دلّ ذلك على أن السهم يتداول بسعر رخيص مقارنة بأرباحه.\n"
