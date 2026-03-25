import streamlit as st
import pandas as pd

# 1. Setup Halaman & Tema Aesthetic
st.set_page_config(page_title="Recruitment Hall of Fame ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Ambil Data
@st.cache_data(ttl=5)
def load_data():
    # ID MILIK ANDA (Jangan diganti)
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        data = pd.read_csv(url)
        # --- AUTO-CORRECTION KOLOM ---
        # Menghapus spasi tak terlihat di awal/akhir nama kolom dan kecilkan huruf
        data.columns = [str(c).strip().lower() for c in data.columns]
        
        # Mapping nama kolom agar Python tidak bingung
        rename_dict = {
            'real': 'realisasi', # Antisipasi jika di sheets tertulis 'Real'
            'ttf': 'time to fill'
        }
        data = data.rename(columns=rename_dict)
        
        return data.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

# Fungsi bersihkan angka murni
def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- MAIN APP ---
df = load_data()

if not df.empty:
    try:
        # Menentukan nama kolom secara fleksibel
        col_bulan = next((c for c in df.columns if 'bulan' in c), df.columns[0])
        col_nama = next((c for c in df.columns if 'nama' in c), None)
        col_nilai = next((c for c in df.columns if 'nilai' in c), None)
        col_foto = next((c for c in df.columns if 'foto' in c), None)
        col_kpi = next((c for c in df.columns if 'kpi' in c), None)

        # Sidebar Filter
        with st.sidebar:
            st.title("Admin Panel ⚙️")
            list_bulan = df[col_bulan].dropna().unique()
            pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)

        # Filter & Cleaning
        df_bulan = df[df[col_bulan] == pilih_bulan].copy()
        
        # Bersihkan angka untuk kolom penting
        if col_nilai: df_bulan[col_nilai] = df_bulan[col_nilai].apply(clean_val)
        
        target_col = next((c for c in df_bulan.columns if 'target' in c), None)
        real_col = next((c for c in df_bulan.columns if 'realisasi' in c), None)
        if target_col: df_bulan[target_col] = df_bulan[target_col].apply(clean_val)
        if real_col: df_bulan[real_col] = df_bulan[real_col].apply(clean_val)
        
        st.title(f"Recruitment Champions: {pilih_bulan} 🏆")
        st.divider()

        # --- RANKING FOTO ---
        if col_nama and col_nilai:
            st.subheader("Our
