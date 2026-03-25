import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Professional Recruitment Dashboard ✨", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    
    # --- AUTO-CORRECTION KOLOM ---
    # Membersihkan spasi dan menyamakan nama kolom agar tidak error
    data.columns = [c.strip().capitalize() for c in data.columns]
    rename_dict = {'Real': 'Realisasi', 'Ttf': 'Time to fill', 'Ach': '% ach'}
    data = data.rename(columns=rename_dict)
    
    return data.dropna(subset=[data.columns[0]])

try:
    df = load_data()
    
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        # Mengambil kolom Bulan (Kolom ke-1)
        col_bulan = df.columns[0]
        list_bulan = df[col_bulan].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan Laporan", list_bulan)
        
        st.divider()
        # Mengambil kolom KPI (Kolom ke-3)
        col_kpi = df.columns[2]
        list_kpi = df[col_kpi].unique()
        pilih_kpi = st.selectbox("📊 Pilih KPI untuk Grafik", list_kpi)

    # Filter Data
    df_bulan = df[df[col_bulan] == pilih_bulan].copy()
    
    # Pastikan angka bisa dihitung
    for col in ['Target', 'Realisasi', 'Nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = pd.to_numeric(df_bulan[col].astype(str).str.replace('%','').str.replace('Rp','').str.replace(',',''), errors='coerce').fillna(0)

    st.title(f"Recruitment Report: {pilih_bulan} 🌸")

    # --- ROW 1: METRICS ---
    c1, c2, c3 = st.columns(3)
    avg_score = df_bulan['Nilai'].mean() if 'Nilai' in df_bulan.columns else 0
    c1.metric("Avg. Team Score ⭐", f"{avg_score:.2f}")
    c2.metric("Total Data", f"{len(df_bulan)} Rows")
    c3.metric("Status", "🟢 Active")

    st.divider()

    # --- ROW 2: CHART ---
    st.subheader(f"Analysis: {pilih_kpi}")
    df_kpi_filtered = df_bulan[df_bulan[col_kpi] == pilih_kpi]
    
    fig = px.bar(df_kpi_filtered, x=df_bulan.columns[1], y=['Target', 'Realisasi'], 
                 barmode='group', color_discrete_map={'Target': '#ffdee9', 'Realisasi': '#ffb7ce'},
                 template="plotly_white", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- ROW 3: TABLE ---
    st.subheader("Detail Data")
    st.dataframe(df_bulan, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Koneksi Berhasil, tapi ada masalah struktur: {e}")
    st.info("Pastikan Baris 1 di Sheets adalah: Bulan, Nama, KPI, Target, Realisasi, Nilai")
