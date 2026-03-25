import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman & Tampilan
st.set_page_config(page_title="HR Dashboard ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { 
        border-radius: 50%; width: 120px; height: 120px; 
        object-fit: cover; border: 4px solid #ffb7ce; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data (Otomatis Update setiap 1 detik)
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
    # Sidebar Sederhana
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        bln_list = df['bulan'].unique()
        pilih_bln = st.selectbox("📅 Pilih Bulan Laporan", bln_list)

    df_b = df[df['bulan'] == pilih_bln].copy()
    
    st.title(f"Recruitment Report: {pilih_bln} 🌸")
    st.divider()

    # --- BAGIAN RANKING ---
    st.subheader("Monthly Champions 👑")
    
    # Ambil nilai rata-rata dan link foto pertama untuk setiap nama
    df_r = df_b.groupby('nama').agg({
        'nilai': 'mean',
        'foto': 'first'
    }).reset_index().sort_values('nilai', ascending=False)
    
    cols = st.columns(3)
    meds = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
    def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    for i in range(min(3, len(df_r))):
        u = df_r.iloc[i]
        with cols[i]:
            # Pastikan link adalah Image Address (berakhiran .jpg/.png)
            pic_url = str(u['foto']).strip() if pd.notna(u['foto']) else def_img
            
            # Proteksi jika link Google Drive masih format /view
            if 'drive.google.com' in pic_url and 'file/d/' in pic_url:
                f_id = pic_url.split('file/d/')[1].split('/')[0]
                pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"

            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size:16px; font-weight:bold; color:#888;">{meds[i]}</div>
                    <img src="{pic_url}" class="rank-img" onerror="this.src='{def_img}'">
                    <div style="font-weight:bold; margin-top:10px; font-size:18px;">{u['nama']}</div>
                    <div style="color:#ff7eb9; font-weight:bold; font-size:22px;">★ {u['nilai']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # --- TABEL SUMMARY ---
    st.divider()
    st.subheader("📋 Summary Performa")
    piv = df_b.pivot_table(index='nama', columns='kpi', values='realisasi', aggfunc='sum').fillna(0)
    st.dataframe(piv, use_container_width=True)

    if st.button("Celebrate! 🥳"):
        st.balloons()
else:
    st.error("Gagal memuat data. Periksa koneksi Google Sheets.")
