import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# إعدادات الصفحة
st.set_page_config(page_title="EGX Radar Pro 30 & 70", page_icon="🇪🇬", layout="wide")

st.title("🇪🇬 EGX Radar Pro - رادار البورصة المصرية الشامل")
st.caption("يشمل القائمة الكاملة لأسهم EGX 30 و EGX 70، الصناديق، التحليل الفني، وحاسبة المخاطر.")

# القائمة الكاملة لأسهم البورصة المصرية والصناديق
EGX_DATA = {
    "مؤشر EGX 30 (30 سهماً بالكامل)": {
        "COMI.CA": "البنك التجاري الدولي (CIB)",
        "TMGH.CA": "مجموعة طلعت مصطفى القابضة",
        "ETEL.CA": "المصرية للاتصالات",
        "EAST.CA": "الشرقية - إيسترن كومباني",
        "FWRY.CA": "فوري لتكنولوجيا البنوك",
        "EFIH.CA": "إي فاينانس للاستثمارات",
        "ABUK.CA": "أبو قير للأسمدة",
        "ADIB.CA": "مصرف أبوظبي الإسلامي",
        "HRHO.CA": "مجموعة إي إف جي القابضة (هيرميس)",
        "ORAS.CA": "أوراسكوم كونستراكشن",
        "CCAP.CA": "القلعة للاستشارات المالية",
        "EFID.CA": "إيديتا للصناعات الغذائية",
        "MFPC.CA": "مصر لإنتاج الأسمدة - موبكو",
        "ALCN.CA": "الإسكندرية لتداول الحاويات",
        "AMOC.CA": "الإسكندرية للزيوت المعدنية",
        "PHDC.CA": "بالم هيلز للتعمير",
        "EGAL.CA": "مصر للألومنيوم",
        "BTFH.CA": "بلتون القابضة",
        "ORHD.CA": "أوراسكوم للتنمية مصر",
        "GBCO.CA": "جي بي كورب",
        "SKPC.CA": "سيدي كرير للبتروكيماويات",
        "JUFO.CA": "جهينة للصناعات الغذائية",
        "CLHO.CA": "مستشفى كليوباترا",
        "HELI.CA": "مصر الجديدة للإسكان والتعمير",
        "ISPH.CA": "ابن سينا فارما",
        "MCQE.CA": "مصر للأسمنت - قنا",
        "EMFD.CA": "إعمار مصر للتنمية",
        "RMDA.CA": "العاشر من رمضان - راميدا",
        "RAYA.CA": "راية القابضة للاستثمارات المالية",
        "SWDY.CA": "السويدي إليكتريك"
    },
    "مؤشر EGX 70 EWI (أهم الأسهم النشطة)": {
        "HDBK.CA": "بنك التعمير والإسكان",
        "CIEB.CA": "بنك كريدي أجريكول مصر",
        "ORWE.CA": "النساجون الشرقيون للسجاد",
        "OCDI.CA": "السادس من أكتوبر للتنمية (سوديك)",
        "TAQA.CA": "طاقة عربية",
        "ACTF.CA": "أكت فاينانشال للاستشارات",
        "MASR.CA": "مدينة مصر للإسكان والتعمير",
        "ZMID.CA": "زهراء المعادي للاستثمار",
        "EGCH.CA": "الصناعات الكيماوية المصرية (كيما)",
        "PHAR.CA": "المصرية الدولية للصناعات الدوائية (ايبيكو)",
        "MTIE.CA": "ام.ام جروب للصناعة والتجارة",
        "MPRC.CA": "المصرية لمدينة الإنتاج الإعلامي",
        "POUL.CA": "القاهرة للدواجن",
        "ISMA.CA": "الإسماعيلية مصر للدواجن",
        "MPCO.CA": "المنصورة للدواجن",
        "ATQA.CA": "مصر الوطنية للصلب - عتاقة",
        "ISMQ.CA": "الحديد والصلب للمناجم والمحاجر",
        "ARCC.CA": "العربية للأسمنت",
        "SCEM.CA": "أسمنت سيناء",
        "MBSC.CA": "مصر بني سويف للأسمنت",
        "SVCE.CA": "أسمنت جنوب الوادي",
        "ASCM.CA": "أسيك للتعدين - اسكوم",
        "ELEC.CA": "الكابلات الكهربائية المصرية",
        "ENGC.CA": "الصناعات الهندسية المعمارية (ايكون)",
        "LCSW.CA": "ليسيكو مصر",
        "DSCW.CA": "دايس للملابس الجاهزة",
        "KABO.CA": "النصر للملابس والمنسوجات (كابو)",
        "EGTS.CA": "المصرية للمنتجعات السياحية",
        "ELSH.CA": "الشمس للإسكان والتعمير",
        "UEGC.CA": "الصعيد العامة للمقاولات",
        "ARAB.CA": "المطورون العرب القابضة",
        "AMER.CA": "مجموعة عامر القابضة",
        "OIH.CA": "أوراسكوم للاستثمار القابضة",
        "OFH.CA": "أو بي المالية القابضة",
        "ATLC.CA": "التوفيق للتأجير التمويلي",
        "CNFN.CA": "كونتكت المالية القابضة",
        "CSAG.CA": "القناة للتوكيلات الملاحية",
        "ETRS.CA": "المصرية لخدمات النقل (ايجيترانس)",
        "MCRO.CA": "ماكرو جروب للمستحضرات الطبية",
        "SDTI.CA": "شارم دريمز للاستثمار السياحي"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF.CA": "صندوق مؤشر EGX 30 (وثائق مؤشرات)",
        "BTFH.CA": "بلتون القابضة (صناديق الذهب والدخل الثابت)",
        "HRHO.CA": "إي إف جي القابضة (صناديق الاستثمار)",
        "ACTF.CA": "أكت فاينانشال (صناديق واستثمار)"
    }
}

# القوائم العلوية للتنقل
col_top1, col_top2 = st.columns(2)
with col_top1:
    selected_index = st.selectbox("📌 1. اختر المؤشر أو الفئة:", list(EGX_DATA.keys()))
with col_top2:
    selected_section = st.selectbox(
        "🧭 2. اختر القسم المطلوب:",
        [
            "🎯 رادار التوصيات والتوقيتات (جميع الأسهم)",
            "📈 التحليل الفني والرسم البياني التفاعلي",
            "⚖️ حاسبة المخاطر وتكلفة الفرصة البديلة",
            "🏦 التحليل المالي ودليل صناديق الاستثمار"
        ]
    )

current_stocks = EGX_DATA[selected_index]
st.divider()

# دالة المؤشرات الفنية
def calc_indicators(df):
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
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Vol_Avg'] = df['Volume'].rolling(window=20).mean()
    df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()
    return df

# دالة التوصيات
def get_signal(last, prev, vol_ratio):
    score = 50
    reasons = []
    rsi_val = last['RSI'] if not pd.isna(last['RSI']) else 50
    
    if rsi_val < 30:
        score += 25; reasons.append("تشبع بيعي حاد")
    elif 30 <= rsi_val <= 45:
        score += 15; reasons.append("منطقة تجميع")
    elif rsi_val > 75:
        score -= 25; reasons.append("تشبع شرائي مرتفع")
    elif 65 < rsi_val <= 75:
        score -= 10; reasons.append("اقتراب من القمة")

    if last['Close'] > last['SMA_20']:
        score += 15; reasons.append("فوق متوسط 20")
    else:
        score -= 10; reasons.append("تحت متوسط 20")

    if last['MACD'] > last['Signal'] and prev['MACD'] <= prev['Signal']:
        score += 20; reasons.append("تقاطع MACD إيجابي")

    if vol_ratio > 1.3 and last['Close'] > prev['Close']:
        score += 10; reasons.append("سيولة عالية")

    score = max(0, min(100, score))
    if score >= 75: action = "شراء قوي 🟢"
    elif score >= 60: action = "تجميع / شراء 🔵"
    elif score >= 45: action = "انتظار ⚪"
    elif score >= 30: action = "جني أرباح 🟠"
    else: action = "بيع / تجنب 🔴"
    return score, action, (" + ".join(reasons) if reasons else "حركة عرضية")

# دالة جلب آمنة مع بديل تلقائي في حال حظر السيرفر من Yahoo Finance
@st.cache_data(ttl=1800)
def fetch_safe_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="4mo", interval="1d")
        if not df.empty and len(df) >= 20:
            return df, "بيانات حية 🟢"
    except Exception:
        pass
        
    # في حال حظر السيرفر السحابي من المصدر، توليد بيانات مرجعية متوافقة لعدم توقف الواجهة
    np.random.seed(abs(hash(symbol)) % (2**32))
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90, freq='B')
    base_price = np.random.uniform(12.0, 95.0)
    returns = np.random.normal(0.001, 0.022, size=len(dates))
    closes = base_price * np.exp(np.cumsum(returns))
    df_sim = pd.DataFrame({
        'Open': closes * np.random.uniform(0.98, 1.01, size=len(dates)),
        'High': closes * np.random.uniform(1.01, 1.04, size=len(dates)),
        'Low': closes * np.random.uniform(0.96, 0.99, size=len(dates)),
        'Close': closes,
        'Volume': np.random.randint(500000, 8000000, size=len(dates))
    }, index=dates)
    return df_sim, "وضع المحاكاة (السيرفر محظور من المصدر) 🟡"

@st.cache_data(ttl=1800)
def build_market_table(symbols_tuple, names_tuple):
    rows = []
    status_used = "بيانات حية 🟢"
    for sym, name in zip(symbols_tuple, names_tuple):
        df, status = fetch_safe_stock_data(sym)
        if "المحاكاة" in status:
            status_used = status
        df = calc_indicators(df.copy())
        last, prev = df.iloc[-1], df.iloc[-2]
        chg = ((float(last['Close']) - float(prev['Close'])) / float(prev['Close'])) * 100
        v_ratio = float(last['Volume']) / float(last['Vol_Avg']) if float(last['Vol_Avg']) > 0 else 1.0
        score, action, note = get_signal(last, prev, v_ratio)
        atr_val = float(last['ATR']) if not pd.isna(last['ATR']) else float(last['Close']) * 0.03
        rsi_val = float(last['RSI']) if not pd.isna(last['RSI']) else 50.0
        
        rows.append({
            "الرمز": sym.replace(".CA", ""),
            "اسم الورقة المالية": name,
            "السعر": round(float(last['Close']), 2),
            "التغير %": round(chg, 2),
            "التقييم (100)": int(score),
            "التوصية والقرار": action,
            "سبب التوقيت": note,
            "وقف خسارة": round(float(last['Close'] - 1.5 * atr_val), 2),
            "هدف بيع": round(float(last['Close'] + 3.0 * atr_val), 2),
            "RSI": round(rsi_val, 1)
        })
    return pd.DataFrame(rows), status_used

# ==============================================================================
# القسم 1: رادار التوصيات والتوقيتات
# ==============================================================================
if selected_section == "🎯 رادار التوصيات والتوقيتات (جميع الأسهم)":
    st.subheader(f"📡 مسح شامل: {selected_index}")
    
    with st.spinner("جاري تجهيز جدول الأسهم والتوصيات..."):
        df_res, data_status = build_market_table(tuple(current_stocks.keys()), tuple(current_stocks.values()))
        
    st.caption(f"حالة الاتصال بالبيانات: **{data_status}**")
    
    if not df_res.empty:
        df_res = df_res.sort_values(by="التقييم (100)", ascending=False).reset_index(drop=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("العدد الإجمالي المعروض", f"{len(df_res)} ورقة مالية")
