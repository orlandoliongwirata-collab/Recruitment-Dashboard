import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="HR Recruitment Dashboard % ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
    .highlight-score { color: #ff7eb9; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data Sheet2 (GID: 1942814563)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Melompati 2 baris sub-judul, baris ke-3 jadi Header
        df = pd.read_csv(url, skiprows=2, header=0)
        
        # Bersihkan Nama Kolom
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # --- TEKNIK FORWARD FILL ---
        # Menangani sel yang digabung (Merged Cells)
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris 'TOTAL' dan baris kosong
        df = df.dropna(subset=['KPI'])
        df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        # Fungsi membersihkan kolom NILAI agar menjadi angka murni
        def clean_percent(x):
            s = str(x).replace('%', '').replace(',', '.').strip()
            try: return float(s)
            except: return 0
            
        if 'NILAI' in df.columns:
            df['NILAI'] = df['NILAI'].apply(clean_percent)
            
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Navigation 🧭")
        view = st.radio("Pilih Tampilan:", ["🌍 Team Overview (%)", "👤 Detail PIC (%)"])

    if view == "🌍 Team Overview (%)":
        st.title("🏆 Leaderboard Pencapaian KPI (%)")
        
        # Hitung Rata-rata Nilai % per Nama
        df_rank = df.groupby('NAMA').agg({'NILAI': 'mean', 'FOTO': 'first'}).reset_index().sort_values('NILAI', ascending=False)
        
        cols = st.columns(len(df_rank))
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i, row in df_rank.iterrows():
            with cols[i]:
                # Logika Foto GDrive
                pic = row['FOTO']
                if 'drive.google.com' in str(pic):
                    f_id = pic.split('file/d/')[1].split('/')[0]
                    pic = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                img_src = pic if pd.notna(pic) and str(pic).startswith('http') else def_img
                
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:25px">{"🥇" if i==0 else "🥈" if i==1 else "🥉"}</div>
                        <img src="{img_src}" class="rank-img" onerror="this.src='{def_img}'">
                        <div style="font-weight:bold; margin-top:10px;">{row['NAMA']}</div>
                        <div class="highlight-score">{row['NILAI']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Nilai per Komponen KPI (%)")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.format("{:.1f}%").background_gradient(cmap='PuRd'), use_container_width=True)

    else:
        st.title("👤 PIC Deep-Dive Analysis (%)")
        target = st.selectbox("Pilih PIC:", df['NAMA'].unique())
        df_pic = df[df['NAMA'] == target]

        c1, c2 = st.columns([1, 2])
        with c1:
            # Info Profil & Rata-rata Skor
            st.metric("Rata-rata Pencapaian", f"{df_pic['NILAI'].mean():.1f}%")
            
            pic_url = df_pic['FOTO'].iloc[0]
            if 'drive.google.com' in str(pic_url):
                f_id = pic_url.split('file/d/')[1].split('/')[0]
                pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"
            
            st.image(pic_url if pd.notna(pic_url) else "https://via.placeholder.com/150", use_container_width=True)
            st.write(f"**NIK:** {df_pic['NIK'].iloc[0]}")
            st.write(f"**Jabatan:** {df_pic['NAMA JABATAN'].iloc[0]}")

        with c2:
            # Grafik Bar khusus kolom NILAI
            fig = px.bar(df_pic, x='KPI', y='NILAI', text_auto='.1f',
                         title=f"Detail Skor KPI: {target} (%)",
                         color='NILAI', color_continuous_scale='PuRd')
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📑 Rekapitulasi KPI")
        st.table(df_pic[['KPI', 'TARGET', 'REAL', 'NILAI']].rename(columns={'NILAI': 'NILAI (%)'}))

else:
    st.info("Menunggu data dari Sheet2. Pastikan Header (NIK, NAMA, KPI, dll) ada di Baris 3.")
