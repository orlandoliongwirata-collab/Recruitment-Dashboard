import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Tema Aesthetic
st.set_page_config(page_title="HR Recruitment Dashboard % ✨", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetricValue"] { color: #ff7eb9 !important; font-size: 28px; font-weight: bold; }
    .stSelectbox label { color: #ff7eb9; font-weight: bold; }
    
    /* Style Kartu Top 3 Champions */
    .rank-card {
        background: white; border-radius: 20px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border: 2px solid #ffdee9;
    }
    .rank-img {
        border-radius: 50%; width: 100px; height: 100px;
        object-fit: cover; border: 3px solid #ffb7ce; margin-bottom: 10px;
    }
    .highlight-name { font-weight: bold; font-size: 16px; color: #4a4a4a; margin-bottom: 5px; }
    .highlight-score { color: #ff7eb9; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Load Data Spesifik Sheet2 (GID: 1942814563)
@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    # GID Sheet2 (Format Perhitungan KPI)
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        # Melompati 2 baris sub-judul, baris ke-3 jadi Header Kuning
        df = pd.read_csv(url, skiprows=2, header=0)
        
        # Bersihkan Nama Kolom
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # --- TEKNIK FORWARD FILL ---
        # Menangani sel yang digabung (Merged Cells) untuk Nama, NIK, Foto
        for col in ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN']:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # Hapus baris 'TOTAL' agar tidak mengganggu perhitungan rata-rata
        df = df.dropna(subset=['KPI'])
        df = df[df['KPI'].str.contains('TOTAL', case=False, na=False) == False].copy()
        
        # Fungsi membersihkan kolom NILAI agar menjadi angka murni
        def clean_percent(x):
            s = str(x).replace('%', '').replace(',', '.').
