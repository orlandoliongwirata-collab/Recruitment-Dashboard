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
        # Load Baris ke-5 Excel (skip 3 baris instruksi/judul)
        df_raw = pd.read_csv(url, skiprows=3)
        df_raw.columns = range(df_raw.shape[1])
        df_raw[2] = df_raw[2].ffill() 

        # --- UPDATE KOORDINAT BULAN (Januari - Juni & Seterusnya) ---
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
        
        # Mapping Quarter / Triwulan
        def get_quarter(m):
            if m in ['Januari', 'Februari', 'Maret']: return 'Q1 (Jan - Mar)'
            elif m in ['April', 'Mei', 'Juni']: return 'Q2 (Apr - Jun)'
            elif m in ['Juli', 'Agustus', 'September']: return 'Q3 (Jul - Sep)'
            elif m in ['Oktober', 'November', 'Desember']: return 'Q4 (Okt - Des)'
            return 'Lainnya'

        df['TRIWULAN'] = df['BULAN_DATA'].apply(get_quarter)

        # Clean ACH untuk angka kalkulasi
        def clean_to_num(x):
            try:
                s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0
        df['ACH_NUM'] = df['ACH'].apply(clean_to_num)

        # Logika PIC khusus yang menghitung Cost Effectiveness dalam ranking
        pic_dengan_cost = [
            "CAROLINA PERMATA SARI", "YUNITA SAVIOR", "ANGELA", 
            "BERLIANNA DEWI SETIAWAN", "TIARA ELSA STEVANNY"
        ]

        df_for_rank = df.copy()
        df_for_rank = df_for_rank[
            (df_for_rank['NAMA'].str.upper().isin(pic_dengan_cost)) | 
            (~df_for_rank['KPI'].str.contains('COST EFFECTIVENESS', case=False, na=False))
        ]

        df_display = df[~df['KPI'].str.contains('COST EFFECTIVENESS', case=False, na=False)].copy()
        
        return df_display, df_for_rank
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_display, df_for_rank = load_data()

if not df_display.empty:
    with st.sidebar:
        st.title("Admin Panel 🧭")
        
        # Pilihan Mode Periode
        mode_periode = st.radio("🗓️ Mode Periode:", ["Laporan Bulanan", "Juara Triwulan (3 Bulan)"])
        
        if mode_periode == "Laporan Bulanan":
            list_bulan = df_display['BULAN_DATA'].unique()
            sel_periode = st.selectbox("📅 Pilih Bulan:", list_bulan)
            df_filtered_view = df_display[df_display['BULAN_DATA'] == sel_periode].copy()
            df_filtered_rank = df_for_rank[df_for_rank['BULAN_DATA'] == sel_periode].copy()
        else:
            list_q = [q for q in df_display['TRIWULAN'].unique() if q != 'Lainnya']
            sel_periode = st.selectbox("🏆 Pilih Triwulan:", list_q)
            df_filtered_view = df_display[df_display['TRIWULAN'] == sel_periode].copy()
            df_filtered_rank = df_for_rank[df_for_rank['TRIWULAN'] == sel_periode].copy()

        st.divider()
        view = st.radio("Tampilan:", ["🌍 Overview Tim", "👤 Detail PIC"])

    if view == "🌍 Overview Tim":
        st.title(f"🏆 Leaderboard - {sel_periode}")
        
        # Perhitungan Rata-Rata ACH Periode Terpilih
        df_rank = df_filtered_rank.groupby('NAMA').agg({'ACH_NUM': 'mean'}).reset_index().sort_values('ACH_NUM', ascending=False).reset_index(drop=True)
        
        avg_score = df_filtered_rank['ACH_NUM'].mean()
        st.markdown(f'<div class="avg-banner"><h3>Average Performance Score</h3><h1>{avg_score:.1f}%</h1></div>', unsafe_allow_html=True)
        
        # Kartu Medali
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
            kpi, val = row['KPI'].upper(), row['ACH_NUM']
            if any(x in kpi for x in ["SUCCESS RATE", "QUALITY OF HIRE", "MANPOWER FULFILLMENT"]): return f"{val:.1f}%"
            elif "SERVICE LEVEL" in kpi: return f"{val:.0f} Hari"
            elif "TRAINING HOURS" in kpi: return f"{val:.1f} Jam"
            else: return f"{val:.1f}"

        df_filtered_view['DISPLAY'] = df_filtered_view.apply(custom_label, axis=1)
        
        # Aggregate rata-rata jika mode Triwulan
        if mode_periode == "Juara Triwulan (3 Bulan)":
            piv = df_filtered_view.pivot_table(index='NAMA', columns='KPI', values='ACH_NUM', aggfunc='mean').fillna(0)
            piv = piv.reindex(df_rank['NAMA'])
            st.dataframe(piv.style.format("{:.1f}%"), use_container_width=True)
        else:
            piv = df_filtered_view.pivot_table(index='NAMA', columns='KPI', values='DISPLAY', aggfunc='first').fillna("-")
            piv = piv.reindex(df_rank['NAMA'])
            st.dataframe(piv, use_container_width=True)

    else:
        st.title(f"👤 Deep-Dive PIC - {sel_periode}")
        target = st.selectbox("Pilih PIC:", df_filtered_view['NAMA'].unique())
        df_pic_display = df_filtered_view[df_filtered_view['NAMA'] == target].copy()
        df_pic_rank = df_filtered_rank[df_filtered_rank['NAMA'] == target]
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Avg Achievement", f"{df_pic_rank['ACH_NUM'].mean():.1f}%")
            st.image("https://via.placeholder.com/150")
        with c2:
            fig = px.bar(df_pic_display, x='KPI', y='ACH_NUM', text_auto='.1f', color_continuous_scale='PuRd')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        st.subheader(f"📑 Tabel Rincian Data: {target}")
        df_rincian = df_pic_display[['KPI', 'BOBOT', 'TARGET', 'REAL', 'ACH', 'NILAI']].copy()
        df_rincian.index = range(1, len(df_rincian) + 1)
        st.table(df_rincian)
else:
    st.info("Memuat data...")
