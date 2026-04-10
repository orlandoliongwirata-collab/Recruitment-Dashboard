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

@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        df_raw = pd.read_csv(url, skiprows=3)
        df_raw.columns = range(df_raw.shape[1])
        
        # Kolom C=2 (NAMA), Kolom H=7 (KPI), Kolom I=8 (UOM)
        df_raw[2] = df_raw[2].ffill() 

        # Konfigurasi Kolom Bulanan
        month_config = {
            'Januari':  {'target': 10, 'real': 11, 'ach': 12},
            'Februari': {'target': 15, 'real': 16, 'ach': 17},
            'Maret':    {'target': 20, 'real': 21, 'ach': 22},
            'April':    {'target': 25, 'real': 26, 'ach': 27}
        }

        all_data = []
        for month, cols in month_config.items():
            if cols['ach'] < df_raw.shape[1]:
                # Kita ambil tambahan kolom 8 (UOM) agar tahu satuannya
                temp = df_raw[[2, 7, 8, cols['target'], cols['real'], cols['ach']]].copy()
                temp.columns = ['NAMA', 'KPI', 'UOM', 'TARGET', 'REAL', 'ACH']
                temp['BULAN_DATA'] = month
                all_data.append(temp)
        
        df = pd.concat(all_data, ignore_index=True)
        df = df.dropna(subset=['KPI'])
        df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)]
        
        # --- PERBAIKAN LOGIKA SATUAN ---
        def format_value(val, uom):
            try:
                # Bersihkan karakter non-numerik kecuali titik/koma
                s = str(val).replace('%', '').replace(',', '.').replace('-', '0').strip()
                v = float(s)
                
                # Jika UOM adalah persen, pastikan dalam skala 0-100
                if uom == '%':
                    return v if v > 2 else v * 100
                return v # Untuk Jam atau Jumlah (#), biarkan angka aslinya
            except:
                return 0.0
            
        # Terapkan format berbeda berdasarkan kolom UOM
        df['VALUE_NUM'] = df.apply(lambda x: format_value(x['ACH'], x['UOM']), axis=1)
        
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
        # Rata-rata tim tetap menggunakan angka achievement
        avg_score = df_filtered['VALUE_NUM'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Average Team Achievement</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
        df_rank = df_filtered.groupby('NAMA').agg({'VALUE_NUM': 'mean'}).reset_index().sort_values('VALUE_NUM', ascending=False).reset_index(drop=True)
        
        cols = st.columns(min(len(df_rank), 5))
        for i, row in df_rank.iterrows():
            with cols[i % 5]:
                medali = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:20px;">{medali}</div>
                        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" class="rank-img">
                        <div style="font-weight:bold; font-size:13px; min-height:40px;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-weight:bold; font-size:18px;">{row['VALUE_NUM']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan per KPI (Adaptif Satuan)")
        
        # Kita buat kolom tampilan yang menggabungkan angka + satuan
        def label_satuan(row):
            if row['UOM'] == '%': return f"{row['VALUE_NUM']:.1f}%"
            if row['UOM'] == 'Jam': return f"{row['VALUE_NUM']:.1f} Jam"
            return f"{row['VALUE_NUM']:.0f}" # Untuk jumlah (#)

        df_filtered['DISPLAY_VAL'] = df_filtered.apply(label_satuan, axis=1)
        piv = df_filtered.pivot_table(index='NAMA', columns='KPI', values='DISPLAY_VAL', aggfunc='first').fillna("-")
        st.dataframe(piv, use_container_width=True)

    else:
        # Detail PIC
        st.title(f"👤 Deep-Dive PIC - {sel_bulan}")
        target = st.selectbox("Pilih PIC:", df_filtered['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == target].copy()
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Avg Achievement", f"{df_pic['VALUE_NUM'].mean():.1f}%")
            st.image("https://via.placeholder.com/150")
        with c2:
            fig = px.bar(df_pic, x='KPI', y='VALUE_NUM', text='VALUE_NUM', color_continuous_scale='PuRd')
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        # Tabel rincian dengan satuan asli
        st.table(df_pic[['KPI', 'UOM', 'TARGET', 'REAL', 'ACH']])
else:
    st.info("Memuat data...")
