import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema Aesthetic
st.set_page_config(page_title="Recruitment Deep-Dive Dashboard ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 Champions */
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce; margin-bottom: 10px;
    }
    .highlight-name { font-weight: bold; font-size: 16px; color: #4a4a4a; margin-bottom: 5px; }
    .highlight-score { color: #ff7eb9; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data Spesifik Format Sheet2 + Kolom Foto
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    # GID Sheet2 terbaru Anda (Contoh, ganti sesuai gid Anda di URL)
    gid_sheet2 = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid_sheet2}"
    
    try:
        # Kita mulai baca dari baris ke-3 (skiprows=2 untuk sub-judul kuning)
        # Tambahkan parameter header=0 agar Python tahu baris setelah skip adalah header
        df = pd.read_csv(url, skiprows=2, header=0)
        
        # Bersihkan nama kolom
        df.columns = [str(c).strip().upper() for c in data.columns]
        
        # --- TEKNIK FORWARD FILL ---
        # Tarik data NAMA, NIK, dan FOTO yang digabung (merged cells) ke bawah
        cols_to_fill = ['NAMA', 'NIK', 'FOTO', 'NAMA JABATAN']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris 'TOTAL' agar tidak mengganggu perhitungan
        df = df[df['KPI'] != 'TOTAL'].copy()
        
        # Fungsi bersihkan angka
        def clean_num(x):
            s = str(x).replace('Rp', '').replace('%', '').replace(',', '').strip()
            try: return float(s)
            except: return 0
            
        # Bersihkan kolom angka penting
        df['NILAI'] = df['NILAI'].apply(clean_num)
        df['REAL'] = df['REAL'].apply(clean_num)
        df['TARGET'] = df['TARGET'].apply(clean_num)

        return df.dropna(subset=['KPI'])
    except Exception as e:
        st.error(f"Error memuat data: {e}")
        return pd.DataFrame()

# --- MAIN APP ---
df = load_data()

if not df.empty:
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation 🧭")
        view_mode = st.radio("Pilih Tampilan:", ["🌍 Overview Team", "👤 Detail Per PIC"])
        st.divider()
        st.info("💡 Data tersinkronisasi otomatis dengan Google Sheets.")

    if view_mode == "🌍 Overview Team":
        st.title("🏆 Leaderboard Recruitment Performance")
        
        # Ranking berdasarkan total nilai
        df_rank = df.groupby('NAMA')['NILAI'].sum().reset_index().sort_values('NILAI', ascending=False)
        
        cols = st.columns(len(df_rank))
        # Foto placeholder jika link di GDrive kosong
        default_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i in range(len(df_rank)):
            with cols[i]:
                u = df_rank.iloc[i]
                
                # Ambil foto pertama yang ditemukan untuk nama ini
                foto_raw = df[df['NAMA'] == u['NAMA']]['FOTO'].iloc[0]
                # Jika link dari GDrive masih format /view, ubah jadi uc?export=view
                if 'drive.google.com' in str(foto_raw):
                     f_id = foto_raw.split('file/d/')[1].split('/')[0]
                     foto_url = f"https://drive.google.com/uc?export=view&id={f_id}"
                else:
                    foto_url = default_img if pd.isna(foto_raw) else foto_raw

                # Tampilan Kartu Ranking
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:30px">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</div>
                        <img src="{foto_url}" class="rank-img">
                        <div class="highlight-name">{u['NAMA']}</div>
                        <div>Skor: <span class="highlight-score">{u['NILAI']:.2f}</span></div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Nilai per KPI")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='sum').fillna(0)
        st.dataframe(piv.style.background_gradient(cmap='PuRd'), use_container_width=True)

    else:
        st.title("👤 PIC Deep-Dive Analysis")
        target_nama = st.selectbox("Pilih PIC:", df['NAMA'].unique())
        df_pic = df[df['NAMA'] == target_nama]

        # Row 1: Profil & Radar Chart
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Total Skor Akhir", f"{df_pic['NILAI'].sum():.2f}")
            # Foto Detail
            pic_raw = df_pic['FOTO'].iloc[0]
            if 'drive.google.com' in str(pic_raw):
                 f_id = pic_raw.split('file/d/')[1].split('/')[0]
                 st.image(f"https://drive.google.com/uc?export=view&id={f_id}", use_container_width=True)
            else:
                 st.image(pic_raw if pd.notna(pic_raw) else "https://via.placeholder.com/150", use_container_width=True)

            st.write(f"**Jabatan:** {df_pic['NAMA JABATAN'].iloc[0]}")
        
        with c2:
            fig = px.polar_bar(df_pic, r='NILAI', theta='KPI', 
                               title=f"Radar Performa: {target_nama}", 
                               color_discrete_sequence=['#ff7eb9'])
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📑 Analisis Spesifik SL & SR")
        
        # Mencari data KPI yang mengandung kata 'Service Level' atau 'Success Rate'
        sl_data = df_pic[df_pic['KPI'].str.contains('SERVICE LEVEL', case=False, na=False)]
        sr_data = df_pic[df_pic['KPI'].str.contains('SUCCESS RATE', case=False, na=False)]

        col_sl, col_sr = st.columns(2)
        with col_sl:
            if not sl_data.empty:
                val = sl_data['REAL'].iloc[0]
                st.info(f"**Kecepatan (SL):** {val}")
                if "Hari" in str(sl_data['UOM'].iloc[0]):
                    st.write("Target Baik jika < 30 Hari")

        with col_sr:
            if not sr_data.empty:
                val = sr_data['REAL'].iloc[0]
                st.success(f"**Ketepatan (SR):** {val}")
                st.write("🎯 Target Baik jika ≤ 3 Kandidat")

else:
    st.error("Data gagal dimuat. Cek akses Google Sheets Anda.")
