st.divider()

    # --- TAMPILAN TABS AGAR RAPI ---
    tab1, tab2 = st.tabs(["📊 Visual Analysis", "📋 Detailed Data Table"])

    with tab1:
        st.subheader(f"Analysis: {pilih_kpi}")
        df_chart = df_bulan[df_bulan['kpi'] == pilih_kpi]
        if not df_chart.empty:
            fig = px.bar(df_chart, x='nama', y=['target', 'realisasi'], 
                         barmode='group', color_discrete_map={'target': '#ffdee9', 'realisasi': '#ffb7ce'},
                         template="plotly_white", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("📋 Master Data Recruitment")
        st.markdown("Gunakan fitur *Search* di pojok kanan tabel untuk mencari nama spesifik.")
        
        # Menata kolom
        df_display = df_bulan[['nama', 'kpi', 'target', 'realisasi', '% ach', 'nilai']].copy()
        df_display.columns = ['Nama', 'Jenis KPI', 'Target', 'Realisasi', '% Achievement', 'Skor Nilai']
        
        # Styling Tabel agar lebih "Clean"
        def style_table(styler):
            styler.format({
                'Target': '{:,.0f}', 
                'Realisasi': '{:,.0f}', 
                '% Achievement': '{:.1f}%', 
                'Skor Nilai': '{:.2f}'
            })
            # Memberikan warna background gradient hanya pada achievement
            styler.background_gradient(subset=['% Achievement'], cmap='PuRd')
            # Membuat teks Nama menjadi tebal
            styler.set_properties(subset=['Nama'], **{'font-weight': 'bold', 'color': '#4a4a4a'})
            return styler

        st.dataframe(
            style_table(df_display.style),
            use_container_width=True,
            hide_index=True,
            height=500 # Mengunci tinggi tabel agar ada scrollbar internal (lebih rapi)
        )

    if st.button("Launch Celebration! 🥳"):
        st.balloons()
