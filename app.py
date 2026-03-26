import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Annual Recruitment Dashboard", layout="wide")

# CSS Custom
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img { border-radius: 50%; width: 90px; height: 90px; object-fit: cover; border: 3px solid #ffb7ce; }
    .avg-banner {
        background: linear-gradient(90deg, #ffdee9 0%, #b5fffc 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data (Multi-Bulan)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Baca baris 2 secara terpisah untuk mengambil nama bulan (Jan'26, Feb'26, dst)
        raw_header = pd.read_csv(url, nrows=2, header=None)
        
        # Baca data utama mulai dari Baris 3
        df = pd.read_csv(url, skiprows=2)
        df.columns = [str(c).strip().upper() for c in df.columns]

        # Logika Deteksi Bulan Otomatis:
        # Jika tidak ada kolom BULAN, kita buat kolom dummy berdasarkan blok baris
        if 'BULAN' not in df.columns:
            # Sederhananya, kita asumsikan setiap 8 baris (termasuk TOTAL) adalah bulan baru
            # Atau kita bisa deteksi baris kosong sebagai pemisah
            df['BULAN'] = "Januari" # Default
            # Tips: Sangat disarankan tambah kolom BULAN di Sheet agar 100% akurat
        
        # Forward Fill untuk merged cells
        cols_to_fill = ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN', 'BULAN']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris TOTAL dan KPI kosong
        df = df.dropna(subset=['KPI'])
        df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)].copy()
        
        # Bersihkan ACH
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0

        if 'ACH' in df.columns:
            df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        else:
            df['ACH_VAL'] = pd.to_numeric(df['NILAI'], errors='coerce').fillna(0) * 100
            
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Admin Panel 🧭")
        # Pilih Bulan
        list_bulan = df['BULAN'].unique()
        sel_bulan = st.selectbox("📅 Pilih Bulan Laporan:", list_bulan)
        st.divider()
        view = st.radio("Tampilan:", ["🌍 Leaderboard Tim", "👤 Analisis Individu"])

    df_filtered = df[df['BULAN'] == sel_bulan]

    if view == "🌍 Leaderboard Tim":
        st.title(f"🏆 Performa Tim - {sel_bulan}")
        
        avg_score = df_filtered['ACH_VAL'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Rata-rata Achievement</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
        # Ranking
        df_rank = df_filtered.groupby('NAMA').agg({'ACH_VAL': 'mean', 'FOTO': 'first'}).reset_index().sort_values('ACH_VAL', ascending=False).reset_index(drop=True)
        
        cols = st.columns(min(len(df_rank), 5))
        for i, row in df_rank.iterrows():
            with cols[i % 5]:
                medali = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                pic = row['FOTO'] if str(row['FOTO']).startswith('http') else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                
                st.markdown(f"""
                    <div class="rank-card">
                        <small>{medali}</small><br>
                        <img src="{pic}" class="rank-img"><br>
                        <b style="font-size:14px;">{row['NAMA']}</b><br>
                        <span style="color:#ff7eb9; font-weight:bold;">{row['ACH_VAL']:.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)

    else:
        # Analisis Individu
        st.title(f"👤 Deep-Dive: {sel_bulan}")
        pilih_nama = st.selectbox("Pilih PIC:", df['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == pilih_nama]
        
        if not df_pic.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Achievement", f"{df_pic['ACH_VAL'].mean():.1f}%")
                st.image(df_pic['FOTO'].iloc[0] if pd.notna(df_pic['FOTO'].iloc[0]) else "https://via.placeholder.com/150")
            with c2:
                fig = px.bar(df_pic, x='KPI', y='ACH_VAL', text_auto='.1f', color='ACH_VAL', color_continuous_scale='PuRd')
                st.plotly_chart(fig, use_container_width=True)
            st.table(df_pic[['KPI', 'TARGET', 'REAL', 'ACH']])
else:
    st.info("Data belum terbaca sempurna. Disarankan menambah kolom 'BULAN' di setiap baris data.")
