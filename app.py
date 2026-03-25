import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema Aesthetic
st.set_page_config(page_title="Recruitment Squad Dashboard ✨", layout="wide")

# Custom CSS untuk tampilan Gen-Z
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 32px; font-weight: bold; }
    .stButton>button { 
        background-color: #ffb7ce; border-radius: 20px; border: none; 
        color: white; width: 100%; height: 3em; font-weight: bold; 
    }
    .stDataFrame { background: white; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Ambil Data (Sangat Stabil)
@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    data = pd.read_csv(url)
    # Membersihkan baris kosong dan spasi pada nama kolom
    data.columns = data.columns.str.strip()
    data = data.dropna(subset=[data.columns[0]])
    return data

try:
    df = load_data()
    
    # Header
    st.title("Recruitment Squad Dashboard 🌸")
    st.markdown("#### *Slaying the targets, one hire at a time!* ✨")

    # Ambil Data Berdasarkan Urutan Kolom
    # Kolom 0 = Nama, Kolom 1 = Hired, Kolom 2 = Time to Fill
    nama_tim = df.iloc[:, 0].astype(str)
    angka_hired = pd.to_numeric(df.iloc[:, 1], errors='coerce').fillna(0)
    angka_ttf = pd.to_numeric(df.iloc[:, 2], errors='coerce').fillna(0)

    # --- ROW 1: METRICS UTAMA ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Hired 🏆", f"{int(angka_hired.sum())}")
    c2.metric("Avg. Time to Fill ⏱️", f"{angka_ttf.mean():.1f} Days")
    c3.metric("Team Happiness 💌", "4.9/5.0")

    st.divider()

    # --- ROW 2: TABEL & GRAFIK ---
    left, right = st.columns([1, 1.5])
    
    with left:
        st.subheader("Leaderboard 👑")
        st.dataframe(df, hide_index=True, use_container_width=True)
        if st.button("Celebrate Wins! 🥳"):
            st.balloons()

    with right:
        st.subheader("Performance Analysis 📈")
        # Buat grafik tanpa ribet
        fig = px.bar(
            x=nama_tim, 
            y=angka_hired, 
            labels={'x': 'Recruiter', 'y': 'Hires'},
            color_discrete_sequence=['#ffb7ce'], 
            template="plotly_white", 
            text=angka_hired
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    # Sidebar: Mood & Music
    with st.sidebar:
        st.title("Team Vibe 💅")
        st.select_slider("Energy Check", options=["😴", "☕", "🫠", "🔥", "✨"])
        st.divider()
        st.write("🎧 **Focus Beats**")
        st.markdown('<iframe src="https://open.spotify.com/embed/playlist/37i9dQZF1DX8Ueb99idp6R" width="100%" height="80" frameBorder="0" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Almost there! ✨")
    st.write("Checking connection to Google Sheets...")
