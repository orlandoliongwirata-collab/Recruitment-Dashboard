import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Annual Recruitment Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
        margin-bottom: 20px; min-height: 220px;
    }
    .rank-img { border-radius: 50%; width: 85px; height: 85px; object-fit: cover; border: 3px solid #ffb7ce; margin-bottom: 8px; }
    .avg-banner {
        background: linear-gradient(90deg, #ffdee9 0%, #b5fffc 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data (Ditingkatkan untuk deteksi BULAN)
@st.cache_data(ttl=1) # Cache hanya bertahan 1 detik agar data selalu baru
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Membaca data
        df = pd.read_csv(url, skiprows=2)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Pastikan kolom BULAN bersih dari spasi
        if 'BULAN' in df.columns:
            df['BULAN'] = df['BULAN'].ffill().str.strip()
        
        # Forward Fill untuk kolom identitas lainnya
        cols_to_fill = ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris yang tidak perlu (Header berulang, Total, atau baris kosong)
        if 'KPI' in df.columns:
            df = df.dropna(subset=['KPI'])
            df = df[~df['NAMA'].str.contains('NAMA', case=False, na=False)].copy()
            df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)].copy()
        
        # Konversi Achievement ke angka
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0

        if 'ACH' in df.columns:
            df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        else:
            df['ACH_VAL'] = 0.0
            
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

# --- LOGIKA TAMPILAN ---
if not df.empty:
    with st.sidebar:
        st.title("Navigation 🧭")
        
        # FITUR: PILIH BULAN (Wajib Muncul)
        if 'BULAN' in df.columns:
            list_bulan = sorted(df['BULAN'].unique(), key=lambda x: ['JANUARI', 'FEBRUARI', 'MARET', 'APRIL', 'MEI', 'JUNI', 'JULI', 'AGUSTUS', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DESEMBER'].index(x.upper()) if x.upper() in ['JANUARI', 'FEBRUARI', 'MARET', 'APRIL', 'MEI', 'JUNI', 'JULI', 'AGUSTUS', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DESEMBER'] else 0)
            sel_bulan = st.selectbox("📅 Pilih Bulan:", list_bulan)
            df_filtered = df[df['BULAN'] == sel_bulan].copy()
        else:
            st.warning("Kolom 'BULAN' tidak terdeteksi di Sheet.")
            df_filtered = df.copy()
            sel_bulan = "Januari"

        st.divider()
        view = st.radio("Pilih Mode:", ["🌍 Team Leaderboard", "👤 Personal Detail"])

    if view == "🌍 Team Leaderboard":
        st.title(f"🏆 Leaderboard - {sel_bulan}")
        
        # Statistik Tim
        avg_team = df_filtered['ACH_VAL'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Rata-rata Performance Tim</h3><h1>{avg_team:.1f}%</h1></div>', unsafe_allow_html=True)
        
        # Perhitungan Ranking
        df_rank = df_filtered.groupby('NAMA').agg({'ACH_VAL': 'mean', 'FOTO': 'first'}).reset_index()
        df_rank = df_rank.sort_values('ACH_VAL', ascending=False).reset_index(drop=True)
        
        # Tampilan Grid
        cols = st.columns(5)
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i, row in df_rank.iterrows():
            with cols[i % 5]:
                medali = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                pic = row['FOTO']
                if 'drive.google.com' in str(pic):
                    f_id = pic.split('file/d/')[1].split('/')[0]
                    pic = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                img_src = pic if pd.notna(pic) and str(pic).startswith('http') else def_img
                
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:18px;">{medali}</div>
                        <img src="{img_src}" class="rank-img" onerror="this.src='{def_img}'">
                        <div style="font-weight:bold; font-size:13px; line-height:1.2; height:32px; overflow:hidden;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-weight:bold; font-size:18px; margin-top:5px;">{row['ACH_VAL']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)

    else:
        # Personal Detail
        st.title(f"👤 Performance Detail - {sel_bulan}")
        pilih_pic = st.selectbox("Pilih Nama PIC:", df_filtered['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == pilih_pic]
        
        if not df_pic.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Avg. Achievement", f"{df_pic['ACH_VAL'].mean():.1f}%")
                pic_url = df_pic['FOTO'].iloc[0]
                if 'drive.google.com' in str(pic_url):
                    f_id = pic_url.split('file/d/')[1].split('/')[0]
                    pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"
                st.image(pic_url if pd.notna(pic_url) and str(pic_url).startswith('http') else "https://via.placeholder.com/150", use_container_width=True)
            
            with c2:
                fig = px.bar(df_pic, x='KPI', y='ACH_VAL', text_auto='.1f', color='ACH_VAL', color_continuous_scale='PuRd')
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.table(df_pic[['KPI', 'TARGET', 'REAL', 'ACH']])
else:
    st.info("Menghubungkan ke Google Sheets... Pastikan kolom 'BULAN' sudah terisi di setiap baris.")
