import streamlit as st
import pandas as pd

# 1. Setup Halaman
st.set_page_config(page_title="Recruitment Hall of Fame ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 110px; height: 110px;
        object-fit: cover; border: 4px solid #ffb7ce; margin-bottom: 10px;
    }
    .highlight-name { font-weight: bold; color: #4a4a4a; font-size: 18px; }
    .highlight-score { color: #ff7eb9; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Ambil Data
@st.cache_data(ttl=5)
def load_data():
    # PASTIKAN ID SHEET DI BAWAH INI ADALAH ID SHEET TERBARU ANDA
    sheet_id = "14XHi4b6yzIA_p2AtkgsjQahPeOg16hL4DBAF9OSa39U" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    data.columns = [str(c).strip().lower() for c in data.columns]
    return data.dropna(subset=[data.columns[0]])

def clean_val(val):
    if pd.isna(val): return 0
    s = str(val).replace('Rp', '').replace('%', '').replace(',', '').strip()
    try: return float(s)
    except: return 0

try:
    df = load_data()
    
    with st.sidebar:
        st.title("Settings ⚙️")
        pilih_bulan = st.selectbox("📅 Pilih Bulan", df['bulan'].unique())

    # Data Processing
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)

    st.title(f"Recruitment Hall of Fame: {pilih_bulan} 🏆")
    st.divider()

    # --- RANKING BERDASARKAN TOTAL NILAI ---
    st.subheader("Monthly Champions 👑")
    df_rank = df_bulan.groupby('nama').agg({
        'nilai': 'mean',
        'foto': 'first'
    }).reset_index().sort_values(by='nilai', ascending=False)

    cols = st.columns(3)
    medals = ["🥇 Gold Performer", "🥈 Silver Performer", "🥉 Bronze Performer"]
    
    # Foto placeholder jika link di Sheets kosong/salah
    placeholder = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    for i in range(min(3, len(df_rank))):
        user = df_rank.iloc[i]
        with cols[i]:
            # Cek apakah link foto ada dan valid
            img_url = user['foto'] if pd.notna(user['foto']) and str(user['foto']).startswith('http') else placeholder
            
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 16px; margin-bottom: 5px;">{medals[i]}</div>
                    <img src="{img_url}" class="rank-img" onerror="this.src='{placeholder}'">
                    <div class="highlight-name">{user['nama']}</div>
                    <div style="margin-top:5px;">Score: <span class="highlight-score">{user['nilai']:.2f}</span></div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- TABEL PIVOT RINGKAS ---
    st.subheader("📋 Summary Performa")
    df_pivot = df_bulan.pivot_table(
        index='nama', columns='kpi', values='realisasi', aggfunc='mean'
    ).fillna(0)
    
    # Tambahkan kolom Nilai Rata-rata
    df_pivot['TOTAL SKOR ⭐'] = df_bulan.groupby('nama')['nilai'].mean()
    
    st.dataframe(df_pivot.style.format("{:.2f}"), use_container_width=True)

except Exception as e:
    st.error("Gagal terhubung ke Google Sheets.")
    st.info(f"Pesan Error: {e}")
    st.warning("Pastikan ID Sheet benar dan aksesnya sudah 'Anyone with the link can view'.")
