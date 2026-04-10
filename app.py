import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Annual Recruitment Dashboard", layout="wide")

st.markdown("""
    <style>
    .rank-card {
        background: white; border-radius: 20px; padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
        margin-bottom: 20px; min-height: 200px;
    }
    .rank-img { border-radius: 50%; width: 80px; height: 80px; object-fit: cover; border: 3px solid #ffb7ce; margin-bottom: 8px; }
    .avg-banner {
        background: linear-gradient(90deg, #ffdee9 0%, #b5fffc 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data (Kalibrasi Baris ke-5)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # skiprows=3 artinya kita ambil Baris 4 Excel sebagai Header, 
        # sehingga data otomatis mulai dari Baris 5 Excel.
        df_raw = pd.read_csv(url, skiprows=3)
        
        # Bersihkan nama kolom agar kita bisa akses lewat angka indeks (0, 1, 2...)
        df_raw.columns = range(df_raw.shape[1])
        
        # --- PEMETAAN KOLOM BERDASARKAN GAMBAR ---
        # Kolom B (Indeks 0) = BULAN
        # Kolom C (Indeks 1) = NIK
        # Kolom D (Indeks 2) = NAMA
        # Kolom G (Indeks 5) = NO
        # Kolom H (Indeks 6) = KPI
        
        # Forward Fill untuk Nama yang di-merge
        df_raw[2] = df_raw[2].ffill() # Nama PIC
        df_raw[0] = df_raw[0].ffill() # Bulan (Jika ada)

        # Pemetaan Blok Bulanan (Sesuai Gambar: Loncat 5 Kolom)
        # Januari (Mulai kolom J/Indeks 8), Februari (Kolom O/Indeks 13), dst.
        month_config = {
            'Januari':  {'target': 9,  'real': 10, 'ach': 11},
            'Februari': {'target': 14, 'real': 15, 'ach': 16},
            'Maret':    {'target': 19, 'real': 20, 'ach': 21},
            'April':    {'target': 24, 'real': 25, 'ach': 26},
            'Mei':      {'target': 29, 'real': 30, 'ach': 31},
            'Juni':     {'target': 34, 'real': 35, 'ach': 36}
        }

        all_data = []
        for month, cols in month_config.items():
            if cols['ach'] < df_raw.shape[1]:
                # Ambil Nama (2), KPI (6), Target, Real, Ach
                temp = df_raw[[2, 6, cols['target'], cols['real'], cols['ach']]].copy()
                temp.columns = ['NAMA', 'KPI', 'TARGET', 'REAL', 'ACH']
                temp['BULAN_DATA'] = month
                all_data.append(temp)
        
        if not all_data: return pd.DataFrame()
        
        df = pd.concat(all_data, ignore_index=True)
        
        # Bersihkan baris yang bukan KPI (seperti baris kosong atau Total)
        df = df.dropna(subset=['KPI'])
        df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)]
        
        # Bersihkan angka Achievement
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0
            
        df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        return df
    except Exception as e:
        st.error(f"Error pembacaan Baris 5: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Admin Panel 🧭")
        list_bulan = df['BULAN_DATA'].unique()
        sel_bulan = st.selectbox("📅 Pilih Bulan:", list_bulan)
        df_filtered = df[df['BULAN_DATA'] == sel_bulan].copy()
        
        st.divider()
        view = st.radio("Tampilan:", ["🌍 Overview Tim", "👤 Detail PIC"])

    if view == "🌍 Overview Tim":
        st.title(f"🏆 Leaderboard - {sel_bulan}")
        avg_score = df_filtered['ACH_VAL'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Average Team Achievement</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
        df_rank = df_filtered.groupby('NAMA').agg({'ACH_VAL': 'mean'}).reset_index().sort_values('ACH_VAL', ascending=False).reset_index(drop=True)
        
        cols = st.columns(min(len(df_rank), 5))
        for i, row in df_rank.iterrows():
            with cols[i % 5]:
                medali = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:20px;">{medali}</div>
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="rank-img">
                        <div style="font-weight:bold; font-size:13px; min-height:40px;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-weight:bold; font-size:18px;">{row['ACH_VAL']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Skor per KPI")
        piv = df_filtered.pivot_table(index='NAMA', columns='KPI', values='ACH_VAL', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)

    else:
        st.title(f"👤 Deep-Dive PIC - {sel_bulan}")
        target = st.selectbox("Pilih PIC:", df_filtered['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == target]
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Avg Achievement", f"{df_pic['ACH_VAL'].mean():.1f}%")
            st.image("https://via.placeholder.com/150")
        with c2:
            fig = px.bar(df_pic, x='KPI', y='ACH_VAL', text_auto='.1f', color_continuous_scale='PuRd')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader(f"📑 Tabel Rincian: {target}")
        df_tabel = df_pic[['KPI', 'TARGET', 'REAL', 'ACH']].copy()
        df_tabel.index = range(1, len(df_tabel) + 1)
        st.table(df_tabel)
else:
    st.info("Menghubungkan ke data Baris 5...")
