import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Executive Dashboard ✨", layout="wide")

# Gaya Visual Pro
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

def clean(v):
    s = str(v).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- PROSES DATA ---
df = load_data()

if not df.empty:
    c_bln = next((c for c in df.columns if 'bulan' in c), df.columns[0])
    c_nam = next((c for c in df.columns if 'nama' in c), None)
    c_nil = next((c for c in df.columns if 'nilai' in c), None)
    c_fot = next((c for c in df.columns if 'foto' in c), None)
    c_kpi = next((c for c in df.columns if 'kpi' in c), None)

    with st.sidebar:
        st.title("Admin Panel ⚙️")
        bln_list = df[c_bln].dropna().unique()
        bln = st.selectbox("📅 Pilih Bulan", bln_list)

    # Filter data bulan yang dipilih
    df_b = df[df[c_bln] == bln].copy()
    
    for c in ['target', 'realisasi', 'nilai']:
        match = next((col for col in df_b.columns if c in col),
