import streamlit as st
import pandas as pd

# 1. Setup Halaman & Tema Aesthetic
st.set_page_config(page_title="HR Recruitment Dashboard ✨", layout="wide")

# CSS untuk Dashboard Professional
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 Champions */
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce; margin-bottom: 15px;
    }
    .highlight-name { font-weight: bold; font-size: 18px; color: #4a4a4a; margin-bottom: 5px; }
    .highlight-score { color: #ff7eb9; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data (Sangat Stabil)
@st.cache_data(ttl=5)
def load_data():
    # ID Sheet Anda (Jangan diganti)
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    try:
        data = pd.read_csv(url)
        # Bersihkan spasi tak terlihat di nama kolom
        data.columns = [str(c).strip() for c in data.columns]
        return data.dropna(subset=[data.columns[0]]).reset_index(drop=True)
    except Exception as e:
        return pd.DataFrame() # Kembalikan DataFrame kosong jika error

# --- MAIN APP ---
try:
    df = load_data()
    
    if df.empty:
        st.error("Gagal terhubung ke Google Sheets. Pastikan ID benar dan akses 'Anyone with link'.")
        st.stop()

    # Sidebar untuk Admin
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['Bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        st.divider()
        st.info("💡 Tips GDrive: Gunakan format link `drive.google.com/uc?export=view&id=ID_FILE` agar foto muncul.")

    # Filter Data berdasarkan bulan
    df_bulan = df[df['Bulan'] == pilih_bulan].copy()

    st.title(f"Recruitment Performance: {pilih_bulan} 🌸")
    st.markdown("---")

    # --- FITUR UTAMA: MONTHLY CHAMPIONS ---
    st.subheader("Monthly Champions 👑")
    
    # Agregasi skor dan foto
    df_rank = df_bulan.groupby('Nama').agg({
        'Nilai': 'mean',
        'Foto': 'first' 
    }).reset_index()
    
    # Ambil Top 3 tertinggi
    df_top3 = df_rank.sort_values(by='Nilai', ascending=False).head(3).reset_index(drop=True)

    cols_top = st.columns(3)
    medals = ["🥇 Gold Performer", "🥈 Silver Performer", "🥉 Bronze Performer"]
    
    # Foto placeholder jika link di GDrive kosong/salah (Lebih Aman)
    default_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    for i in range(len(df_top3)):
        rank_data = df_top3.iloc[i]
        
        # Validasi link foto, pastikan diawali 'http' agar tidak error
        img_url = rank_data['Foto'] if pd.notna(rank_data['Foto']) and str(rank_data['Foto']).startswith('http') else default_img
        
        with cols_top[i]:
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 18px; margin-bottom: 10px;">{medals[i]}</div>
                    <img src="{img_url}" class="rank-img" onerror="this.src='{default_img}'">
                    <div class="highlight-name">{rank_data['Nama']}</div>
                    <div>Skor: <span class="highlight-score">{rank_data['Nilai']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- ROW 2: DETAIL DATA ALL KPI (VERSI TABEL RINGKAS) ---
    st.subheader("📋 Ringkasan Performa Tim")
    
    # Menghapus baris 'Total' agar bersih
    df_display = df_bulan[df_bulan['KPI'] != 'Total'].copy()
    
    # Hitung % Achievement Otomatis jika perlu (opsional)
    
    st.dataframe(
        df_display[['Nama', 'KPI', 'Target', 'Realisasi', 'Nilai']],
        use_container_width=True,
        hide_index=True
    )

    if st.button("Celebrate Team Achievement! 🥳"):
        st.balloons()

except Exception as e:
    st.warning("Menyiapkan dashboard... Mohon Refresh halaman.")
    st.error(f"Detail kendala: {e}")
