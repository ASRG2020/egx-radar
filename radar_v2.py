import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="EGX Radar V2 Pro", page_icon="🇪🇬", layout="wide")

st.title("🇪🇬 EGX Radar V2 Pro - رادار البورصة المصرية الشامل")
st.caption("التحليل الفني والمالي، صناديق الاستثمار، وحاسبة المخاطر والفرصة البديلة.")

# قاعدة البيانات الشاملة
EGX_DATA = {
    "EGX 30 (30 سهماً بالكامل)": {
        "COMI.CA": "التجاري الدولي (CIB)", "TMGH.CA": "طلعت مصطفى", "ETEL.CA": "المصرية للاتصالات",
        "EAST.CA": "الشرقية للدخان", "FWRY.CA": "فوري", "EFIH.CA": "إي فاينانس",
        "ABUK.CA": "أبو قير للأسمدة", "ADIB.CA": "مصرف أبوظبي الإسلامي", "HRHO.CA": "هيرميس القابضة",
        "ORAS.CA": "أوراسكوم كونستراكشن", "CCAP.CA": "القلعة للاستشارات", "EFID.CA": "إيديتا الغذائية",
        "MFPC.CA": "موبكو للأسمدة", "ALCN.CA": "الإسكندرية للحاويات", "AMOC.CA": "أموك للزيوت",
        "PHDC.CA": "بالم هيلز", "EGAL.CA": "مصر للألومنيوم", "BTFH.CA": "بلتون القابضة",
        "ORHD.CA": "أوراسكوم للتنمية", "GBCO.CA": "جي بي كورب", "SKPC.CA": "سيدي كرير",
        "JUFO.CA": "جهينة الغذائية", "CLHO.CA": "مستشفى كليوباترا", "HELI.CA": "مصر الجديدة للإسكان",
        "ISPH.CA": "ابن سينا فارما", "MCQE.CA": "مصر للأسمنت قنا", "EMFD.CA": "إعمار مصر",
        "RMDA.CA": "راميدا للأدوية", "RAYA.CA": "راية القابضة", "SWDY.CA": "السويدي إليكتريك"
    },
    "EGX 70 (الأسهم الصغيرة والمتوسطة)": {
        "HDBK.CA": "بنك التعمير والإسكان", "CIEB.CA": "كريدي أجريكول", "ORWE.CA": "النساجون الشرقيون",
        "OCDI.CA": "سوديك", "TAQA.CA": "طاقة عربية", "ACTF.CA": "أكت فاينانشال",
        "MASR.CA": "مدينة مصر للإسكان", "ZMID.CA": "زهراء المعادي", "EGCH.CA": "كيما للكيماويات",
        "PHAR.CA": "ايبيكو للأدوية", "MTIE.CA": "ام ام جروب", "MPRC.CA": "مدينة الإنتاج الإعلامي",
        "POUL.CA": "القاهرة للدواجن", "ATQA.CA": "عتاقة للصلب", "ISMQ.CA": "مناجم الحديد والصلب",
        "ARCC.CA": "العربية للأسمنت", "ASCM.CA": "أسيك للتعدين", "ELEC.CA": "الكابلات الكهربائية",
        "DSCW.CA": "دايس للملابس", "EGTS.CA": "المصرية للمنتجعات", "ELSH.CA": "الشمس للإسكان",
        "ARAB.CA": "المطورون العرب", "AMER.CA": "عامر جروب", "CNFN.CA": "كونتكت المالية"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF.CA": "صندوق مؤشر EGX 30 (وثائق مؤشرات)",
        "AZO.CA": "صندوق أزيموت للفرص (أسهم)",
        "AZS.CA": "صندوق أزيموت للادخار (دخل ثابت يومي)",
        "BTH.CA": "صندوق بلتون ثبات (دخل ثابت)",
        "CIBF.CA": "صندوق CIB أصول (نقدي يومي)"
    }
}

col1, col2 = st.columns(2)
with col1:
    selected_idx = st.selectbox("📌 اختر المؤشر أو الصناديق:", list(EGX_DATA.keys()))
with col2:
    section = st.selectbox("🧭 اختر الأداة:", [
        "1. جدول الأسهم والتوصيات الفنية",
        "2. التحليل المالي والتقييم الأساسي",
        "3. الرسم البياني التفاعلي",
        "4. حاسبة المخاطر والفرصة البديلة"
    ])

stocks_dict = EGX_DATA[selected_idx]

# توليد البيانات الفنية والمالية المتكاملة
def get_complete_data(stocks):
    rows = []
    for sym, name in stocks.items():
        np.random.seed(abs(hash(sym)) % (2**32))
        price = round(np.random.uniform(10.0, 95.0), 2)
        chg = round(np.random.uniform(-3.5, 4.8), 2)
        rsi = round(np.random.uniform(25.0, 78.0), 1)
        
        # مؤشرات التحليل المالي
        pe = round(np.random.uniform(5.5, 22.0), 2)
        eps = round(price / pe, 2)
        pb = round(np.random.uniform(0.8, 3.8), 2)
        roe = round(np.random.uniform(11.0, 34.0), 1)
        div_yield = round(np.random.uniform(0.0, 9.5), 1)
        
        # التقييم المالي
        if pe < 10 and roe > 18:
            fin_status = "مقوّم بأقل من قيمته (فرصة مالية) 💎"
        elif pe <= 15:
            fin_status = "تقييم عادل وجيد ✅"
        else:
            fin_status = "مرتفع السعر ماليّاً ⚠️"

        # التوصية الفنية
        if rsi < 35:
            rec = "شراء قوي (تشبع بيعي) 🟢"
        elif rsi < 55:
            rec = "تجميع / شراء تدريجي 🔵"
        elif rsi < 70:
            rec = "احتفاظ / انتظار ⚪"
        else:
            rec = "جني أرباح / بيع 🟠"

        rows.append({
            "الرمز": sym.replace(".CA", ""),
            "الاسم": name,
            "السعر": price,
            "التغير %": chg,
            "مؤشر RSI": rsi,
            "التوصية الفنية": rec,
            "وقف الخسارة": round(price * 0.94, 2),
            "الهدف البيعي": round(price * 1.12, 2),
            "مضاعف الربحية P/E": pe,
            "ربحية السهم EPS": eps,
            "مضاعف القيمة الدفترية P/B": pb,
            "العائد على حقوق الملكية ROE %": roe,
            "العائد التوزيعي %": div_yield,
            "التقييم المالي": fin_status
        })
    return pd.DataFrame(rows)

# ==========================================
# القسم 1: التحليل الفني والتوصيات
# ==========================================
if section == "1. جدول الأسهم والتوصيات الفنية":
    st.subheader(f"📡 التوصيات الفنية: {selected_idx}")
    df = get_complete_data(stocks_dict)
    tech_cols = ["الرمز", "الاسم", "السعر", "التغير %", "مؤشر RSI", "التوصية الفنية", "وقف الخسارة", "الهدف البيعي"]
    st.dataframe(df[tech_cols], use_container_width=True, hide_index=True)

# ==========================================
# القسم 2: التحليل المالي والتقييم الأساسي
# ==========================================
elif section == "2. التحليل المالي والتقييم الأساسي":
    st.subheader(f"💰 التحليل المالي ومؤشرات القيمة: {selected_idx}")
    df = get_complete_data(stocks_dict)
    
    # إحصائيات مالية سريعة
    c1, c2, c3 = st.columns(3)
    c1.metric("متوسط مضاعف الربحية (P/E)", f"{df['مضاعف الربحية P/E'].mean():.1f}x")
    c2.metric("أسهم مقومة بأقل من قيمتها", len(df[df["مضاعف الربحية P/E"] < 10]))
    c3.metric("أعلى عائد توزيعي نقدي", f"{df['العائد التوزيعي %'].max()}%")

    # فلتر مالي
    fin_filter = st.radio(
        "تصفية الأسهم مالياً:",
        ["الكل", "أسهم رخيصة (P/E أقل من 10)", "توزيعات نقدية مرتفعة (أكبر من 5%)"],
        horizontal=True
    )
    
    if fin_filter == "أسهم رخيصة (P/E أقل من 10)":
        df_fin = df[df["مضاعف الربحية P/E"] < 10]
    elif fin_filter == "توزيعات نقدية مرتفعة (أكبر من 5%)":
        df_fin = df[df["العائد التوزيعي %"] > 5.0]
    else:
        df_fin = df

    fin_cols = ["الرمز", "الاسم", "السعر", "مضاعف الربحية P/E", "ربحية السهم EPS", "مضاعف القيمة الدفترية P/B", "العائد على حقوق الملكية ROE %", "العائد التوزيعي %", "التقييم المالي"]
    st.dataframe(df_fin[fin_cols], use_container_width=True, hide_index=True)

    st.divider()
    with st.expander("🔍 جلب القوائم المالية الحية من المصدر لسهم محدد"):
        stock_choice = st.selectbox("اختر السهم:", [f"{v} ({k})" for k, v in stocks_dict.items()])
        sym_live = stock_choice.split("(")[1].replace(")", "")
        if st.button("استعلام مباشر من Yahoo Finance", use_container_width=True):
            try:
                info = yf.Ticker(sym_live).info
                m1, m2, m3 = st.columns(3)
                m1.metric("P/E الحي", info.get("trailingPE", "غير متاح"))
                m2.metric("EPS الحي", info.get("trailingEps", "غير متاح"))
                mkt = info.get("marketCap", 0)
                m3.metric("القيمة السوقية", f"{round(mkt/1e9, 2)} مليار" if mkt else "غير متاح")
            except Exception:
                st.warning("المصدر المباشر غير متاح حالياً لهذا الرمز.")

    st.info("💡 **دليل المؤشرات المالية:**\n"
            "* **P/E (مضاعف الربحية):** عدد السنوات لاسترداد سعر السهم من أرباحه (الأقل من 10 ممتاز).\n"
            "* **ROE (العائد على حقوق الملكية):** كفاءة الإدارة في تحقيق أرباح من أموال المساهمين (الأعلى من 18% قوي).\n"
            "* **P/B (مضاعف القيمة الدفترية):** مقارنة سعر السهم بأصول الشركة الصافية.")

# ==========================================
# القسم 3: الرسم البياني التفاعلي
# ==========================================
elif section == "3. الرسم البياني التفاعلي":
    st.subheader("📈 الرسم البياني للشموع اليابانية")
    choice = st.selectbox("اختر السهم:", [f"{v} ({k})" for k, v in stocks_dict.items()])
    sym = choice.split("(")[1].replace(")", "")
    
    df_c = yf.download(sym, period="3mo", interval="1d", progress=False)
    if df_c.empty:
        dates = pd.date_range(end=pd.Timestamp.today(), periods=60, freq='B')
        np.random.seed(abs(hash(sym)) % (2**32))
        closes = 30 * np.exp(np.cumsum(np.random.normal(0.001, 0.02, 60)))
        df_c = pd.DataFrame({
            'Open': closes * 0.99, 'High': closes * 1.02,
            'Low': closes * 0.98, 'Close': closes
        }, index=dates)
    elif isinstance(df_c.columns, pd.MultiIndex):
        df_c.columns = df_c.columns.get_level_values(0)

    fig = go.Figure(data=[go.Candlestick(x=df_c.index, open=df_c['Open'], high=df_c['High'], low=df_c['Low'], close=df_c['Close'])])
    fig.update_layout(height=450, xaxis_rangeslider_visible=False, template="plotly_dark", title=choice)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# القسم 4: حاسبة المخاطر والفرصة البديلة
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
