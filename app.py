@st.cache_data(ttl=1)
def load_data():
    sid = "182IHHJRWlfcnr8acNSDIZyh-y_gAxNwo8OB12geEp7o"
    gid = "1942814563"
    url = f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"
    
    try:
        df = pd.read_csv(url, skiprows=2)
        df.columns = [str(c).strip().upper() for c in df.columns]

        # 1. Tambahkan kolom BULAN otomatis jika belum ada (Berdasarkan Blok)
        # Sesuai gambar Anda, setiap 8 baris adalah satu bulan
        if 'BULAN' not in df.columns:
            # Membuat list bulan (Januari untuk 24 baris pertama, Februari 24 baris berikutnya, dst)
            # Anda bisa sesuaikan angka 24 ini sesuai jumlah baris per bulan di Sheets
            df['BULAN'] = "Januari"
            # Tips: Menambah kolom BULAN di Sheet tetap cara paling aman
        
        # 2. Forward Fill untuk merged cells
        cols_to_fill = ['NIK', 'NAMA', 'FOTO', 'NAMA JABATAN', 'BULAN']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df[col].ffill()
        
        # 3. PEMBERSIHAN KRUSIAL:
        if 'KPI' in df.columns:
            df = df.dropna(subset=['KPI']) # Buang baris kosong
            
            # Buang baris yang isinya 'TOTAL' atau 'NAMA' atau 'NIK' (Baris Header berulang)
            df = df[~df['NAMA'].str.contains('NAMA', case=False, na=False)].copy()
            df = df[~df['KPI'].str.contains('TOTAL', case=False, na=False)].copy()
            df = df[~df['KPI'].str.contains('KPI', case=False, na=False)].copy()
        
        # 4. Bersihkan ACH
        def clean_ach(x):
            s = str(x).replace('%', '').replace(',', '.').replace('-', '0').strip()
            try:
                v = float(s)
                return v if v > 2 else v * 100
            except: return 0.0

        if 'ACH' in df.columns:
            df['ACH_VAL'] = df['ACH'].apply(clean_ach)
        else:
            df['ACH_VAL'] = 0.0
            
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()
