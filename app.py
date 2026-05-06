import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="SPK AHP", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.title("📊 Sistem Pendukung Keputusan")
st.markdown("## Pemilihan Guru Paling Aktif (Metode AHP)")
st.write("Silahkan isi penilaian dengan memilih kategori yang sesuai.")

st.markdown("---")

# ======================
# DATA
# ======================
kriteria = {
    "Kehadiran": {
        "Baik": "> 95%",
        "Cukup": "80% – 94%",
        "Kurang": "< 80%"
    },
    "Aktivitas Mengajar": {
        "Baik": "Metode variatif & aktif",
        "Cukup": "Sesuai rancangan namun kurang aktif",
        "Kurang": "Tidak sesuai rancangan & tidak aktif"
    },
    "Partisipasi Kegiatan Sekolah": {
        "Baik": "Aktif didalam ataupun diluar sekolah",
        "Cukup": "Ikut sebagian kegiatan sekolah",
        "Kurang": "Jarang mengikuti kegiatan"
    },
    "Pengembangan Diri": {
        "Baik": "> 4 pelatihan",
        "Cukup": "2–3",
        "Kurang": "< 1"
    },
    "Administrasi": {
        "Baik": "Lengkap dan tepat waktu",
        "Cukup": "Cukup lengkap namun terlambat",
        "Kurang": "Kurang lengkap & sering terlambat"
    }
}

bobot_kriteria = {
    "Kehadiran": 0.438,
    "Aktivitas Mengajar": 0.256,
    "Partisipasi Kegiatan Sekolah": 0.128,
    "Pengembangan Diri": 0.092,
    "Administrasi": 0.084
}

bobot_sub = {
    "Baik": 0.54,
    "Cukup": 0.29667,
    "Kurang": 0.16333
}

alternatif = ["Asrunsyah", "Istamin", "Sutiani", "Kasran", "Raminah", "Rukini", "Saleh"]

# ======================
# INPUT
# ======================
penilaian = {}

st.markdown("### Input Penilaian")

for guru in alternatif:
    with st.expander(guru):
        penilaian[guru] = {}

        for k, deskripsi in kriteria.items():
            pilihan = st.selectbox(
                k,
                ["Baik", "Cukup", "Kurang"],
                key=f"{guru}_{k}"
            )
            st.caption(deskripsi[pilihan])
            penilaian[guru][k] = pilihan

st.markdown("---")

# ======================
# PERHITUNGAN
# ======================
if st.button("Hitung Hasil", use_container_width=True):

    hasil = {}

    for guru in alternatif:
        total = 0
        hasil[guru] = {}

        for k in kriteria:
            nilai = bobot_kriteria[k] * bobot_sub[penilaian[guru][k]]
            hasil[guru][k] = round(nilai, 6)
            total += nilai

        hasil[guru]["Total"] = round(total, 6)

    df = pd.DataFrame(hasil).T
    df["Ranking"] = df["Total"].rank(ascending=False).astype(int)
    df_sorted = df.sort_values("Ranking")

    # ======================
    # DETAIL PERHITUNGAN
    # ======================
    st.markdown("### 📊 Detail Perhitungan AHP")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # ======================
    # RANKING
    # ======================
    st.markdown("### 🏆 Hasil Perangkingan")

    top_guru = df_sorted.index[0]
    st.success(f"Guru Terbaik: {top_guru}")

    st.dataframe(df_sorted[["Total", "Ranking"]], use_container_width=True)

    # ======================
    # GRAFIK (SUDAH DIPERBAIKI)
    # ======================
    st.markdown("### 📈 Grafik Nilai Akhir")

    df_plot = df_sorted.copy()
    df_plot["Label"] = df_plot["Ranking"].astype(str) + " - " + df_plot.index

    fig, ax = plt.subplots()

    ax.barh(df_plot["Label"], df_plot["Total"])
    ax.invert_yaxis()  # ranking 1 di atas

    # tampilkan angka di samping bar
    for i, v in enumerate(df_plot["Total"]):
        ax.text(v, i, f"{v:.3f}", va='center')

    ax.set_xlabel("Nilai")
    ax.set_title("Ranking Guru")

    st.pyplot(fig)

    # ======================
    # EXPORT EXCEL
    # ======================
    df_input = pd.DataFrame(penilaian).T

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_input.to_excel(writer, sheet_name='Input')
        df.to_excel(writer, sheet_name='Perhitungan')
        df_sorted.to_excel(writer, sheet_name='Ranking')

    st.download_button(
        "⬇️ Download Hasil Excel",
        data=output.getvalue(),
        file_name="hasil_ahp.xlsx"
    )
