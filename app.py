import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Executive Dashboard ✨", layout="wide")

# Gaya Visual Professional
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
    </style>
    """, unsafe_allow_html=True)

def fix_gdrive_link(link):
    """Fungsi otomatis mengubah link GDrive biasa menjadi Direct Link"""
    if 'drive.google.com' in str(link) and 'file/d/' in str(link):
        file_id = link.split('file/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return link

@st.cache_data(ttl=5)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(how='all')
    except:
        return pd.DataFrame()

def clean(v):
    s = str(v).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Admin Panel ⚙️")
        bln = st.selectbox("📅 Pilih Bulan", df['bulan'].unique())

    df_b = df[df['bulan'] == bln].copy()
    
    for k in ['target', 'realisasi', 'nilai']:
        if k in df_b.columns: df_b[k] = df_b[k].apply(clean)

    st.title(f"Recruitment Performance: {bln} 🌸")
    st.divider()

    # --- TOP PERFORMERS ---
    st.subheader("Monthly Champions 👑")
    df_r = df_b.groupby('nama').agg({'nilai': 'mean', 'foto': 'first'}).reset_index()
    df_r = df_r.sort_values('nilai', ascending=False)
    
    cols = st.columns(3)
    meds = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
    def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    for i in range(min(3, len(df_r))):
        u = df_r.iloc[i]
        with cols[i]:
            # Perbaiki link foto secara otomatis sebelum ditampilkan
            raw_pic = u['foto']
            pic = fix_gdrive_link(raw_pic) if pd.notna(raw_pic) else def_img
            
            val_skor = f"{u['nilai']:.2f}"
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size:16px">{meds[i]}</div>
                    <img src="{pic}" class="rank-img" onerror="this.src='{def_img}'">
                    <div style="font-weight:bold; margin-top:10px">{u['nama']}</div>
                    <div style="color:#ff7eb9; font-weight:bold; font-size:22px">★ {val_skor}</div>
                </div>
            """, unsafe_allow_html=True)

    # --- SUMMARY TABLE ---
    st.divider()
    st.subheader("📋 Summary Performa")
    df_b['% ach'] = (df_b['realisasi'] / df_b['target'] * 100).fillna(0)
    piv = df_b.pivot_table(index='nama', columns='kpi', values='% ach', aggfunc='mean').fillna(0)
    piv['TOTAL SKOR ⭐'] = df_b.groupby('nama')['nilai'].mean()
    
    st.dataframe(piv.style.format("{:.1f}%", subset=piv.columns[:-1])
                 .format("{:.2f}", subset=['TOTAL SKOR ⭐'])
                 .background_gradient(cmap='PuRd', subset=['TOTAL SKOR ⭐']), 
                 use_container_width=True)

    if st.button("Celebrate! 🥳"): st.balloons()
else:
    st.warning("Hubungkan ke Google Sheets...")
