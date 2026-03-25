import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
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

# 2. Fungsi Ambil Data (Menggunakan ID Anda)
@st.cache_data(ttl=5)
def load_data():
    # ID MILIK ANDA:
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        data = pd.read_csv(url)
        # Bersihkan spasi dan kecilkan huruf pada nama kolom
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(subset=[data.columns[0]])
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
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
        # Sidebar
        with st.sidebar:
            st.title("Admin Panel ⚙️")
            # Cek apakah kolom 'bulan' ada
            col_bulan = 'bulan' if 'bulan' in df.columns else df.columns[0]
            list_bulan = df[col_bulan].unique()
            pilih_bulan = st.selectbox("📅 Pilih Bulan", list_bulan)

        # Filter & Cleaning
        df_bulan = df[df[col_bulan] == pilih_bulan].copy()
        
        # Pastikan kolom-kolom utama dibersihkan angkanya
        for col in ['target', 'realisasi', 'nilai']:
            if col in df_bulan.columns:
                df_bulan[col] = df_bulan[col].apply(clean_val)
        
        # Hitung % Achievement
        if 'target' in df_bulan.columns and 'realisasi' in df_bulan.columns:
            df_bulan['% ach'] = (df_bulan['realisasi'] / df_bulan['target'] * 100).fillna(0)

        st.title(f"Recruitment Report: {pilih_bulan} 🌸")
        st.divider()

        # --- RANKING FOTO ---
        if 'nama' in df_bulan.columns and 'nilai' in df_bulan.columns:
            st.subheader("Monthly Champions 👑")
            df_rank = df_bulan.groupby('nama').agg({
                'nilai': 'mean',
                'foto': 'first' if 'foto' in df_bulan.columns else 'first'
            }).reset_index().sort_values(by='nilai', ascending=False)
            
            cols = st.columns(3)
            medals = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
            for i in range(min(3, len(df_rank))):
                user = df_rank.iloc[i]
                with cols[i]:
                    img = user['foto'] if 'foto' in user and pd.notna(user['foto']) and str(user['foto']).startswith('http') else "
