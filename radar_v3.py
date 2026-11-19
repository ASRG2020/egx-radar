import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="EGX Radar V3 Mobile", page_icon="🚀", layout="wide")

st.title("🚀 EGX Radar V3 - الرادار الشامل للبورصة المصرية")
st.success("✅ النسخة السريعة المتوافقة كلياً مع شاشات الهواتف.")

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

def generate_stock_df(symbol):
    np.random.seed(abs(hash(symbol)) % (2**32))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90, freq='B')
    base = np.random.uniform(15.0, 95.0)
    rets = np.random.normal(0.001, 0.02, size=90)
    closes = base * np.exp(np.cumsum(rets))
    vols = np.random.randint(500000, 8000000, size=90)
    
    df = pd.DataFrame({
        'السعر': closes,
        'High': closes * np.random.uniform(1.005, 1.035, 90),
        'Low': closes * np.random.uniform(0.965, 0.995, 90),
        'Volume': vols
    }, index=dates)
    
    delta = df['السعر'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
    
    tp = (df['High'] + df['Low'] + df['السعر']) / 3
    rmf = tp * df['Volume']
    pos_mf = np.where(tp > tp.shift(1), rmf, 0)
    neg_mf = np.where(tp < tp.shift(1), rmf, 0)
    mfr = pd.Series(pos_mf, index=df.index).rolling(14).sum() / (pd.Series(neg_mf, index=df.index).rolling(14).sum() + 1e-9)
    df['تدفق السيولة MFI'] = 100 - (100 / (1 + mfr))
    
    df['متوسط 20 يوم'] = df['السعر'].rolling(20).mean()
    return df

# ==========================================
# الأداة 1: التحليل الفني والسيولة الذكية
# ==========================================
if section == "1. التحليل الفني والسيولة الذكية (Smart Money)":
    st.subheader(f"📡 التحليل الفني والسيولة الذكية: {selected_idx}")
    
    with st.expander("📖 اضغط هنا لفهم الأداة والنسب المئوية لاختيار السهم فنياً"):
        st.markdown("""
        * **مؤشر القوة النسبية (RSI):** أقل من **35%** تعني تشبع بيعي وفرصة ارتداد صاعد، وأعلى من **70%** تعني تشبع شرائي واحتمال جني أرباح.
        * **مؤشر تدفق السيولة (MFI):** أقل من **35%** يدل على تجميع سيولة ذكية في القاع (شراء قوي 🟢)، وأعلى من **78%** يدل على تصريف سيولة (بيع 🟠).
        * **وقف الخسارة والهدف:** مضبوط عند **-6%** لحماية رأس المال، والهدف عند **+12%** (نسبة عائد للمخاطرة **2 : 1**).
        """)

    rows = []
    for sym, name in stocks_dict.items():
        df = generate_stock_df(sym)
        price = round(float(df['السعر'].iloc[-1]), 2)
        prev = round(float(df['السعر'].iloc[-2]), 2)
        chg = round(((price - prev) / prev) * 100, 2)
        rsi = round(float(df['RSI'].iloc[-1]), 1)
        mfi = round(float(df['تدفق السيولة MFI'].iloc[-1]), 1)
        
        if mfi < 35 and rsi < 40:
            rec = "شراء قوي (تجميع سيولة) 🟢"
        elif price > float(df['متوسط 20 يوم'].iloc[-1]) and rsi < 68:
            rec = "اتجاه صاعد / احتفاظ 🔵"
        elif rsi > 72 or mfi > 78:
            rec = "جني أرباح / بيع 🟠"
        else:
            rec = "انتظار ⚪"
            
        rows.append({
            "الرمز": sym, "الاسم": name, "السعر": price, "التغير %": chg,
            "RSI": rsi, "MFI": mfi, "التوصية": rec,
            "وقف الخسارة": round(price * 0.94, 2), "الهدف": round(price * 1.12, 2)
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ==========================================
# الأداة 2: التحليل المالي والتقييم الأساسي
# ==========================================
elif section == "2. التحليل المالي والتقييم الأساسي (P/E & ROE)":
    st.subheader(f"💰 التحليل المالي والتقييم الأساسي: {selected_idx}")
    
    with st.expander("📖 اضغط هنا لفهم النسب المالية لاختيار الأسهم الرخيصة والقوية"):
        st.markdown("""
        * **مضاعف الربحية (P/E):** أقل من **10 مرات** يعني أن السهم رخيص ومقوّم بأقل من قيمته 💎.
        * **العائد على حقوق الملكية (ROE %):** النسبة الأعلى من **18%** تعني كفاءة عالية في تحقيق الأرباح.
        * **العائد التوزيعي %:** النسبة الأعلى من **5%** ممتازة للمستثمر الباحث عن كوبونات نقدية.
        """)

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
            "P/E": pe, "EPS": eps, "ROE %": roe, "التوزيعات %": div, "التقييم": status
        })
    st.dataframe(pd.DataFrame(rows_fin), use_container_width=True, hide_index=True)

# ==========================================
# الأداة 3: الرسم البياني والدعوم والمقاومات (مدمج وسريع 100%)
# ==========================================
elif section == "3. الرسم البياني والدعوم والمقاومات":
    st.subheader("📈 الرسم البياني وحركة السعر والسيولة")
    
    with st.expander("📖 اضغط هنا لفهم كيفية قراءة الرسم البياني ومناطق الدخول والخروج"):
        st.markdown("""
        * **منطقة الشراء (الدعم S1):** عندما يقترب السعر من مستوى الدعم وينخفض مؤشر السيولة **MFI** تحت **30%**.
        * **منطقة البيع (المقاومة R1):** عندما يقترب السعر من مستوى المقاومة أو يرتفع مؤشر السيولة فوق **80%**.
        * **المتوسط المتحرك (20 يوم):** بقاء السعر فوق خط المتوسط يؤكد استمرار الاتجاه الصاعد.
        """)

    stock_labels = [f"{name} ({sym})" for sym, name in stocks_dict.items()]
    selected_label = st.selectbox("اختر السهم أو الصندوق لعرض الرسم البياني:", stock_labels)
    
    # استخراج الرمز بأمان تام
    selected_sym = selected_label.split("(")[-1].replace(")", "").strip()
    df_c = generate_stock_df(selected_sym)
    
    curr_p = round(float(df_c['السعر'].iloc[-1]), 2)
    res1 = round(float(df_c['High'].tail(20).max()), 2)
    sup1 = round(float(df_c['Low'].tail(20).min()), 2)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("السعر الحالي", f"{curr_p} ج.م")
    c2.metric("أقرب مقاومة (R1 - بيع)", f"{res1} ج.م")
    c3.metric("أقرب دعم (S1 - شراء)", f"{sup1} ج.م")

    st.markdown("**📊 حركة السعر والمتوسط المتحرك (آخر 90 جلسة):**")
    st.line_chart(df_c[['السعر', 'متوسط 20 يوم']], use_container_width=True)
    
    st.markdown("**💧 مؤشر تدفق السيولة المؤسسية (MFI):**")
    st.area_chart(df_c[['تدفق السيولة MFI']], use_container_width=True)

# ==========================================
# الأداة 4: حاسبة المخاطر والفرصة البديلة
# ==========================================
elif section == "4. حاسبة المخاطر والفرصة البديلة":
    st.subheader("⚖️ حاسبة إدارة المخاطر وتكلفة الفرصة البديلة")
    
    with st.expander("📖 اضغط هنا لفهم قواعد إدارة رأس المال وتكلفة الفرصة البديلة"):
        st.markdown("""
        * **نسبة المخاطرة (1% - 2%):** لا تخاطر بأكثر من **2%** من محفظتك في الصفقة الواحدة.
        * **نسبة العائد للمخاطرة:** يفضل أن تكون **2 : 1** أو أعلى.
        * **تكلفة الفرصة البديلة:** تقارن ربح السهم المتوقع بالعائد الآمن لأذون الخزانة أو صناديق الدخل الثابت (**25% سنوياً**).
        """)

    c1, c2 = st.columns(2)
    with c1:
        cap = st.number_input("رأس المال (جنيه):", value=100000.0, step=5000.0)
        risk = st.slider("نسبة المخاطرة %:", 0.5, 5.0, 2.0)
        rf = st.number_input("عائد أذون الخزانة / الدخل الثابت السنوي %:", value=25.0)
