import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
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
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data dengan Proteksi
@st.cache_data(ttl=5)
def load_data():
    # ID Spreadsheet Anda
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        data = pd.read_csv(url)
        # Bersihkan spasi di nama kolom dan kecilkan huruf
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(how='all').reset_index(drop=True)
    except Exception as e:
        st.error(f"Gagal memuat data dari Sheets: {e}")
        return pd.DataFrame()

def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- MAIN APP LOGIC ---
df_raw = load_data()

if not df_raw.empty:
    try:
        # Identifikasi kolom secara cerdas (mencari kata kunci)
        col_bulan = next((c for c in df_raw.columns if 'bulan' in c), df_raw.columns[0])
        col_nama = next((c for c in df_raw.columns if 'nama' in c), None)
        col_nilai = next((c for c in df_raw.columns if 'nilai' in c), None)
        col_foto = next((c for c in df_raw.columns if 'foto' in c), None)
        col_kpi = next((c for c in df_raw.columns if 'kpi' in c), None)

        # Sidebar
        with st.sidebar:
            st.title("Admin Panel ⚙️")
            list_bulan = df_raw[col_bulan].dropna().unique()
            pilih_bulan = st.selectbox("📅 Pilih Bulan", list_bulan)

        # Filter Data
        df_filtered = df_raw[df_raw[col_bulan] == pilih_bulan].copy()
        
        # Bersihkan angka untuk kolom penting
        for target_col in ['target', 'realisasi', 'nilai']:
            found_col = next((c for c in df_filtered.columns if target_col in c), None)
            if found_col:
                df_filtered[found_col] = df_filtered[found_col].apply(clean_val)

        st.title(f"Recruitment Report: {pilih_bulan} 🌸")
        st.divider()

        # --- SECTION RANKING FOTO ---
        if col_nama and col_nilai:
            st.subheader("Monthly Champions 👑")
            # Agregasi nilai rata-rata per orang
            df_rank = df_filtered.groupby(col_nama).agg({
                col_nilai: 'mean',
                col_foto: 'first' if col_foto else 'first'
            }).reset_index().sort_values(by=col_nilai, ascending=False)
            
            cols = st.columns(3)
            medals = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
            # Foto standar jika link tidak tersedia
            placeholder = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

            for i in range(min(3, len(df_rank))):
                user = df_rank.iloc[i]
                with cols[i]:
                    # Cek validitas link foto
                    img_link = str(user[col_foto]) if col_foto and pd.notna(user[col_foto]) else placeholder
                    if not img_link.startswith('http'): img_link = placeholder
                    
                    st.markdown(f"""
                        <div class="rank-card">
                            <div style="font-size: 18px;">{medals[i]}</div>
                            <img src="{img_link}" class="rank-img" onerror="this.src='{placeholder}'">
                            <div style="font-weight:bold; margin-top:10px;">{user[col_nama]}</div>
                            <div style="color:#ff7eb9; font-weight:bold; font-size:20px;">★ {user[col_nilai]:.2f}</div>
                        </div>
                    """, unsafe_allow_html=True)

        st.divider()

        # --- SECTION TABEL SUMMARY ---
        if col_kpi and col_nama:
            st.subheader("📋 Summary Performa (% Achievement)")
            
            col_target = next((c for c in df_filtered.columns if 'target' in c), None)
            col_real = next((
