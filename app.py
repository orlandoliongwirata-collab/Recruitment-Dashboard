import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Setup Halaman
st.set_page_config(page_title="Recruitment Hall of Fame ✨", layout="wide")

# CSS Aesthetic untuk Kartu Ranking
st.markdown("""
    <style>
    .main { background-color: #fdf6f9; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
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
        width: 110px;
        height: 110px;
        object-fit: cover;
        border: 4px solid #ffb7ce;
    }
    .gold { border: 4px solid #ffd700 !important; }
    .highlight-name { font-size: 20px; font-weight: bold; color: #4a4a4a; margin-top: 10px; }
    .highlight-total { font-size: 24px; color: #ff7eb9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def load_data():
    sheet_id = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o" 
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
    
    # Sidebar Filter
    with st.sidebar:
        st.title("Settings ⚙️")
        pilih_bulan = st.selectbox("📅 Pilih Bulan", df['bulan'].unique())
        st.divider()
        pilih_kpi = st.selectbox("📊 Cek Detail KPI", df['kpi'].unique())

    # Data Processing
    df_bulan = df[df['bulan'] == pilih_bulan].copy()
    for col in ['target', 'realisasi', 'nilai']:
        if col in df_bulan.columns:
            df_bulan[col] = df_bulan[col].apply(clean_val)

    st.title(f"Recruitment Hall of Fame: {pilih_bulan} 🏆")

    # --- LOGIKA RANKING BERDASARKAN TOTAL NILAI ---
    # Menghitung rata-rata nilai per orang
    df_rank = df_bulan.groupby('nama').agg({
        'nilai': 'mean',
        'foto': 'first'
    }).reset_index().sort_values(by='nilai', ascending=False).reset_index(drop=True)

    # Menampilkan Top 3 Visual
    st.subheader("Our Top Performers ✨")
    cols = st.columns(3)
    medals = ["👑 Gold", "🥈 Silver", "🥉 Bronze"]
    
    for i in range(min(3, len(df_rank))):
        user = df_rank.iloc[i]
        with cols[i]:
            img = user['foto'] if pd.notna(user['foto']) else "https://via.placeholder.com/150"
            is_gold = "gold" if i == 0 else ""
            st.markdown(f"""
                <div class="rank-card">
                    <div style="font-size: 30px;">{medals[i]}</div>
                    <img src="{img}" class="rank-img {is_gold}">
                    <div class="highlight-name">{user['nama']}</div>
                    <div class="highlight-total">{user['nilai']:.2f}</div>
                    <div style="color: gray; font-size: 14px;">Average Monthly Score</div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- ROW 2: GRAFIK & TABEL ---
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader(f"Detail KPI: {pilih_kpi}")
        df_chart = df_bulan[df_bulan['kpi'] == pilih_kpi]
        fig = px.bar(df_chart, x='nama', y=['target', 'realisasi'], barmode='group',
                     color_discrete_map={'target': '#ffdee9', 'realisasi': '#ffb7ce'},
                     template="plotly_white", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Leaderboard List")
        # Menampilkan ranking dalam bentuk tabel simpel
        df_display = df_rank.copy()
        df_display.index = df_display.index + 1
        st.table(df_display[['nama', 'nilai']].rename(columns={'nama': 'Name', 'nilai': 'Total Score'}))

    if st.button("Launch Celebration! 🥳"):
        st.balloons()

except Exception as e:
    st.error(f"Error: {e}")
