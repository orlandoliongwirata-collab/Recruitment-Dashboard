import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup Halaman & Tema
st.set_page_config(page_title="Recruitment Hall of Fame ✨", layout="wide")

# Custom CSS untuk Kartu Ranking Aesthetic (Glassmorphism + Pastel)
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 */
    .rank-card {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 20px;
    }
    .rank-img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 4px solid #ffb7ce;
        margin-bottom: 10px;
    }
    .rank-name { font-weight: bold; font-size: 18px; color: #4a4a4a; }
    .rank-score { color: #ff7eb9; font-size: 22px; font-weight: bold; }
    .crown { font-size: 40px; margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    
    # --- AUTO-CORRECTION KOLOM & LOWERCASE ---
    data.columns = [str(c).strip().lower() for c in data.columns]
    mapping = {
        'bulan': 'bulan', 'nama': 'nama', 'kpi': 'kpi',
        'target': 'target', 'realisasi': 'realisasi', 'real': 'realisasi',
        'nilai': 'nilai', 'foto': 'foto' # Tambahkan kolom Foto
    }
    data = data.rename(columns=mapping)
    return data.dropna(subset=[data.columns[0]])

def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try:
        return float(s)
    except:
        return 0

try:
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        st.divider()
        list_kpi = df['kpi'].unique()
        pilih_kpi = st.selectbox("📊 Pilih KPI untuk Grafik", list_kpi)

    # Filter & Cleaning
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)

    st.title(f"Recruitment Squad Report: {pilih_bulan} 🌸")
    st.markdown("#### *Celebrating our champions and tracking our growth!* ✨")

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    avg_score = df_bulan['nilai'].mean()
    c1.metric("Avg. Team Score ⭐", f"{avg_score:.2f}")
    c2.metric("Total Data", f"{len(df_bulan)} Rows")
    c3.metric("Status", "🟢 Active")

    st.divider()

    # --- FITUR BARU: HALL OF FAME (TOP 3 RANKING) ---
    st.subheader("Monthly Hall of Fame 👑")
    
    # Hitung rata-rata nilai per orang dan ambil link foto pertama
    df_rank = df_bulan.groupby('nama').agg({
        'nilai': 'mean',
        'foto': 'first' # Ambil link foto dari baris pertama
    }).reset_index()
    
    # Urutkan berdasarkan nilai tertinggi dan ambil Top 3
    df_top3 = df_rank.sort_values(by='nilai', ascending=False).head(3)

    # Menampilkan Foto dalam Kolom (Top 1, Top 2, Top 3)
    cols_top = st.columns(3)
    icons = ["👑", "🥈", "🥉"] # Ikon Ranking
    
    # Link foto default jika link di Excel mati/kosong
    default_img = "http://googleusercontent.com/google.com/search?q=profil_placeholder"

    # Perulangan untuk membuat Kartu Foto Top 3
    for i in range(len(df_top3)):
        rank_data = df_top3.iloc[i]
        # Jika link foto kosong, gunakan placeholder
        img_url = rank_data['foto'] if pd.notna(rank_data['foto']) else default_img
        
        with cols_top[i]:
            # HTML & CSS untuk Kartu
            st.markdown(f"""
                <div class="rank-card">
                    <div class="crown">{icons[i]}</div>
                    <img src="{img_url}" class="rank-img">
                    <div class="rank-name">{rank_data['nama']}</div>
                    <div class="rank-score">★ {rank_data['nilai']:.2f}</div>
                    <div style="color: #888; font-size: 12px;">Top {i+1} Performer</div>
                </div>
            """, unsafe_allow_html=True)

    if st.button("Celebrate Team Achievement! 🥳"):
        st.balloons()

    st.divider()

    # Chart Section (Masih sama)
    st.subheader(f"Analysis KPI: {pilih_kpi}")
    df_chart = df_bulan[df_bulan['kpi'] == pilih_kpi]
    if not df_chart.empty:
        fig = px.bar(df_chart, x='nama', y=['target', 'realisasi'], 
                     barmode='group', color_discrete_map={'target': '#ffdee9', 'realisasi': '#ffb7ce'},
                     template="plotly_white", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pilih KPI di sidebar untuk melihat grafik.")

    # Table Section (Hapus kolom Foto di tabel detail agar bersih)
    st.subheader("Detail Data")
    st.dataframe(df_bulan.drop(columns=['foto'], errors='ignore'), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Gagal memuat data. Periksa Google Sheets: Bulan, Nama, KPI, Target, Realisasi, Nilai, Foto. Error: {e}")
