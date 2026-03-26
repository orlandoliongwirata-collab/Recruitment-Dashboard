import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Recruitment Dashboard", layout="wide")

# CSS untuk tampilan rapi
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data (GID Sheet2: 1942814563)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Melompati 2 baris awal subjudul
        df = pd.read_csv(url, skiprows=2)
        
        # Bersihkan nama kolom
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # FORWARD FILL untuk menangani merged cells (NAMA, NIK, FOTO)
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Buang baris TOTAL dan baris tanpa KPI
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
        return pd.DataFrame() # Jika gagal, kirim data kosong

# --- PROSES UTAMA ---
df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Menu 🧭")
        view = st.radio("Pilih Tampilan:", ["🌍 Overview Team (%)", "👤 Detail PIC (%)"])

    # ---------------------------
    # MODE 1: OVERVIEW TEAM
    # ---------------------------
    if view == "🌍 Overview Team (%)":
        st.title("🏆 Leaderboard Pencapaian KPI (%)")
        
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
                        <div style="font-size:22px;">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</div>
                        <img src="{img_src}" class="rank-img" onerror="this.src='{def_img}'">
                        <div style="font-weight:bold;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-size:20px; font-weight:bold;">{row['NILAI']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Nilai per Komponen KPI (%)")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)

    # ---------------------------
    # MODE 2: DETAIL PIC (DIPERBAIKI)
    # ---------------------------
    else:
        st.title("👤 PIC Deep-Dive Analysis (%)")
        
        # Ambil daftar nama yang tersedia
        list_nama = df['NAMA'].unique()
        target = st.selectbox("Pilih PIC untuk Melihat Detail:", list_nama)
        
        # Filter data berdasarkan nama yang dipilih
        df_pic = df[df['NAMA'] == target]

        if not df_pic.empty:
            c1, c2 = st.columns([1, 2])
            
            with c1:
                # Foto
                pic_url = df_pic['FOTO'].iloc[0]
                if 'drive.google.com' in str(pic_url):
                    f_id = pic_url.split('file/d/')[1].split('/')[0]
                    pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                st.image(pic_url if pd.notna(pic_url) and str(pic_url).startswith('http') else "https://via.placeholder.com/150", use_container_width=True)
                
                # Info
                st.metric("Rata-rata Pencapaian", f"{df_pic['NILAI'].mean():.1f}%")
                st.write(f"**Nama:** {target}")
                st.write(f"**Jabatan:** {df_pic['NAMA JABATAN'].iloc[0]}")

            with c2:
                # Grafik
                fig = px.bar(df_pic, x='KPI', y='NILAI', text_auto='.1f',
                             title=f"Skor KPI: {target}",
                             color='NILAI', color_continuous_scale='PuRd')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("📑 Tabel Rincian Data")
            # Tabel detail (putih bersih)
            st.table(df_pic[['KPI', 'TARGET', 'REAL', 'NILAI']].rename(columns={'NILAI': 'NILAI (%)'}))
        else:
            st.warning("Data untuk PIC ini tidak ditemukan.")

else:
    st.info("Menghubungkan ke Google Sheets... Pastikan header (NIK, NAMA, dll) ada di baris 3 Sheet2.")
