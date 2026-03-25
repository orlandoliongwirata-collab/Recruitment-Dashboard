import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Professional Recruitment Dashboard ✨", layout="wide")

# CSS Custom untuk tampilan profesional namun tetap estetik
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    h1, h2, h3 { color: #4a4a4a; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    # ID Sheet Anda yang terbaru
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    return data.dropna(subset=[data.columns[0]])

try:
    df = load_data()
    
    # Sidebar untuk Filter
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        list_bulan = df['Bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        
        st.divider()
        list_kpi = df['KPI'].unique()
        pilih_kpi = st.selectbox("📊 Pilih KPI untuk Grafik", list_kpi)

    # Filter Data berdasarkan bulan
    df_bulan = df[df['Bulan'] == pilih_bulan].copy()
    
    # Hitung Persentase Achievement (Realisasi/Target)
    df_bulan['% Ach'] = (pd.to_numeric(df_bulan['Realisasi'], errors='coerce') / 
                         pd.to_numeric(df_bulan['Target'], errors='coerce') * 100).fillna(0)

    st.title(f"Recruitment Performance Report: {pilih_bulan} 🌸")

    # --- ROW 1: SUMMARY METRICS ---
    c1, c2, c3, c4 = st.columns(4)
    avg_score = pd.to_numeric(df_bulan['Nilai'], errors='coerce').mean()
    total_hired_kpi = df_bulan[df_bulan['KPI'].str.contains('Fulfillment', case=False)]['Realisasi'].sum()
    
    c1.metric("Avg. Team Score ⭐", f"{avg_score:.2f}")
    c2.metric("Avg. Achievement %", f"{df_bulan['% Ach'].mean():.1f}%")
    c3.metric("Team Members", f"{len(df_bulan['Nama'].unique())}")
    c4.metric("Status", "🟢 On Track")

    st.divider()

    # --- ROW 2: GRAFIK PERFORMANCE ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"Target vs Realisasi: {pilih_kpi}")
        df_kpi_filtered = df_bulan[df_bulan['KPI'] == pilih_kpi]
        fig_bar = px.bar(df_kpi_filtered, x='Nama', y=['Target', 'Realisasi'], 
                         barmode='group',
                         color_discrete_map={'Target': '#ffdee9', 'Realisasi': '#ffb7ce'},
                         template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("Distribusi Nilai Akhir ⭐")
        # Menghitung rata-rata nilai per orang di bulan tersebut
        df_nilai_avg = df_bulan.groupby('Nama')['Nilai'].mean().reset_index()
        fig_line = px.line(df_nilai_avg, x='Nama', y='Nilai', markers=True,
                           color_discrete_sequence=['#ff7eb9'], template="plotly_white")
        fig_line.update_layout(yaxis_range=[0, 5]) # Asumsi skala nilai 1-5
        st.plotly_chart(fig_line, use_container_width=True)

    # --- ROW 3: TABEL DETAIL ---
    st.subheader("Data Detail Seluruh KPI")
    st.dataframe(df_bulan[['Nama', 'KPI', 'Target', 'Realisasi', '% Ach', 'Nilai']], 
                 use_container_width=True, hide_index=True)

    if st.button("Download Monthly Summary 📑"):
        st.success("Feature coming soon! (Data ready to be screenshotted for your Manager)")

except Exception as e:
    st.error("Gagal memuat data. Periksa apakah nama kolom di Sheets sudah tepat: Bulan, Nama, KPI, Target, Realisasi, Nilai.")
