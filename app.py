import streamlit as st
import pandas as pd

# 1. Setup Halaman
st.set_page_config(page_title="HR Executive Dashboard ✨", layout="wide")

# CSS untuk Dashboard Professional
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data
@st.cache_data(ttl=5)
def load_data():
    # ID MILIK ANDA
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        data = pd.read_csv(url)
        # Penting: Menghapus spasi di awal/akhir nama kolom dan kecilkan huruf
        data.columns = [str(c).strip().lower() for c in data.columns]
        # Hapus baris yang benar-benar kosong
        return data.dropna(how='all').reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame()

def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- MAIN APP ---
df = load_data()

if not df.empty:
    try:
        # Menentukan nama kolom secara fleksibel (antisipasi typo di Sheets)
        col_bulan = next((c for c in df.columns if 'bulan' in c), df.columns[0])
        col_nama = next((c for c in df.columns if 'nama' in c), None)
        col_nilai = next((c for c in df.columns if 'nilai' in c), None)
        col_foto = next((c for c in df.columns if 'foto' in c), None)
        col_kpi = next((c for c in df.columns if 'kpi' in c), None)

        # Sidebar Filter
        with st.sidebar:
            st.title("Admin Panel ⚙️")
            list_bulan = df[col_bulan].dropna().unique()
