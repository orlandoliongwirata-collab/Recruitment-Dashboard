import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Gaya
st.set_page_config(page_title="Recruitment Dashboard %", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce; margin-bottom: 10px;
    }
    .highlight-name { font-weight: bold; font-size: 16px; color: #4a4a4a; }
    .highlight-score { color: #ff7eb9; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data (GID: 1942814563)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Lompat 2 baris awal, baris 3 jadi judul kolom (Header Kuning)
        df = pd.read_csv(url, skiprows=2)
        
        # Bersihkan nama kolom
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # --- FORWARD FILL (MENGISI MERGED CELLS) ---
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Buang baris TOTAL dan baris kosong di kolom KPI
        if 'KPI' in df.columns:
            df = df.dropna(subset=['KPI'])
            df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        # Fungsi bersihkan angka persen
        def clean_percent(x):
            s = str(x).replace('%', '').replace(',', '.').strip()
            try:
                return float(s)
            except:
                return 0.0

        if 'NILAI' in df.columns:
            df['NILAI'] = df['NILAI'].apply(clean_percent)
            
        return df
    except Exception as e:
        st.error(f"Kendala: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Menu 🧭")
        view = st.radio("Pilih Tampilan:", ["🌍 Overview Team (%)", "👤 Detail PIC (%)"])

    if view == "🌍 Overview Team (%)":
        st.title("🏆 Leaderboard Pencapaian KPI (%)")
        
        # Rata-rata Nilai per Nama
        df_rank = df.groupby('NAMA').agg({'NILAI': 'mean', 'FOTO': 'first'}).reset_index().sort_values('NILAI', ascending=False)
        
        cols = st.columns(len(df_rank))
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i, row in df_rank.iterrows():
            with cols[i]:
                pic = row['FOTO']
                if 'drive.google.com' in str(pic):
                    f_id = pic.split('file/d/')[1].split('/')[0]
                    pic = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                img_src = pic if pd.notna(pic) and str(pic).startswith('http') else def_img
                
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:25px; margin-bottom:10px;">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</div>
                        <img src="{img_src}" class="rank-img" onerror="this.src='{def_img}'">
                        <div class="highlight-name">{row['NAMA']}</div>
                        <div class="highlight-score">{row['NILAI']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Nilai per Komponen KPI (%)")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='mean').fillna(0)
        
        # Tampilan Tabel Putih Bersih (Tanpa Warna Gelap)
        st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)

    else:
        st.title("👤 PIC Deep-Dive Analysis (%)")
        target = st.selectbox("Pilih PIC:", df['NAMA'].unique())
        df_pic = df[df['NAMA'] == target]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Rata-rata Pencapaian", f"{df_pic['NILAI'].mean():.1f}%")
            
            pic_url = df_pic['FOTO'].iloc[0]
            if 'drive.google.com' in str(pic_url):
                f_id = pic_url.split('file/d/')[1].split('/')[0]
                pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"
            
            st.image(pic_url if pd.notna(pic_url) else "https://via.placeholder.com/150", use_container_width=True)
            st
