import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Recruitment Squad Dashboard ✨", layout="wide")

# Gaya Visual
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
        st.title("Admin Panel ⚙️")
        list_bulan = df['bulan'].unique()
        pilih_bulan = st.selectbox("📅 Pilih Bulan", list_bulan)
        st.divider()
        list_nama = ["Semua Nama"] + list(df['nama'].unique())
        pilih_nama = st.selectbox("👤 Filter Nama Tim", list_nama)

    # Filter & Cleaning
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)
    
    df_bulan['% ach'] = (df_bulan['realisasi'] / df_bulan['target'] * 100).fillna(0)

    if pilih_nama != "Semua Nama":
        df_bulan = df_bulan[df_bulan['nama'] == pilih_nama]

    st.title(f"Recruitment Dashboard: {pilih_bulan} 🌸")

    # --- TOP RANKING ---
    if pilih_nama == "Semua Nama":
        st.subheader("Monthly Champions 👑")
        df_rank = df_bulan.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index().sort_values(by='nilai', ascending=False)
        cols = st.columns(3)
        medals = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
        for i in range(min(3, len(df_rank))):
            user = df_rank.iloc[i]
            with cols[i]:
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
    tab1, tab2 = st.tabs(["📊 Visual Analysis", "📋 Detailed Data"])

    with tab1:
        st.subheader("KPI Achievement Chart")
        # Filter agar bar 'Total' tidak mengganggu grafik jika ada
        df_chart = df_bulan[~df_bulan['kpi'].str.contains('total', case=False, na=False)]
        fig = px.bar(df_chart, x='kpi', y=['target', 'realisasi'], 
                     barmode='group', color_discrete_map={'target': '#ffdee9', 'realisasi': '#ffb7ce'},
                     template="plotly_white", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Master Table Detail")
        # Pastikan kolom yang dipanggil ada dan string ditutup dengan benar
        cols_to_show = ['nama', 'kpi', 'target', 'realisasi', '% ach', 'nilai']
        df_disp = df_bulan[cols_to_show].copy()
        df_disp.columns = ['Nama', 'Jenis KPI', 'Target', 'Realisasi', '% Achievement', 'Skor Nilai']
        
        st.dataframe(
            df_disp.style.format({
                'Target': '{:,.0f}', 
                'Realisasi': '{:,.0f}', 
                '% Achievement': '{:.1f}%', 
                'Skor Nilai': '{:.2f}'
            }).background_gradient(subset=['% Achievement'], cmap='PuRd'),
            use_container_width=True, 
            hide_index=True, 
            height=450
        )

    if st.button("Celebration! 🥳"):
        st.balloons()

except Exception as e:
    st.error(f"Terjadi kesalahan teknis: {e}")
