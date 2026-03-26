import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema Aesthetic
st.set_page_config(page_title="Recruitment Deep-Dive Dashboard ✨", layout="wide")

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

# 2. Fungsi Load Data Spesifik Sheet2
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid_sheet2 = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid_sheet2}"
    
    try:
        # Baca mulai dari baris judul kolom (Header Kuning)
        df = pd.read_csv(url, skiprows=2)
        
        # Bersihkan nama kolom dari spasi dan ubah ke uppercase
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # --- TEKNIK FORWARD FILL (MENGATASI MERGED CELLS) ---
        # Mengisi baris kosong di bawah NAMA, NIK, FOTO dengan data di atasnya
        for col in ['NAMA', 'NIK', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris 'TOTAL' agar tidak merusak rata-rata
        df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        # Fungsi bersihkan angka
        def clean_num(x):
            s = str(x).replace('Rp', '').replace('%', '').replace(',', '').strip()
            try: return float(s)
            except: return 0
            
        # Bersihkan kolom angka
        if 'NILAI' in df.columns: df['NILAI'] = df['NILAI'].apply(clean_num)
        if 'REAL' in df.columns: df['REAL'] = df['REAL'].apply(clean_num)

        return df.dropna(subset=['KPI'])
    except Exception as e:
        st.error(f"Terjadi kendala teknis: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Navigation 🧭")
        view_mode = st.radio("Menu:", ["🌍 Overview Team", "👤 Detail Per PIC"])
        st.divider()
        st.info("GID Aktif: 1942814563")

    if view_mode == "🌍 Overview Team":
        st.title("🏆 Leaderboard Performa Rekrutmen")
        
        # Hitung Total Skor per Nama
        df_rank = df.groupby('NAMA')['NILAI'].sum().reset_index().sort_values('NILAI', ascending=False)
        
        cols = st.columns(len(df_rank))
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i in range(len(df_rank)):
            with cols[i]:
                u = df_rank.iloc[i]
                # Ambil foto pertama milik PIC tersebut
                pic_link = df[df['NAMA'] == u['NAMA']]['FOTO'].iloc[0]
                
                # Cek jika link adalah Google Drive, ubah jadi direct link
                if 'drive.google.com' in str(pic_link):
                    f_id = pic_link.split('file/d/')[1].split('/')[0]
                    pic_link = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                final_pic = pic_link if pd.notna(pic_link) and str(pic_link).startswith('http') else def_img

                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:30px">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</div>
                        <img src="{final_pic}" class="rank-img" onerror="this.src='{def_img}'">
                        <div class="highlight-name">{u['NAMA']}</div>
                        <div class="highlight-score">{u['NILAI']:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Skor per KPI")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='sum').fillna(0)
        st.dataframe(piv.style.background_gradient(cmap='PuRd'), use_container_width=True)

    else:
        st.title("👤 PIC Deep-Dive Analysis")
        target_pic = st.selectbox("Pilih PIC:", df['NAMA'].unique())
        df_pic = df[df['NAMA'] == target_pic]

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Total Skor", f"{df_pic['NILAI'].sum():.2f}")
            # Tampilkan Foto
            raw_foto = df_pic['FOTO'].iloc[0]
            if 'drive.google.com' in str(raw_foto):
                f_id = raw_foto.split('file/d/')[1].split('/')[0]
                st.image(f"https://drive.google.com/uc?export=view&id={f_id}", use_container_width=True)
            else:
                st.image(raw_foto if pd.notna(raw_foto) else "https://via.placeholder.com/150", use_container_width=True)
            
            st.write(f"**Jabatan:** {df_pic['NAMA JABATAN'].iloc[0]}")

        with c2:
            fig = px.bar(df_pic, x='KPI', y='NILAI', color='KPI', 
                         title=f"Distribusi Nilai KPI: {target_pic}",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📑 Analisis Service Level (SL) & Success Rate (SR)")
        
        # Filter KPI spesifik SL dan SR
        sl = df_pic[df_pic['KPI'].str.contains('SERVICE LEVEL', case=False, na=False)]
        sr = df_pic[df_pic['KPI'].str.contains('SUCCESS RATE', case=False, na=False)]

        cl, cr = st.columns(2)
        with cl:
            if not sl.empty:
                val = sl['REAL'].iloc[0]
                st.info(f"**Kecepatan (SL):** {val} Hari")
                st.write("Target: < 30 Hari")
        with cr:
            if not sr.empty:
                val = sr['REAL'].iloc[0]
                st.success(f"**Ketepatan (SR):** {val} Kandidat")
                st.write("Target: ≤ 3 Kandidat")

else:
    st.error("Data tidak ditemukan. Pastikan GID dan format kolom NAMA, KPI, NILAI sudah sesuai.")
