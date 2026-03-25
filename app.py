import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup Halaman
st.set_page_config(page_title="Recruitment Performance Detail ✨", layout="wide")

# CSS Aesthetic
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce;
    }
    .stDataFrame { border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
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
        st.title("Admin Filter ⚙️")
        pilih_bulan = st.selectbox("📅 Pilih Bulan", df['bulan'].unique())
        st.divider()
        list_kpi = df['kpi'].unique()
        pilih_kpi = st.selectbox("📊 Analisis Grafik KPI", list_kpi)

    # Data Processing & Filtering
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)
    
    # Hitung % Achievement otomatis
    df_bulan['% ach'] = (df_bulan['realisasi'] / df_bulan['target'] * 100).fillna(0)

    st.title(f"Recruitment Squad Detail Report: {pilih_bulan} 🌸")

    # --- TOP 3 RANKING ---
    df_rank = df_bulan.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index().sort_values(by='nilai', ascending=False)
    
    cols = st.columns(3)
    medals = ["👑 Gold", "🥈 Silver", "🥉 Bronze"]
    for i in range(min(3, len(df_rank))):
        user = df_rank.iloc[i]
        with cols[i]:
            img = user['foto'] if pd.notna(user['foto']) else "https://via.placeholder.com/150"
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 25px;">{medals[i]}</div>
                    <img src="{img}" class="rank-img">
                    <div style="font-weight:bold; font-size:18px;">{user['nama']}</div>
                    <div style="color:#ff7eb9; font-size:20px; font-weight:bold;">★ {user['nilai']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- GRAFIK ANALISIS ---
    st.subheader(f"Grafik Perbandingan: {pilih_kpi}")
    df_chart = df_bulan[df_bulan['kpi'] == pilih_kpi]
    fig = px.bar(df_chart, x='nama', y=['target', 'realisasi'], barmode='group',
                 color_discrete_map={'target': '#ffdee9', 'realisasi': '#ffb7ce'},
                 template="plotly_white", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- TABEL DETAIL ALL KPI ---
    st.subheader("📋 Detail Seluruh KPI Anak Buah")
    st.markdown("Berikut adalah data
