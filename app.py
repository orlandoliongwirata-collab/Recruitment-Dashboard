import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Gaya Visual
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
        df_raw[2] = df_raw[2].ffill() # Nama PIC

        month_config = {
            'Januari':  {'bobot': 9,  'target': 10, 'real': 11, 'ach': 12, 'nilai': 13},
            'Februari': {'bobot': 14, 'target': 15, 'real': 16, 'ach': 17, 'nilai': 18},
            'Maret':    {'bobot': 19, 'target': 20, 'real': 21, 'ach': 22, 'nilai': 23},
            'April':    {'bobot': 24, 'target': 25, 'real': 26, 'ach': 27, 'nilai': 28},
            'Mei':      {'bobot': 29, 'target': 30, 'real': 31, 'ach': 32, 'nilai': 33},
            'Juni':     {'bobot': 34, 'target': 35, 'real': 36, 'ach': 37, 'nilai': 38},
            'Juli':     {'bobot': 39, 'target': 40, 'real': 41, 'ach': 42, 'nilai': 43},
            'Agustus':  {'bobot': 44, 'target': 45, 'real': 46, 'ach': 47, 'nilai': 48}
        }

        all_data = []
        for month, cols in month_config.items():
            if cols['nilai'] < df_raw.shape[1]:
                temp = df_raw[[2, 6, 7, cols['bobot'], cols['target'], cols['real'], cols['ach'], cols['nilai']]].copy()
                temp.columns = ['NAMA', 'KPI', 'UOM', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']
                temp['BULAN_DATA'] = month
                all_data.append(temp)
        
        df = pd.concat(all_data, ignore_index=True)
        df = df.dropna(subset=['KPI'])
        df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)].copy()
        
        def get_quarter(m):
            if m in ['Januari', 'Februari', 'Maret']: return 'Q1 (Jan - Mar)'
            elif m in ['April', 'Mei', 'Juni']: return 'Q2 (Apr - Jun)'
            elif m in ['Juli', 'Agustus', 'September']: return 'Q3 (Jul - Sep)'
            elif m in ['Oktober', 'November', 'Desember']: return 'Q4 (Okt - Des)'
            return 'Lainnya'

        df['TRIWULAN'] = df['BULAN_DATA'].apply(get_quarter)

        # --- PERBAIKAN LOGIKA PEMBERSAHAN ANGKA (SUPPORT >100%) ---
        def clean_to_num(x):
            try:
                s = str(x).replace('%', '').replace(',', '.').replace('-', '0').replace('Rp', '').strip()
                v = float(s)
                # Jika Google Sheets mengeksport angka persen sebagai desimal (misal 1.2 = 120%), kalikan 100.
                # Jika sudah berupa angka bulat biasa (misal 120), gunakan langsung nilainya.
                return v * 100 if v <= 2.5 and v > 0 else v
            except: 
                return 0.0
            
        df['ACH_NUM'] = df['ACH'].apply(clean_to_num)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Admin Panel 🧭")
        
        mode_periode = st.radio("🗓️ Mode Periode:", ["Laporan Bulanan", "Juara Triwulan (3 Bulan)"])
        
        if mode_periode == "Laporan Bulanan":
            list_bulan = df['BULAN_DATA'].unique()
            sel_periode = st.selectbox("📅 Pilih Bulan:", list_bulan)
            df_filtered = df[df['BULAN_DATA'] == sel_periode].copy()
        else:
            list_q = [q for q in df['TRIWULAN'].unique() if q != 'Lainnya']
            sel_periode = st.selectbox("🏆 Pilih Triwulan:", list_q)
            df_filtered = df[df['TRIWULAN'] == sel_periode].copy()

        st.divider()
        view = st.radio("Tampilan:", ["🌍 Overview Tim", "👤 Detail PIC"])

    if view == "🌍 Overview Tim":
        st.title(f"🏆 Leaderboard - {sel_periode}")
        
        df_rank = df_filtered.groupby('NAMA').agg({'ACH_NUM': 'mean'}).reset_index().sort_values('ACH_NUM', ascending=False).reset_index(drop=True)
        avg_score = df_rank['ACH_NUM'].mean()
        
        st.markdown(f'<div class="avg-banner"><h3>Average Performance Score</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
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
        st.subheader(f"📋 Ringkasan per KPI ({sel_periode})")
        
        def custom_label(row):
            kpi, val = str(row['KPI']).upper(), row['ACH_NUM']
            if any(x in kpi for x in ["SUCCESS RATE", "QUALITY OF HIRE", "MANPOWER FULFILLMENT", "TRAINING HOURS"]):
                return f"{val:.1f}%"
            elif "SERVICE LEVEL" in kpi:
                return f"{val:.0f} Hari"
            elif "COST EFFECTIVENESS" in kpi:
                return f"Rp {val:,.0f}"
            else:
                return f"{val:.1f}"

        df_filtered['DISPLAY'] = df_filtered.apply(custom_label, axis=1)
        
        if mode_periode == "Juara Triwulan (3 Bulan)":
            piv = df_filtered.pivot_table(index='NAMA', columns='KPI', values='ACH_NUM', aggfunc='mean').fillna(0)
            piv = piv.reindex(df_rank['NAMA'])
            st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)
        else:
            piv = df_filtered.pivot_table(index='NAMA', columns='KPI', values='DISPLAY', aggfunc='first').fillna("-")
            piv = piv.reindex(df_rank['NAMA'])
            st.dataframe(piv, use_container_width=True)

    else:
        st.title(f"👤 Deep-Dive PIC - {sel_periode}")
        target = st.selectbox("Pilih PIC:", df_filtered['NAMA'].unique())
        df_pic = df_filtered[df_filtered['NAMA'] == target].copy()
        
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.metric("Avg Achievement", f"{df_pic['ACH_NUM'].mean():.1f}%")
            st.image("https://via.placeholder.com/150")
        
        with c2:
            df_pic_avg = df_pic.groupby('KPI', as_index=False)['ACH_NUM'].mean()
            fig = px.bar(
                df_pic_avg, 
                x='KPI', 
                y='ACH_NUM', 
                text_auto='.1f', 
                color_discrete_sequence=['#ff7eb9'],
                title=f"Rata-rata Pencapaian KPI ({sel_periode})"
            )
            fig.update_layout(yaxis_title="Rata-rata ACH (%)", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader(f"📑 Tabel Rincian Data: {target}")
        
        if mode_periode == "Juara Triwulan (3 Bulan)":
            bulan_list = df_pic['BULAN_DATA'].unique()
            tabs = st.tabs([f"📅 {b}" for b in bulan_list])
            
            for idx, b_name in enumerate(bulan_list):
                with tabs[idx]:
                    df_sub = df_pic[df_pic['BULAN_DATA'] == b_name][['KPI', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']].copy()
                    df_sub.index = range(1, len(df_sub) + 1)
                    st.table(df_sub)
        else:
            df_rincian = df_pic[['KPI', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']].copy()
            df_rincian.index = range(1, len(df_rincian) + 1)
            st.table(df_rincian)
else:
    st.info("Memuat data...")
