import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HR Dashboard Sheet2 ✨", layout="wide")

# Gaya Visual
st.markdown("""
    <style>
    .rank-card { background: white; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #ffdee9; }
    .rank-img { border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #ffb7ce; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563" 
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # PENTING: header=0 dan skiprows=2 berarti baris ke-3 di Sheets menjadi Judul Kolom
        df = pd.read_csv(url, skiprows=2, header=0)
        
        # Bersihkan nama kolom: Hilangkan spasi dan ubah ke Huruf Besar
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Jika kolom NAMA JABATAN terbaca aneh karena sel gabungan, kita rapikan
        # Kita hanya butuh kolom: NIK, NAMA, FOTO, KPI, TARGET, REAL, NILAI
        
        # --- TEKNIK FORWARD FILL ---
        # Di Sheet Anda, NAMA (Kolom C) dan FOTO (Kolom D) hanya terisi di baris pertama blok
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()

        # Hapus baris kosong atau baris 'TOTAL' agar tidak merusak data
        df = df.dropna(subset=['KPI'])
        df = df[df['KPI'].str.contains('TOTAL', case=False) == False]
        
        # Bersihkan Angka
        for col in ['NILAI', 'REAL', 'TARGET']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(str(x).replace('Rp','').replace('%','').replace(',','').strip()) if pd.notna(x) else 0)

        return df
    except Exception as e:
        st.error(f"Detail Error Pembacaan: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    with st.sidebar:
        st.title("Navigation 🧭")
        view = st.radio("Menu", ["🌍 Overview Team", "👤 PIC Deep-Dive"])

    if view == "🌍 Overview Team":
        st.title("🏆 Leaderboard Recruitment Sheet2")
        # Hitung skor total per PIC
        res = df.groupby('NAMA').agg({'NILAI': 'sum', 'FOTO': 'first'}).reset_index().sort_values('NILAI', ascending=False)
        
        cols = st.columns(len(res))
        for i, row in res.iterrows():
            with cols[i]:
                # Logika Foto: Jika link imgur/gdrive, pastikan bisa tampil
                pic = row['FOTO'] if str(row['FOTO']).startswith('http') else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                st.markdown(f"""
                    <div class="rank-card">
                        <img src="{pic}" class="rank-img">
                        <h4>{row['NAMA']}</h4>
                        <h2 style="color:#ff7eb9;">{row['NILAI']:.2f}</h2>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Ringkasan Detail KPI")
        piv = df.pivot_table(index='NAMA', columns='KPI', values='NILAI', aggfunc='sum').fillna(0)
        st.dataframe(piv, use_container_width=True)

    else:
        st.title("👤 PIC Deep-Dive Analysis")
        name = st.selectbox("Pilih PIC", df['NAMA'].unique())
        detail = df[df['NAMA'] == name]
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(detail['FOTO'].iloc[0] if str(detail['FOTO'].iloc[0]).startswith('http') else "https://via.placeholder.com/150")
            st.metric("Total Skor", f"{detail['NILAI'].sum():.2f}")
        with c2:
            fig = px.bar(detail, x='KPI', y='NILAI', color='KPI', title=f"Pencapaian {name}")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Pastikan Header di Sheet2 (NIK, NAMA, KPI, dll) berada tepat di Baris 3.")
