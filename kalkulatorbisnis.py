import streamlit as st
import pandas as pd
import numpy as np
import io

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Kalkulator Bisnis & BEP UMKM",
    page_icon="📊",
    layout="wide"
)

# Judul Utama
st.title("📊 Kalkulator & Proyeksi Keuntungan UMKM")
st.markdown("Gunakan alat ini untuk menghitung **Break-Even Point (BEP)** dan menganalisis proyeksi keuntungan bisnis Anda.")

st.divider()

# --- SIDEBAR: INPUT DATA BISNIS ---
st.sidebar.header("⚙️ Parameter Bisnis")

nama_produk = st.sidebar.text_input("Nama Produk/Layanan", value="Kopi Susu Gula Aren")
biaya_tetap = st.sidebar.number_input("Biaya Tetap per Bulan (Rp)", min_value=0, value=5000000, step=100000)
st.sidebar.caption("Contoh: Sewa tempat, gaji karyawan tetap, listrik/internet dasar.")

biaya_variabel = st.sidebar.number_input("Biaya Variabel per Unit (Rp)", min_value=0, value=8000, step=500)
st.sidebar.caption("Contoh: Bahan baku per porsi, kemasan, plastik.")

harga_jual = st.sidebar.number_input("Harga Jual per Unit (Rp)", min_value=0, value=18000, step=500)

# Validation Harga Jual
if harga_jual <= biaya_variabel:
    st.sidebar.error("⚠️ Harga jual harus lebih besar dari biaya variabel per unit!")

st.sidebar.divider()
st.sidebar.header("🎯 Target Penjualan")
target_penjualan = st.sidebar.slider("Target Penjualan per Bulan (Unit)", min_value=1, max_value=2000, value=800)

# --- PERHITUNGAN UTAMA ---
margin_kontribusi = harga_jual - biaya_variabel

if margin_kontribusi > 0:
    bep_unit = int(np.ceil(biaya_tetap / margin_kontribusi))
    bep_rupiah = bep_unit * harga_jual
    
    total_pendapatan = target_penjualan * harga_jual
    total_biaya_variabel = target_penjualan * biaya_variabel
    total_biaya = biaya_tetap + total_biaya_variabel
    laba_bersih = total_pendapatan - total_biaya
    
    # --- DISPLAY METRIK UTAMA ---
    st.subheader("📌 Hasil Perhitungan Titik Impas (BEP)")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(label="BEP (Unit)", value=f"{bep_unit:,} Unit")
    col2.metric(label="BEP (Rupiah)", value=f"Rp {bep_rupiah:,.0f}")
    col3.metric(label="Margin Kontribusi / Unit", value=f"Rp {margin_kontribusi:,.0f}")
    
    st.divider()
    
    # --- PROYEKSI KEUNTUNGAN & GRAFIK ---
    st.subheader("📈 Proyeksi Keuangan Bulan Ini")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Target Penjualan", f"{target_penjualan:,} Unit")
    m2.metric("Total Pendapatan", f"Rp {total_pendapatan:,.0f}")
    m3.metric("Total Biaya Operasional", f"Rp {total_biaya:,.0f}")
    
    # Warna delta indikator laba/rugi
    if laba_bersih >= 0:
        m4.metric("Estimasi Laba Bersih", f"Rp {laba_bersih:,.0f}", delta=f"Untung Rp {laba_bersih:,.0f}")
    else:
        m4.metric("Estimasi Laba Bersih", f"Rp {laba_bersih:,.0f}", delta=f"Rugi Rp {laba_bersih:,.0f}", delta_color="inverse")
        
    # --- SIMULASI KURVA BEP (GRAFIK INTERAKTIF) ---
    max_range = max(target_penjualan * 2, bep_unit * 2)
    units = np.linspace(0, max_range, 50)
    df_chart = pd.DataFrame({
        "Jumlah Unit Penjualan": units,
        "Total Biaya (Rp)": biaya_tetap + (units * biaya_variabel),
        "Total Pendapatan (Rp)": units * harga_jual
    }).set_index("Jumlah Unit Penjualan")

    st.write("#### Kurva Analisis Titik Impas")
    st.line_chart(df_chart)

    # --- EKSPOR DATA KE EXCEL ---
    st.divider()
    st.subheader("📥 Unduh Laporan Simulasi")

    # Membuat dataframe detail laporan
    df_laporan = pd.DataFrame({
        "Parameter / Metrik": [
            "Nama Produk", "Biaya Tetap (Rp)", "Biaya Variabel/Unit (Rp)", "Harga Jual/Unit (Rp)",
            "Margin Kontribusi/Unit (Rp)", "BEP (Unit)", "BEP (Rupiah)",
            "Target Penjualan (Unit)", "Total Pendapatan (Rp)", "Total Biaya (Rp)", "Estimasi Laba/Rugi (Rp)"
        ],
        "Nilai": [
            nama_produk, biaya_tetap, biaya_variabel, harga_jual,
            margin_kontribusi, bep_unit, bep_rupiah,
            target_penjualan, total_pendapatan, total_biaya, laba_bersih
        ]
    })

    # Konversi DataFrame ke Excel via Buffer Memory
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_laporan.to_excel(writer, index=False, sheet_name="Laporan BEP")
    
    st.download_button(
        label="📄 Download Laporan Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"Laporan_BEP_{nama_produk.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("Silakan pastikan Harga Jual lebih besar dari Biaya Variabel per unit.")