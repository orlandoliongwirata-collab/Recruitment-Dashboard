import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup Halaman & Tema Aesthetic
st.set_page_config(page_title="HR Recruitment Dashboard ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 Champions */
    .rank-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%;
        width: 110px;
        height: 110px;
        object-fit: cover;
        border: 4px solid #ffb7ce;
        margin-bottom: 15px;
    }
    .highlight-name {
        font-weight: bold;
        font-size: 18px;
        color: #4a4a4a;
        margin-bottom: 5px;
    }
    .highlight-score {
        color: #ff7eb9;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data
@st.cache_data(ttl=5)
def load_data():
    # ID Sheet Anda (Jangan diganti)
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
    
    # Ambil Data
    data = pd.read_csv(url)
    
    # --- AUTO-CORRECTION KOLOM ---
    # Membersihkan spasi tak terlihat dan menyamakan nama kolom agar tidak error
    data.columns = [str(c).strip() for c in data.columns]
    
    return data.dropna(subset=[data.columns[0]]).reset_index(drop=True)

try:
    df = load_data()
    
    # Sidebar untuk Admin
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['Bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        
        st.divider()
        st.info("Pastikan link di kolom FOTO adalah link gambar langsung (Direct Link) berakhiran .jpg atau .png")

    # Filter Data berdasarkan bulan
    df_bulan = df[df['Bulan'] == pilih_bulan].copy()

    st.title(f"Recruitment Monthly Performance: {pilih_bulan} 🌸")
    st.markdown("---")

    # --- FITUR UTAMA: MONTHLY CHAMPIONS (DENGAN FOTO) ---
    st.subheader("Monthly Champions 👑")
    
    # Menghitung rata-rata skor per orang dan mengambil link foto pertama
    df_rank = df_bulan.groupby('Nama').agg({
        'Nilai': 'mean',
        'Foto': 'first' # Mengambil link foto pertama yang ditemukan
    }).reset_index()
    
    # Urutkan berdasarkan nilai tertinggi dan ambil Top 3
    df_top3 = df_rank.sort_values(by='Nilai', ascending=False).head(3).reset_index(drop=True)

    # Menampilkan Top 3 Visual (Gold, Silver, Bronze)
    cols_top = st.columns(3)
    medals = ["🥇 Gold Performer", "🥈 Silver Performer", "🥉 Bronze Performer"]
    
    # Link foto default jika link di Excel mati/kosong
    default_img = "http://googleusercontent.com/google.com/search?q=placeholder_png_profile"

    # Perulangan untuk membuat Kartu Foto Top 3
    for i in range(len(df_top3)):
        rank_data = df_top3.iloc[i]
        
        # Validasi link foto, jika kosong pakai default
        img_url = rank_data['Foto'] if pd.notna(rank_data['Foto']) and str(rank_data['Foto']).startswith('http') else default_img
        
        with cols_top[i]:
            # HTML & CSS untuk Kartu Champions
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 18px; margin-bottom: 10px;">{medals[i]}</div>
                    <img src="{img_url}" class="rank-img">
                    <div class="highlight-name">{rank_data['Nama']}</div>
                    <div>Skor: <span class="highlight-score">{rank_data['Nilai']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- ROW 2: DETAIL DATA ALL KPI ---
    st.subheader("📋 Detail Seluruh KPI Tim")
    
    # Menghapus baris 'Total' di tabel detail agar bersih
    df_display = df_bulan[df_bulan['KPI'] != 'Total'].copy()
    
    # Menghitung % Achievement Otomatis (Realisasi/Target)
    # Catatan: Perlu penyesuaian di Excel agar Target ditulis angka murni (cth: 90 bukan 90%)
    
    st.dataframe(
        df_display[['Nama', 'KPI', 'Target', 'Realisasi', 'Nilai']],
        use_container_width=True,
        hide_index=True
    )

    if st.button("Celebrate Team Achievement! 🥳"):
        st.balloons()

except Exception as e:
    st.warning("Menyiapkan dashboard... Mohon Refresh halaman.")
    st.error(f"Detail kendala teknis: {e}")
    st.info("Tips: Refresh Halaman > Clear Cache > Rerun. Jika masih error, periksa nama kolom di Baris 1 Sheets Anda.")
