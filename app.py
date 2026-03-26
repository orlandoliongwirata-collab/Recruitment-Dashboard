import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Recruitment Deep-Dive Dashboard ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee;
    }
    .rank-img { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 4px solid #ffb7ce; }
    .stMetric { background: #fdf6f9; padding: 15px; border-radius: 10px; border-left: 5px solid #ff7eb9; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(how='all')
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR & NAVIGATION ---
    with st.sidebar:
        st.title("Navigation 🧭")
        view_mode = st.radio("Pilih Tampilan:", ["🌍 Overview Keseluruhan", "👤 Detail Per PIC"])
        st.divider()
        bln_list = df['bulan'].unique()
        pilih_bln = st.selectbox("📅 Pilih Bulan", bln_list)

    df_b = df[df['bulan'] == pilih_bln].copy()

    # ==========================================
    # MODE 1: OVERVIEW KESELURUHAN
    # ==========================================
    if view_mode == "🌍 Overview Keseluruhan":
        st.title(f"Recruitment Overview: {pilih_bln} 🌸")
        
        # Ranking Top 3
        df_r = df_b.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index().sort_values('nilai', ascending=False)
        cols = st.columns(3)
        meds = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i in range(min(3, len(df_r))):
            u = df_r.iloc[i]
            with cols[i]:
                pic = str(u['foto']).strip() if pd.notna(u['foto']) and str(u['foto']).startswith('http') else def_img
                st.markdown(f'<div class="rank-card"><small>{meds[i]}</small><br><img src="{pic}" class="rank-img"><br><b>{u["nama"]}</b><br><span style="color:#ff7eb9; font-size:20px;">★ {u["nilai"]:.2f}</span></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Tabel Performa Seluruh Tim")
        piv = df_b.pivot_table(index='nama', columns='kpi', values='nilai', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.background_gradient(cmap='PuRd'), use_container_width=True)

    # ==========================================
    # MODE 2: DETAIL PER PIC (DRILL-DOWN)
    # ==========================================
    else:
        st.title("👤 PIC Deep-Dive Analysis")
        nama_pic = st.selectbox("Pilih Nama PIC untuk Melihat Detail:", df_b['nama'].unique())
        
        # Filter data khusus PIC yang dipilih
        df_pic = df_b[df_b['nama'] == nama_pic]
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Tampilkan Foto PIC
            pic_url = str(df_pic['foto'].iloc[0]) if pd.notna(df_pic['foto'].iloc[0]) else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            st.image(pic_url, caption=f"Profile {nama_pic}", use_container_width=True)
            st.metric("Rata-rata Skor", f"{df_pic['nilai'].mean():.2f}")

        with col2:
            st.subheader(f"Statistik Pencapaian: {nama_pic}")
            # Grafik Batang Pencapaian per KPI
            fig = px.bar(df_pic, x='kpi', y='nilai', color='kpi', 
                         title=f"Skor KPI {nama_pic}", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # Detail Analisis (Quality of Hire & Recruitment Process)
        st.subheader("📑 Analisis Detail & Proses")
        
        c1, c2, c3 = st.columns(3)
        
        # Contoh mengambil data spesifik (Pastikan di Sheets ada KPI 'Quality of Hire' dsb)
        qoh = df_pic[df_pic['kpi'].str.contains('Quality', case=False, na=False)]
        ttf = df_pic[df_pic['kpi'].str.contains('Time', case=False, na=False)]
        
        with c1:
            val_qoh = qoh['realisasi'].iloc[0] if not qoh.empty else 0
            st.metric("Quality of Hire", f"{val_qoh}%")
            st.caption("Target vs Realisasi kualitas kandidat.")

        with c2:
            # Simulasi data rekrut vs resign (Bisa diambil dari kolom lain di Sheets jika ada)
            st.metric("Total Rekrut", "12 Orang")
            st.write("✅ 10 Orang Lolos Probasi")

        with c3:
            st.metric("Total Resign (Early)", "2 Orang")
            st.write("⚠️ Turnover Rate: 16%")

        st.info(f"**💡 Catatan Performa:** {nama_pic} menunjukkan keunggulan pada KPI {df_pic.loc[df_pic['nilai'].idxmax(), 'kpi']}. Perlu perhatian pada proses onboarding untuk menekan angka resign dini.")

else:
    st.error("Gagal memuat data.")
