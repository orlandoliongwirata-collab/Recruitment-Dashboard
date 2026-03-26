import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Recruitment Achievement Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
        height: 100%;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce; margin-bottom: 10px;
    }
    .avg-banner {
        background: linear-gradient(90deg, #ffdee9 0%, #b5fffc 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        df = pd.read_csv(url, skiprows=2)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Forward Fill
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Filter: Buang baris TOTAL
        if 'KPI' in df.columns:
            df = df.dropna(subset=['KPI'])
            df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                val = float(s)
                return val if val > 2 else val * 100
            except:
                return 0.0

        if 'ACH' in df.columns:
            df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        else:
            df['ACH_VAL'] = 0.0
            
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Menu 🧭")
        view = st.radio("Pilih Tampilan:", ["🌍 Overview Team", "👤 Detail PIC"])

    if view == "🌍 Overview Team":
        st.title("🏆 Leaderboard Achievement Tim")
        
        avg_team = df['ACH_VAL'].mean()
        st.markdown(f'<div class="avg-banner"><h2>Rata-rata Achievement Tim</h2><h1 style="color:#ff7eb9;">{avg_team:.1f}%</h1></div>', unsafe_allow_html=True)
        
        # --- LOGIKA URUTAN: WAJIB SORT BERDASARKAN ACH_VAL DESCENDING ---
        df_rank = df.groupby('NAMA').agg({
            'ACH_VAL': 'mean', 
            'FOTO': 'first'
        }).reset_index()
        
        # Kita urutkan disini, lalu reset index agar index 0 pasti nilai tertinggi
        df_rank = df_rank.sort_values(by='ACH_VAL', ascending=False).reset_index(drop=True)
        
        cols = st.columns(len(df_rank))
        def_img = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

        for i, row in df_rank.iterrows():
            # Penentuan Medali Berdasarkan Urutan Hasil Sort
            if i == 0: medali, warna = "🥇", "#FFD700"
            elif i == 1: medali, warna = "🥈", "#C0C0C0"
            else: medali, warna = "🥉", "#CD7F32"
            
            with cols[i]:
                pic = row['FOTO']
                if 'drive.google.com' in str(pic):
                    f_id = pic.split('file/d/')[1].split('/')[0]
                    pic = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                img_src = pic if pd.notna(pic) and str(pic).startswith('http') else def_img
                
                st.markdown(f"""
                    <div class="rank-card">
                        <div style="font-size:25px; margin-bottom:5px;">{medali}</div>
                        <img src="{img_src}" class="rank-img" style="border-color:{warna};" onerror="this.src='{def_img}'">
                        <div style="font-weight:bold; font-size:16px;">{row['NAMA']}</div>
                        <div style="color:#ff7eb9; font-size:20px; font-weight:bold;">{row['ACH_VAL']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Achievement per KPI")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='ACH_VAL', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)

    else:
        # Bagian Detail PIC
        st.title("👤 PIC Achievement Analysis")
        list_nama = df['NAMA'].unique()
        target = st.selectbox("Pilih PIC:", list_nama)
        df_pic = df[df['NAMA'] == target]
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
                fig = px.bar(df_pic, x='KPI', y='ACH_VAL', text_auto='.1f', title=f"Achievement: {target}", color_discrete_sequence=['#ff7eb9'])
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Menghubungkan ke Google Sheets...")
