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
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25 :px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Kita baca mulai dari baris ke-4 Excel (skip 3 baris) agar header terbaca benar
        df_raw = pd.read_csv(url, skiprows=3)
        df_raw.columns = range(df_raw.shape[1])
        
        # Identitas: NAMA (Kolom D/Indeks 2), KPI (Kolom H/Indeks 6), UOM (Kolom I/Indeks 7)
        df_raw[2] = df_raw[2].ffill() 

        # Konfigurasi Kolom Bulanan (Masing-masing bulan punya 5 kolom: Bobot, Target, Real, Ach, Nilai)
        # Januari mulai kolom J (Indeks 8)
        month_config = {
            'Januari':  {'bobot': 8, 'target': 9,  'real': 10, 'ach': 11, 'nilai': 12},
            'Februari': {'bobot': 13, 'target': 14, 'real': 15, 'ach': 16, 'nilai': 17},
            'Maret':    {'bobot': 18, 'target': 19, 'real': 20, 'ach': 21, 'nilai': 22},
            'April':    {'bobot': 23, 'target': 24, 'real': 25, 'ach': 26, 'nilai': 27}
        }

        all_data = []
        for month, cols in month_config.items():
            if cols['nilai'] < df_raw.shape[1]:
                # Ambil Nama, KPI, UOM, dan 5 kolom data bulanan
                temp = df_raw[[2, 6, 7, cols['bobot'], cols['target'], cols['real'], cols['ach'], cols['nilai']]].copy()
                temp.columns = ['NAMA', 'KPI', 'UOM', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']
                temp['BULAN_DATA'] = month
                all_data.append(temp)
        
        df = pd.concat(all_data, ignore_index=True)
        df = df.dropna(subset=['KPI'])
        df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)]
        
        # Logika pembersihan angka untuk kalkulasi (Ranking tetap pakai Ach %)
        def clean_to_num(x):
            try:
                s = str(x).replace('%', '').replace(',', '.').replace('-', '0').replace('Rp', '').strip()
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0
            
        df['ACH_NUM'] = df['ACH'].apply(clean_to_num)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Admin Panel 🧭")
        list_bulan = df['BULAN_DATA'].unique()
        sel_bulan = st.selectbox("📅 Pilih Bulan:", list_bulan)
        df_filtered = df[df['BULAN_DATA'] == sel_bulan].copy()
        view = st.radio("Tampilan:", ["🌍 Overview Tim", "👤 Detail PIC"])

    if view == "🌍 Overview Tim":
        st.title(f"🏆 Leaderboard - {sel_bulan}")
        avg_score = df_filtered['ACH_NUM'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Average Team Achievement</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
        # Leaderboard berdasarkan rata-rata Achievement
        df_rank = df_filtered.groupby('NAMA').agg({'ACH_NUM': 'mean'}).reset_index().sort_values('ACH_NUM', ascending=False).reset_index(drop=True)
        
        cols = st.columns(min(len(df_rank), 5))
        for i, row in df_rank.iterrows():
            with cols[i % 5]:
                medali = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:20px;">{medali}</div>
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="rank-img">
                        <div style="font-weight:bold; font-size:13px; min-height:40px;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-weight:bold; font-size:18px;">{row['ACH_NUM']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan per KPI (Adaptif Satuan)")
        
        # Formatter tampilan tabel ringkasan agar sesuai UOM
        def label_display(row):
            if row['UOM'] == '%': return f"{row['ACH_NUM']:.1f}%"
            if row['UOM'] == 'Jam': return f"{row['ACH_NUM']:.1f} Jam"
            return f"{row['ACH_NUM']:.0f}"

        df_filtered['DISPLAY'] = df_filtered.apply(label_display, axis=1)
        piv = df_filtered.pivot_table(index='NAMA', columns='KPI', values='DISPLAY', aggfunc='first').fillna("-")
        st.dataframe(piv, use_container_width=True)

    else:
        # --- PERSONAL DETAIL (RINCIAN LENGKAP) ---
        st.title(f"👤 Deep-Dive PIC - {sel_bulan}")
        target = st.selectbox("Pilih PIC:", df_filtered['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == target].copy()
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Avg Achievement", f"{df_pic['ACH_NUM'].mean():.1f}%")
            st.image("https://via.placeholder.com/150")
        with c2:
            fig = px.bar(df_pic, x='KPI', y='ACH_NUM', text_auto='.1f', color_continuous_scale='PuRd')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader(f"📑 Tabel Rincian Data Lengkap: {target}")
        
        # Menampilkan kolom rincian sesuai permintaan Anda: Bobot, Target, Real, Ach, Nilai
        df_rincian = df_pic[['KPI', 'UOM', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']].copy()
        df_rincian.index = range(1, len(df_rincian) + 1)
        
        st.table(df_rincian)

else:
    st.info("Memuat data dari Baris 5...")
