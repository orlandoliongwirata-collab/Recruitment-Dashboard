import streamlit as st
import pandas as pd

st.set_page_config(page_title="HR Executive Dashboard ✨", layout="wide")

# Gaya Visual
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

@st.cache_data(ttl=5)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid=0"
    try:
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower() for c in data.columns]
        return data.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

def clean(v):
    s = str(v).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

# --- MAIN LOGIC ---
df = load_data()

if not df.empty:
    # Cari Nama Kolom (Sistem Keyword)
    c_bln = next((c for c in df.columns if 'bulan' in c), df.columns[0])
    c_nam = next((c for c in df.columns if 'nama' in c), None)
    c_nil = next((c for c in df.columns if 'nilai' in c), None)
    c_fot = next((c for c in df.columns if 'foto' in c), None)
    c_kpi = next((c for c in df.columns if 'kpi' in c), None)

    with st.sidebar:
        st.title("Admin Panel ⚙️")
        bln = st.selectbox("📅 Pilih Bulan", df[c_bln].dropna().unique())

    df_b = df[df[c_bln] == bln].copy()
    for c in ['target', 'realisasi', 'nilai']:
        match = next((col for col in df_b.columns if c in col), None)
        if match: df_b[match] = df_b[match].apply(clean)

    st.title(f"Recruitment Report: {bln} 🌸")
    st.divider()

    # --- RANKING ---
    if c_nam and c_nil:
        st.subheader("Monthly Champions 👑")
        df_r = df_b.groupby(c_nam).agg({c_nil: 'mean', c_fot: 'first'}).reset_index().sort_values(c_nil, ascending=False)
        cols = st.columns(3)
        meds = ["🥇 Gold", "🥈 Silver", "🥉 Bronze"]
        placeholder = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i in range(min(3, len(df_r))):
            u = df_r.iloc[i]
            with cols[i]:
                pic = str(u[c_fot]) if pd.notna(u[c_fot]) and str(u[c_fot]).startswith('http') else placeholder
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:18px">{meds[i]}</div>
                        <img src="{pic}" class="rank-img" onerror="this.src='{placeholder}'">
                        <div style="font-weight:bold; margin-top:10px">{u[c_nam]}</div>
                        <div style="color:#ff7eb9; font-weight:bold; font-size:20px">★ {u[c_nil]:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)

    # --- TABEL SUMMARY ---
    if c_kpi and c_nam:
        st.divider()
        st.subheader("📋 Summary Performa (% Achievement)")
        c_tar = next((c for c in df_b.columns if 'target' in c), None)
        c_rea = next((c for c in df_b.columns if 'realisasi' in c), None)
        
        if c_tar and c_rea:
            df_b['% ach'] = (df_b[c_rea] / df_b[c_tar] * 100).fillna(0)
            piv = df_b.pivot_table(index=c_nam, columns=c_kpi, values='% ach', aggfunc='mean').fillna(0)
            piv['TOTAL SKOR ⭐'] = df_b.groupby(c_nam)[c_nil].mean()
            st.dataframe(piv.style.format("{:.1f}%", subset=piv.columns[:-1]).format("{:.2f}", subset=['TOTAL SKOR ⭐']).background_gradient(cmap='PuRd', subset=['TOTAL SKOR ⭐']), use_container_width=True)

    if st.button("Celebrate! 🥳"): st.balloons()
else:
    st.warning("Menunggu data... Pastikan akses Google Sheets sudah 'Anyone with link'.")
