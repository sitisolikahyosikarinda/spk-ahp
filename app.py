import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="SPK AHP", layout="wide")


# TAMPILAN

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

h1 {
    font-size: 40px !important;
    font-weight: 700;
}

h2 {
    font-size: 26px !important;
    font-weight: 500;
    color: #444;
}

.stButton>button {
    height: 45px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)


# JUDUL & DESKRIPSI

st.title("📊 Sistem Pendukung Keputusan")
st.markdown("## Pemilihan Guru Paling Aktif (Metode AHP)")
st.write("Silahkan isi penilaian dengan memilih kategori yang sesuai.")

st.markdown("---")


# DATA

kriteria = {
    "Kehadiran": {
        "Baik": "Kehadiran > 95%",
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
        "Baik": "Lengkap dan tepat waktu pengumpulan",
        "Cukup": "Cukup lengkap namun pengumpulan agak terlambat.",
        "Kurang": "Kurang lengkap dan sering terlambat"
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


# INPUT

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


# PERHITUNGAN (rumus)

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

  
    # HASIL
    
    st.markdown("### Hasil Perhitungan")

    top_guru = df_sorted.index[0]
    st.write(f"**Guru Terbaik:** {top_guru}")

    st.dataframe(df_sorted[["Total", "Ranking"]], use_container_width=True)

    st.markdown("---")

    st.bar_chart(df_sorted["Total"], use_container_width=True)

  
    # EXPORT FILE EXCEL
    
    df_input = pd.DataFrame(penilaian).T

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_input.to_excel(writer, sheet_name='Input')
        df.to_excel(writer, sheet_name='AHP')
        df_sorted.to_excel(writer, sheet_name='Ranking')

    st.download_button(
        "Download Excel",
        data=output.getvalue(),
        file_name="hasil_ahp.xlsx"
    )
