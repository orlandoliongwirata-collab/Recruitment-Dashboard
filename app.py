import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema
st.set_page_config(page_title="Recruitment Executive Dashboard ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
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

try:
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        st.divider()
        list_nama = ["Semua Nama"] + list(df['nama'].unique())
        pilih_nama = st.selectbox("👤 Filter Nama Spesifik", list_nama)

    # Data Processing
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)
    
    # Hitung % Achievement Otomatis
    df_bulan['% ach'] = (df_bulan['realisasi'] / df_bulan['target'] * 100).fillna(0)

    # Filter data jika nama dipilih
    df_view = df_bulan.copy()
    if pilih_nama != "Semua Nama":
        df_view = df_view[df_view['nama'] == pilih_nama]

    st.title(f"Recruitment Squad Dashboard: {pilih_bulan} 🌸")

    # --- TOP RANKING ---
    if pilih_nama == "Semua Nama":
        st.subheader("Monthly Champions 👑")
        df_rank = df_bulan.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index().sort_values(by='nilai', ascending=False)
        cols_rank = st.columns(3)
        medals = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
        for i in range(min(3, len(df_rank))):
            user = df_rank.iloc[i]
            with cols_rank[i]:
                img = user['foto'] if pd.notna(user['foto']) and str(user['foto']).startswith('http') else "https://via.placeholder.com/150"
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size: 20px;">{medals[i]}</div>
                        <img src="{img}" class="rank-img">
                        <div style="font-weight:bold;">{user['nama']}</div>
                        <div style="color:#ff7eb9; font-weight:bold;">★ {user['nilai']:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.divider()

    # --- TAMPILAN TABS ---
    tab1, tab2 = st.tabs(["📊 Visual Analysis", "📋 Summary Table (Ringkas)"])

    with tab1:
        st.subheader("KPI Performance Chart")
        # Hilangkan baris 'total' agar grafik tidak rusak
        df_chart = df_view[~df_view['kpi'].str.contains('total', case=False, na=False)]
        fig = px.bar(df_chart, 
                     x='kpi' if pilih_nama != "Semua Nama" else 'nama', 
                     y=['target', 'realisasi'],
                     color='kpi' if pilih_nama == "Semua Nama" else None,
                     barmode='group', 
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     template="plotly_white", text_auto='.2s')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("📋 Ringkasan Performa Per Personel")
        st.markdown("Satu baris untuk satu orang. Angka menunjukkan **% Achievement**.")

        # PROSES PIVOT: Mengubah Baris Berulang jadi Kolom Menyamping
        # Kita ambil nilai '% ach' untuk isi tabelnya
        df_pivot = df_view.pivot_table(
            index='nama', 
            columns='kpi', 
            values='% ach', 
            aggfunc='mean'
        ).fillna(0)

        # Tambahkan Rata-rata Skor Nilai di paling kanan
        df_nilai = df_view.groupby('nama')['nilai'].mean()
        df_pivot['SKOR AKHIR ⭐'] = df_nilai

        # Styling Warna Otomatis
        def color_ach(val):
            if isinstance(val, (int, float)):
                if val >= 100: return 'background-color: #d1f2eb; color: #145a32' # Hijau (Capai)
                if val >= 80: return 'background-color: #fef9e7; color: #7d6608'  # Kuning (Hampir)
            return ''

        st.dataframe(
            df_pivot.style.format("{:.1f}%", subset=df_pivot.columns[:-1])
            .format("{:.2f}", subset=['SKOR AKHIR ⭐'])
            .applymap(color_ach, subset=df_pivot.columns[:-1])
            .set_properties(**{'font-weight': 'bold'}, subset=['SKOR AKHIR ⭐']),
            use_container_width=True, height=400
        )

    if st.button("Celebration! 🥳"):
        st.balloons()

except Exception as e:
    st.error(f"Oops! Ada kendala: {e}")
