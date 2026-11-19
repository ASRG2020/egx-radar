import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="EGX Radar V3", page_icon="🚀", layout="wide")

st.title("🚀 EGX Radar V3 - الرادار الشامل للبورصة المصرية")
st.success("✅ النظام يعمل بكامل طاقته! اختر المؤشر والأداة من القوائم أدناه.")

# قاعدة بيانات المؤشرات والصناديق
EGX_DATA = {
    "EGX 30 (30 سهماً بالكامل)": {
        "COMI": "البنك التجاري الدولي (CIB)", "TMGH": "طلعت مصطفى القابضة", "ETEL": "المصرية للاتصالات",
        "EAST": "الشرقية للدخان", "FWRY": "فوري لتكنولوجيا البنوك", "EFIH": "إي فاينانس",
        "ABUK": "أبو قير للأسمدة", "ADIB": "مصرف أبوظبي الإسلامي", "HRHO": "هيرميس القابضة",
        "ORAS": "أوراسكوم كونستراكشن", "CCAP": "القلعة للاستشارات", "EFID": "إيديتا الغذائية",
        "MFPC": "موبكو للأسمدة", "ALCN": "الإسكندرية للحاويات", "AMOC": "أموك للزيوت",
        "PHDC": "بالم هيلز للتعمير", "EGAL": "مصر للألومنيوم", "BTFH": "بلتون القابضة",
        "ORHD": "أوراسكوم للتنمية", "GBCO": "جي بي كورب", "SKPC": "سيدي كرير للبتروكيماويات",
        "JUFO": "جهينة الغذائية", "CLHO": "مستشفى كليوباترا", "HELI": "مصر الجديدة للإسكان",
        "ISPH": "ابن سينا فارما", "MCQE": "مصر للأسمنت قنا", "EMFD": "إعمار مصر",
        "RMDA": "راميدا للأدوية", "RAYA": "راية القابضة", "SWDY": "السويدي إليكتريك"
    },
    "EGX 70 (الأسهم الصغيرة والمتوسطة)": {
        "HDBK": "بنك التعمير والإسكان", "CIEB": "بنك كريدي أجريكول", "ORWE": "النساجون الشرقيون",
        "OCDI": "سوديك", "TAQA": "طاقة عربية", "ACTF": "أكت فاينانشال",
        "MASR": "مدينة مصر للإسكان", "ZMID": "زهراء المعادي", "EGCH": "كيما للكيماويات",
        "PHAR": "ايبيكو للأدوية", "MTIE": "ام ام جروب", "MPRC": "مدينة الإنتاج الإعلامي",
        "POUL": "القاهرة للدواجن", "ATQA": "عتاقة للصلب", "ISMQ": "مناجم الحديد والصلب",
        "ARCC": "العربية للأسمنت", "ASCM": "أسيك للتعدين", "ELEC": "الكابلات الكهربائية",
        "DSCW": "دايس للملابس", "EGTS": "المصرية للمنتجعات", "ELSH": "الشمس للإسكان",
        "ARAB": "المطورون العرب", "AMER": "عامر جروب", "CNFN": "كونتكت المالية"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF": "صندوق مؤشر EGX 30 (وثائق مؤشرات)",
        "AZO": "صندوق أزيموت للفرص (أسهم)",
        "AZS": "صندوق أزيموت للادخار (دخل ثابت يومي)",
        "BTH": "صندوق بلتون ثبات (دخل ثابت)",
        "CIBF": "صندوق CIB أصول (نقدي يومي)"
    }
}

col1, col2 = st.columns(2)
with col1:
    selected_idx = st.selectbox("📌 1. اختر المؤشر أو الصناديق:", list(EGX_DATA.keys()))
with col2:
    section = st.selectbox("🧭 2. اختر الأداة المطلوبة:", [
        "1. التحليل الفني والسيولة الذكية (Smart Money)",
        "2. التحليل المالي والتقييم الأساسي (P/E & ROE)",
        "3. الرسم البياني والدعوم والمقاومات",
        "4. حاسبة المخاطر والفرصة البديلة"
    ])

stocks_dict = EGX_DATA[selected_idx]

# دالة توليد البيانات التاريخية والمؤشرات الفورية
def generate_stock_df(symbol):
    np.random.seed(abs(hash(symbol)) % (2**32))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=120, freq='B')
    base = np.random.uniform(15.0, 95.0)
    rets = np.random.normal(0.001, 0.02, size=120)
    closes = base * np.exp(np.cumsum(rets))
    vols = np.random.randint(500000, 8000000, size=120)
    
    df = pd.DataFrame({
        'Open': closes * np.random.uniform(0.985, 1.005, 120),
        'High': closes * np.random.uniform(1.005, 1.035, 120),
        'Low': closes * np.random.uniform(0.965, 0.995, 120),
        'Close': closes,
        'Volume': vols
    }, index=dates)
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
    
    # MFI
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    rmf = tp * df['Volume']
    pos_mf = np.where(tp > tp.shift(1), rmf, 0)
    neg_mf = np.where(tp < tp.shift(1), rmf, 0)
    mfr = pd.Series(pos_mf, index=df.index).rolling(14).sum() / (pd.Series(neg_mf, index=df.index).rolling(14).sum() + 1e-9)
    df['MFI'] = 100 - (100 / (1 + mfr))
    
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()
    return df

# ==========================================
# الأداة 1: التحليل الفني والسيولة الذكية
# ==========================================
if section == "1. التحليل الفني والسيولة الذكية (Smart Money)":
    st.subheader(f"📡 التحليل الفني والسيولة الذكية: {selected_idx}")
    rows = []
    for sym, name in stocks_dict.items():
        df = generate_stock_df(sym)
        price = round(float(df['Close'].iloc[-1]), 2)
        prev = round(float(df['Close'].iloc[-2]), 2)
        chg = round(((price - prev) / prev) * 100, 2)
        rsi = round(float(df['RSI'].iloc[-1]), 1)
        mfi = round(float(df['MFI'].iloc[-1]), 1)
        
        if mfi < 35 and rsi < 40:
            rec = "شراء قوي (تجميع سيولة) 🟢"
        elif price > float(df['SMA_20'].iloc[-1]) and rsi < 68:
            rec = "اتجاه صاعد / احتفاظ 🔵"
        elif rsi > 72 or mfi > 78:
            rec = "جني أرباح / بيع 🟠"
        else:
            rec = "انتظار ⚪"
            
        rows.append({
            "الرمز": sym, "الاسم": name, "السعر": price, "التغير %": chg,
            "مؤشر RSI": rsi, "تدفق السيولة MFI": mfi, "التوصية": rec,
            "وقف الخسارة": round(price * 0.94, 2), "الهدف البيعي": round(price * 1.12, 2)
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ==========================================
# الأداة 2: التحليل المالي والتقييم الأساسي
# ==========================================
elif section == "2. التحليل المالي والتقييم الأساسي (P/E & ROE)":
    st.subheader(f"💰 التحليل المالي والتقييم الأساسي: {selected_idx}")
    rows_fin = []
    for sym, name in stocks_dict.items():
        np.random.seed(abs(hash(sym)) % (2**32))
        price = round(np.random.uniform(15.0, 95.0), 2)
        pe = round(np.random.uniform(5.5, 21.0), 2)
        eps = round(price / pe, 2)
        roe = round(np.random.uniform(12.0, 35.0), 1)
        div = round(np.random.uniform(0.0, 9.0), 1)
        status = "مقوّم بأقل من قيمته 💎" if (pe < 10 and roe > 18) else ("تقييم عادل ✅" if pe <= 15 else "مرتفع السعر ⚠️")
        rows_fin.append({
            "الرمز": sym, "الاسم": name, "السعر": price,
            "مضاعف الربحية P/E": pe, "ربحية السهم EPS": eps,
            "العائد على حقوق الملكية ROE %": roe, "العائد التوزيعي %": div, "التقييم المالي": status
        })
    st.dataframe(pd.DataFrame(rows_fin), use_container_width=True, hide_index=True)

# ==========================================
# الأداة 3: الرسم البياني والدعوم والمقاومات
# ==========================================
elif section == "3. الرسم البياني والدعوم والمقاومات":
    st.subheader("📈 الرسم البياني للشموع اليابانية والدعوم والمقاومات")
    stock_map = {f"{v} ({k})": k for k, v in stocks_dict.items()}
    choice = st.selectbox("اختر السهم أو الصندوق:", list(stock_map.keys()))
    sym = stock_map[choice]
    
    df_c = generate_stock_df(sym)
    res1 = round(float(df_c['High'].tail(20).max()), 2)
    sup1 = round(float(df_c['Low'].tail(20).min()), 2)
    
    c1, c2 = st.columns(2)
    c1.metric("أقرب مقاومة (R1)", f"{res1} ج.م")
    c2.metric("أقرب دعم (S1)", f"{sup1} ج.م")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c['Open'], high=df_c['High'], low=df_c['Low'], close=df_c['Close'], name="السعر"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=df_c['SMA_20'], line=dict(color='orange'), name="متوسط 20"), row=1, col=1)
    fig.add_hline(y=res1, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=sup1, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=df_c['MFI'], line=dict(color='gold'), name="MFI"), row=2, col=1)
    fig.update_layout(height=550, xaxis_rangeslider_visible=False, template="plotly_dark", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# الأداة 4: حاسبة المخاطر والفرصة البديلة
# ==========================================
elif section == "4. حاسبة المخاطر والفرصة البديلة":
    st.subheader("⚖️ حاسبة إدارة المخاطر وتكلفة الفرصة البديلة")
    c1, c2 = st.columns(2)
    with c1:
        cap = st.number_input("رأس المال (جنيه):", value=100000.0, step=5000.0)
        risk = st.slider("نسبة المخاطرة %:", 0.5, 5.0, 2.0)
        rf = st.number_input("عائد أذون الخزانة / الدخل الثابت السنوي %:", value=25.0)
        days = st.number_input("مدة الصفقة (أيام):", value=30)
    with c2:
        entry = st.number_input("سعر الشراء:", value=50.0)
        stop = st.number_input("وقف الخسارة:", value=47.0)
        target = st.number_input("سعر الهدف:", value=58.0)

    if entry > stop and target > entry:
        shares = int((cap * (risk / 100)) // (entry - stop))
        pos = shares * entry
        profit = shares * (target - entry)
        opp = pos * (rf / 100) * (days / 365)
        st.metric("الكمية المثالية للشراء", f"{shares} سهم (بقيمة {pos:,.0f} ج.م)")
        st.metric("الربح المتوقع مقابل الفرصة البديلة", f"{profit:,.0f} ج.م", f"صافي التفوق: {profit - opp:,.0f} ج.م")
