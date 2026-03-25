# --- TABEL DETAIL ALL KPI (VERSI SIMPEL TANPA MATPLOTLIB) ---
    st.subheader("📋 Detail Seluruh KPI Anak Buah")
    st.markdown("Berikut adalah data lengkap pencapaian seluruh tim untuk bulan ini:")
    
    df_display = df_bulan[['nama', 'kpi', 'target', 'realisasi', '% ach', 'nilai']].copy()
    df_display.columns = ['Nama', 'Jenis KPI', 'Target', 'Realisasi', '% Achievement', 'Skor Nilai']
    
    # Format angka agar rapi
    st.dataframe(
        df_display.style.format({
            'Target': '{:,.0f}', 
            'Realisasi': '{:,.0f}', 
            '% Achievement': '{:.1f}%', 
            'Skor Nilai': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
