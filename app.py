import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema Aesthetic
st.set_page_config(page_title="Recruitment Squad Dashboard ✨", layout="wide")

# Custom CSS untuk gaya Gen-Z (Pastel Pink & Soft UI)
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 32px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 */
    .rank-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        border: 4px solid #ffb7ce;
        margin-bottom: 10px;
    }
    .stDataFrame { background: white; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data (PASTIKAN ID SHEET ANDA BENAR)
@st.cache_data(ttl=5)
def load_data():
    sheet_id = "14XHi4b6yzIA_p2AtkgsjQahPeOg16hL4DBAF9OSa39U" # Ganti dengan ID Anda jika berbeda
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    return data.dropna(how='all').reset_index(drop=True)

try:
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.title("Team Vibe 💅")
        st.select_slider("Energy Check", options=["😴", "☕", "🫠", "🔥", "✨"])
        st.divider()
        st.write("🎧 **Work Beats**")
        st.markdown('<iframe src="http://googleusercontent.com/spotify.com/7" width="100%" height="80" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>', unsafe_allow_html=True)

    st.title("Recruitment Squad Hall of Fame 🌸")
    st.markdown("#### *Let's make magic happen today!* ✨")

    # Ambil Data Berdasarkan Urutan Kolom
    # Kolom 0 = Nama, Kolom 1 = Hired, Kolom 2 = TTF, Kolom 3 = Foto
    nama_tim = df.iloc[:, 0]
    angka_hired = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
    angka_ttf = pd.to_numeric(df.iloc[:, 2], errors='coerce').fillna(0)

    # --- TOP PERFORMERS WITH PHOTOS ---
    st.subheader("Monthly Champions 👑")
    
    # Siapkan data untuk ranking foto
    df_rank = df.copy()
    df_rank['Hired_Clean'] =angka_hired
    # Urutkan berdasarkan siapa yang paling banyak Hired
    df_top3 = df_rank.sort_values(by='Hired_Clean', ascending=False).head(3)

    cols_top = st.columns(3)
    # Gunakan link foto placeholder jika link di Excel mati/kosong
    default_img = "http://googleusercontent.com/google.com/search?q=profil_placeholder_png"

    for i in range(len(df_top3)):
        rank_data = df_top3.iloc[i]
        with cols_top[i]:
            # Jika kolom ke-4 (indeks 3) berisi Foto, kita ambil
            img_url = rank_data.iloc[3] if len(rank_data) > 3 and pd.notna(rank_data.iloc[3]) else default_img
            st.markdown(f"""
                <div class="rank-card">
                    <img src="{img_url}" class="rank-img">
                    <div style="font-weight:bold; font-size:18px;">{rank_data.iloc[0]}</div>
                    <div style="color:#ff7eb9; font-size:22px; font-weight:bold;">{int(rank_data.iloc[1])} Hired</div>
                    <div style="color:#888;">TTF: {rank_data.iloc[2]:.0f} Days</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.divider()

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hired 🏆", f"{int(angka_hired.sum())}")
    c2.metric("Avg. Time to Fill ⏱️", f"{angka_ttf.mean():.1f} Days")
    c3.metric("Team Happiness 💌", "4.9/5.0")

    # Tabel & Grafik
    left, right = st.columns([1, 1.5])
    with left:
        st.subheader("Leaderboard 👑")
        st.dataframe(df, hide_index=True, use_container_width=True)
        if st.button("Celebrate Wins! 🥳"):
            st.balloons()

    with right:
        st.subheader("Performance Chart 📈")
        chart_df = pd.DataFrame({'Recruiter': nama_tim, 'Total Hires': angka_hired})
        fig = px.bar(chart_df, x='Recruiter', y='Total Hires', color_discrete_sequence=['#ffb7ce'], template="plotly_white", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("✨ Menghubungkan ke Google Sheets... ✨")
    st.info("Pastikan Google Sheets Anda sudah di-Share ke 'Anyone with the link can view' dan kolom FOTO sudah diisi.")
