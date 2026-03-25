import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Dashboard ✨", layout="wide")

# Tema Warna Pink Soft
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=2)
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
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        bln = st.selectbox("📅 Pilih Bulan", df['bulan'].unique())

    df_b = df[df['bulan'] == bln].copy()
    
    st.title(f"Recruitment Report: {bln} 🌸")
    st.divider()

    # --- BAGIAN RANKING ---
    st.subheader("Monthly Champions 👑")
    df_r = df_b.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index()
    df_r = df_r.sort_values('nilai', ascending=False)
    
    cols = st.columns(3)
    meds = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
    def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    for i in range(min(3, len(df_r))):
        u = df_r.iloc[i]
        with cols[i]:
            # Ambil link foto dari sheets
            pic = str(u['foto']).strip() if pd.notna(u['foto']) else def_img
            # Jika isinya bukan link internet, pakai placeholder
            if not pic.startswith('http'): pic = def_img
            
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size:16px">{meds[i]}</div>
                    <img src="{pic}" class="rank-img">
                    <div style="font-weight:bold; margin-top:10px">{u['nama']}</div>
                    <div style="color:#ff7eb9; font-weight:bold; font-size:22px">★ {u['nilai']:.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # --- TABEL RINGKASAN ---
    st.divider()
    st.subheader("📋 Summary Performa")
    piv = df_b.pivot_table(index='nama', columns='kpi', values='realisasi', aggfunc='sum').fillna(0)
    st.dataframe(piv, use_container_width=True)

    if st.button("Celebrate! 🥳"):
        st.balloons()
else:
    st.error("Data tidak ditemukan. Pastikan link Google Sheets sudah benar.")
