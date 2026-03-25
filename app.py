import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman & Tema
st.set_page_config(page_title="Recruitment Squad Executive Report ✨", layout="wide")

# Custom CSS untuk gaya Executive (Clean & Professional)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 Ranking */
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
        margin-bottom: 10px;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce;
    }
    .highlight-name { font-size: 18px; font-weight: bold; color: #4a4a4a; margin-top: 10px; }
    .highlight-score { color: #ff7eb9; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data
@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    # Standarisasi kolom: kecilkan semua & hapus spasi
    data.columns = [str(c).strip().lower() for c in data.columns]
    return data.dropna(subset=[data.columns[0]])

def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- MAIN APP ---
try:
    df = load_data()
    
    # Sidebar Filter
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        st.divider()
        st.info("Dashboard ini menampilkan ringkasan performa tim berdasarkan pencapaian KPI bulanan.")

    # Data Processing
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)
    
    # Hitung % Achievement Otomatis
    df_bulan['% ach'] = (df_bulan['realisasi'] / df_bulan['target'] * 100).fillna(0)

    st.title(f"Recruitment Monthly Performance: {pilih_bulan} 🌸")
    st.markdown("---")

    # --- SECTION 1: TOP 3 RANKING (HALL OF FAME) ---
    st.subheader("Monthly Champions 👑")
    df_rank = df_bulan.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index().sort_values(by='nilai', ascending=False)
    
    cols_rank = st.columns(3)
    medals = ["🥇 Gold Performer", "🥈 Silver Performer", "🥉 Bronze Performer"]
    
    for i in range(min(3, len(df_rank))):
        user = df_rank.iloc[i]
        with cols_rank[i]:
            img = user['foto'] if pd.notna(user['foto']) and str(user['foto']).startswith('http') else "https://via.placeholder.com/150"
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 18px; margin-bottom:10px;">{medals[i]}</div>
                    <img src="{img}" class="rank-img">
                    <div class="highlight-name">{user['nama']}</div>
                    <div class="highlight-total">Score: <span class="highlight-score">{user['nilai']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- SECTION 2: EXECUTIVE SUMMARY TABLE (PIVOT) ---
    st.subheader("📋 Summary Performa Tim (% Achievement)")
    st.markdown("Tabel di bawah merangkum persentase pencapaian setiap personel untuk seluruh kategori KPI.")

    # PROSES PIVOT: Mengubah data memanjang menjadi menyamping (Satu nama = satu baris)
    df_pivot = df_bulan.pivot_table(
        index='nama', 
        columns='kpi', 
        values='% ach', 
        aggfunc='mean'
    ).fillna(0)

    # Tambahkan Rata-rata Skor Nilai di paling kanan
    df_nilai = df_bulan.groupby('nama')['nilai'].mean()
    df_pivot['RATA-RATA SKOR ⭐'] = df_nilai

    # Fungsi Pewarnaan Sel (Heatmap)
    def color_ach(val):
        if isinstance(val, (int, float)):
            if val >= 100: return 'background-color: #d1f2eb; color: #145a32' # Hijau (Capai Target)
            if val >= 80: return 'background-color: #fef9e7; color: #7d6608'  # Kuning (Hampir Capai)
            if val > 0 and val < 80: return 'background-color: #fce4ec; color: #880e4f' # Merah Muda (Di bawah target)
        return ''

    # Tampilkan Tabel
    st.dataframe(
        df_pivot.style.format("{:.1f}%", subset=df_pivot.columns[:-1])
        .format("{:.2f}", subset=['RATA-RATA SKOR ⭐'])
        .applymap(color_ach, subset=df_pivot.columns[:-1])
        .set_properties(**{'font-weight': 'bold'}, subset=['RATA-RATA SKOR ⭐']),
        use_container_width=True
    )

    # --- SECTION 3: DETAIL DATA RAW ---
    with st.expander("🔍 Lihat Detail Data Mentah (Target vs Realisasi)"):
        df_raw = df_bulan[['nama', 'kpi', 'target', 'realisasi', 'nilai']].copy()
        df_raw.columns = ['Nama', 'Kategori KPI', 'Target', 'Realisasi (Real)', 'Skor']
        st.dataframe(df_raw, use_container_width=True, hide_index=True)

    if st.button("Celebrate Team Wins! 🥳"):
        st.balloons()

except Exception as e:
    st.error(f"Terjadi kesalahan teknis dalam memuat tabel: {e}")
    st.info("Saran: Pastikan format Google Sheets Anda tetap konsisten dengan kolom: Bulan, Nama, KPI, Target, Realisasi, Nilai, Foto.")
