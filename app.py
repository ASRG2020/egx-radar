import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعدادات الصفحة
st.set_page_config(page_title="EGX Radar Pro 30 & 70", page_icon="🇪🇬", layout="wide")

st.title("🇪🇬 EGX Radar Pro - رادار البورصة المصرية الشامل")
st.caption("يشمل القائمة الكاملة لأسهم EGX 30 و EGX 70، الصناديق، التحليل الفني، وحاسبة المخاطر.")

# القائمة الكاملة والمحدثة لأسهم البورصة المصرية
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
        "VLMR.CA": "فالمور القابضة للاستثمار",
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
        "RAYA.CA": "راية القابضة للاستثمارات المالية"
    },
    "مؤشر EGX 70 EWI (70 سهماً بالكامل)": {
        "SWDY.CA": "السويدي إليكتريك",
        "HDBK.CA": "بنك التعمير والإسكان",
        "CIEB.CA": "بنك كريدي أجريكول مصر",
        "ORWE.CA": "النساجون الشرقيون للسجاد",
        "OCDI.CA": "السادس من أكتوبر للتنمية (سوديك)",
        "TAQA.CA": "طاقة عربية",
        "VALU.CA": "فاليو للتمويل الاستهلاكي",
        "BONY.CA": "بنيان للتنمية والتجارة",
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
        "PRCL.CA": "العامة لمنتجات الخزف والصيني",
        "DSCW.CA": "دايس للملابس الجاهزة",
        "KABO.CA": "النصر للملابس والمنسوجات (كابو)",
        "EGTS.CA": "المصرية للمنتجعات السياحية",
        "ELSH.CA": "الشمس للإسكان والتعمير",
        "ELKA.CA": "القاهرة للإسكان والتعمير",
        "PRDC.CA": "بايونيرز بروبرتيز للتنمية العمرانية",
        "UEGC.CA": "الصعيد العامة للمقاولات",
        "DAPH.CA": "التعمير والاستشارات الهندسية",
        "ARAB.CA": "المطورون العرب القابضة",
        "AMER.CA": "مجموعة عامر القابضة",
        "OIH.CA": "أوراسكوم للاستثمار القابضة",
        "OFH.CA": "أو بي المالية القابضة",
        "ASPI.CA": "اسباير كابيتال القابضة",
        "AMIA.CA": "الملتقى العربي للاستثمارات",
        "AIHC.CA": "العربية للاستثمارات والتنمية",
        "AIDC.CA": "العربية للاستثمار والتنمية",
        "ATLC.CA": "التوفيق للتأجير التمويلي",
        "CNFN.CA": "كونتكت المالية القابضة",
        "CSAG.CA": "القناة للتوكيلات الملاحية",
        "ETRS.CA": "المصرية لخدمات النقل (ايجيترانس)",
        "ICFC.CA": "الدولية للأسمدة والكيماويات",
        "MPCI.CA": "ممفيس للأدوية والصناعات الكيماوية",
        "NIPH.CA": "النيل للأدوية والصناعات الكيماوية",
        "SIPC.CA": "سبأ الدولية للأدوية",
        "MCRO.CA": "ماكرو جروب للمستحضرات الطبية",
        "MEPA.CA": "العبوات الطبية",
        "ZEOT.CA": "الزيوت المستخلصة ومنتجاتها",
        "COSG.CA": "القاهرة للزيوت والصابون",
        "AIFI.CA": "اطلس للاستثمار والصناعات الغذائية",
        "GOUR.CA": "جورميه إيجيبت",
        "SDTI.CA": "شارم دريمز للاستثمار السياحي",
        "GDWA.CA": "جدوى للتنمية الصناعية",
        "GPIM.CA": "جي بي أي للنمو العمراني",
        "NCCW.CA": "النصر للأعمال المدنية",
        "IEEC.CA": "المشروعات الصناعية والهندسية",
        "MOED.CA": "المصرية لنظم التعليم الحديثة"
    },
    "صناديق الأسهم والمؤشرات والدخل الثابت": {
        "EGX30ETF.CA": "صندوق مؤشر EGX 30 (وثائق مؤشرات)",
        "BTFH.CA": "بلتون القابضة (صناديق الذهب والدخل الثابت)",
        "HRHO.CA": "إي إف جي القابضة (صناديق الاستثمار)",
        "ACTF.CA": "أكت فاينانشال (صناديق واستثمار)"
    }
}

# اختيار المؤشر والقسم في واجهة واحدة واضحة
col_top1, col_top2 = st.columns([1, 2])
with col_top1:
    selected_index = st.selectbox("📌 1. اختر المؤشر:", list(EGX_DATA.keys()))
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
    if last['RSI'] < 30:
        score += 25; reasons.append("تشبع بيعي حاد")
    elif 30 <= last['RSI'] <= 45:
        score += 15; reasons.append("منطقة تجميع")
    elif last['RSI'] > 75:
        score -= 25; reasons.append("تشبع شرائي مرتفع")
    elif 65 < last['RSI'] <= 75:
        score -= 10; reasons.append("اقتراب من القمة")

    if last['Close'] > last['SMA_20'] and last['SMA_20'] > last['SMA_50']:
        score += 15; reasons.append("اتجاه صاعد")
    elif last['Close'] < last['SMA_20'] and last['Close'] < last['SMA_50']:
        score -= 15; reasons.append("اتجاه هابط")

    if last['MACD'] > last['Signal'] and prev['MACD'] <= prev['Signal']:
        score += 20; reasons.append("تقاطع MACD إيجابي")
    elif last['MACD'] < last['Signal'] and prev['MACD'] >= prev['Signal']:
        score -= 20; reasons.append("تقاطع MACD سلبي")

    if vol_ratio > 1.4 and last['Close'] > prev['Close']:
        score += 10; reasons.append("سيولة عالية")

    score = max(0, min(100, score))
    if score >= 75: action = "شراء قوي 🟢"
    elif score >= 60: action = "تجميع / شراء 🔵"
    elif score >= 45: action = "انتظار ⚪"
    elif score >= 30: action = "جني أرباح 🟠"
    else: action = "بيع / تجنب 🔴"
    return score, action, (" + ".join(reasons) if reasons else "حركة عرضية")

# تحميل مجمع سريع جداً لجميع الأسهم
@st.cache_data(ttl=1800)
def fetch_all_market(symbols_tuple, names_tuple):
    symbols = list(symbols_tuple)
    names_map = dict(zip(symbols, names_tuple))
    rows = []
    try:
        data = yf.download(symbols, period="4mo", interval="1d", group_by="ticker", progress=False, threads=True)
    except Exception:
        return pd.DataFrame()

    for sym in symbols:
        try:
            df = data[sym].dropna(how='all') if len(symbols) > 1 else data.dropna(how='all')
            if df.empty or len(df) < 25:
                continue
            df = calc_indicators(df.copy())
            last, prev = df.iloc[-1], df.iloc[-2]
            chg = ((float(last['Close']) - float(prev['Close'])) / float(prev['Close'])) * 100
            v_ratio = float(last['Volume']) / float(last['Vol_Avg']) if float(last['Vol_Avg']) > 0 else 1.0
            score, action, note = get_signal(last, prev, v_ratio)
            rows.append({
                "الرمز": sym.replace(".CA", ""),
                "اسم الشركة": names_map[sym],
                "السعر": round(float(last['Close']), 2),
                "التغير %": round(chg, 2),
                "التقييم (100)": int(score),
                "القرار والتوصية": action,
                "سبب التوقيت": note,
                "وقف خسارة": round(float(last['Close'] - 1.5 * last['ATR']), 2),
                "هدف بيع": round(float(last['Close'] + 3.0 * last['ATR']), 2),
                "RSI": round(float(last['RSI']), 1)
            })
        except Exception:
            continue
    return pd.DataFrame(rows)

# ==============================================================================
# القسم 1: رادار التوصيات والتوقيتات
# ==============================================================================
if selected_section == "🎯 رادار التوصيات والتوقيتات (جميع الأسهم)":
    st.subheader(f"📡 مسح شامل: {selected_index}")
    if st.button("🔄 تحديث الأسعار الآن"):
        st.cache_data.clear()
        
