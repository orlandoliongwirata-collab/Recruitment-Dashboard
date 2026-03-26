import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Recruitment Achievement Dashboard", layout="wide")

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
    .avg-banner {
        background: linear-gradient(90deg, #ffdee9 0%, #b5fffc 100%);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        df = pd.read_csv(url, skiprows=2)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Forward Fill untuk merged cells
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Filter: Buang baris TOTAL dan pastikan ada KPI
        if 'KPI' in df.columns:
            df = df.dropna(subset=['KPI'])
            df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        # Fungsi khusus untuk membersihkan kolom ACH (Persentase)
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                # Menangani angka desimal seperti 1.06 (yang berarti 106%)
                val = float(s)
                # Jika angka di excel berupa desimal kecil (misal 1.06), konversi ke persen asli (106)
                return val if val > 2 else val * 100
            except:
                return 0.0

        if 'ACH' in df.columns:
            df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        else:
            # Jika kolom ACH tidak terbaca, buat dummy 0
            df['ACH_VAL'] = 0.0
            
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Menu 🧭")
        view = st.radio("Pilih Tampilan:", ["🌍 Overview Team (ACH%)", "👤 Detail PIC (ACH%)"])

    if view == "🌍 Overview Team (ACH%)":
        st.title("🏆 Leaderboard Achievement Tim")
        
        # Banner Rata-rata ACH Tim
        avg_team = df['ACH_VAL'].mean()
        st.markdown(f"""
            <div class="avg-banner">
                <h2 style="margin:0; color:#4a4a4a;">Rata-rata Achievement Seluruh Tim</h2>
                <h1 style="margin:0; color:#ff7eb9;">{avg_team:.1f}%</h1>
            </div>
        """, unsafe_allow_html=True)
        
        # Grouping per Nama
        df_rank = df.groupby('NAMA').agg({'ACH_VAL': 'mean', 'FOTO': 'first'}).reset_index().sort_values('ACH_VAL', ascending=False)
        
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
                        <div style="color:#ff7eb9; font-size:20px; font-weight:bold;">{row['ACH_VAL']:.1f}%</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Ringkasan Achievement per KPI")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='ACH_VAL', aggfunc='mean').fillna(0)
        st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)

    else:
        st.title("👤 PIC Achievement Analysis")
        list_nama = df['NAMA'].unique()
        target = st.selectbox("Pilih PIC:", list_nama)
        df_pic = df[df['NAMA'] == target]

        if not df_pic.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                pic_url = df_pic['FOTO'].iloc[0]
                if 'drive.google.com' in str(pic_url):
                    f_id = pic_url.split('file/d/')[1].split('/')[0]
                    pic_url = f"https://drive.google.com/uc?export=view&id={f_id}"
                
                st.image(pic_url if pd.notna(pic_url) and str(pic_url).startswith('http') else "https://via.placeholder.com/150", use_container_width=True)
                st.metric("Avg. Achievement", f"{df_pic['ACH_VAL'].mean():.1f}%")
                st.write(f"**Jabatan:** {df_pic['NAMA JABATAN'].iloc[0]}")

            with c2:
                fig = px.bar(df_pic, x='KPI', y='ACH_VAL', text_auto='.1f',
                             title=f"Grafik Achievement: {target}",
                             labels={'ACH_VAL': 'Achievement (%)'},
                             color='ACH_VAL', color_continuous_scale='PuRd')
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("📑 Tabel Rincian Achievement")
            # Menampilkan kolom asli dari Sheet untuk detail
            st.table(df_pic[['KPI', 'TARGET', 'REAL', 'ACH']].rename(columns={'ACH': 'ACH (%)'}))

    if st.button("Celebrate! 🥳"): st.balloons()
else:
    st.info("Sedang menarik data ACH dari Sheet2...")
