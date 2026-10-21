# 📊 Dashboard Operasional Penjualan
🔗 **Demo:** https://dashboard-penjualan-sherly.streamlit.app

**Bedah Kasus 1 · Visualisasi Data**  
Sherly Saskia Rani · NIM 241051002

🔗 **Demo:** (isi setelah deploy)

Dashboard interaktif berbasis Streamlit untuk menganalisis data operasional penjualan. Dataset berisi **1.000 data sintesis** yang dikembangkan dari 2 baris seed pada materi kuliah (Laptop dan Buku).

## Data seed

| Produk | Kategori | Harga (Rp) | Jumlah Terjual | Tanggal |
|---|---|---|---|---|
| Laptop | Elektronik | 8.500.000 | 45 | 01/01/24 |
| Buku | Pendidikan | 75.000 | 120 | 02/01/24 |

Data sintesis dibangkitkan dengan asumsi: 10 produk dalam 3 kategori (Elektronik, Pendidikan, Fashion), harga berdistribusi lognormal di sekitar harga seed, jumlah terjual berdistribusi Poisson dengan pola musiman (Januari, Juli sampai Agustus, dan Desember lebih ramai), serta harga lebih tinggi cenderung menurunkan jumlah terjual. Data ini hanya untuk latihan, bukan data penjualan sebenarnya.

## Skala pengukuran data

| Kolom | Skala | Visualisasi |
|---|---|---|
| Produk, Kategori | Nominal | Bar chart, pie chart |
| Harga (Rp) | Rasio (kontinu) | Histogram, box plot |
| Jumlah Terjual | Rasio (diskrit) | Histogram |
| Tanggal | Interval | Line chart tren waktu |

## Fitur dashboard

- 5 kartu KPI: total pendapatan, unit terjual, jumlah transaksi, median harga, rata-rata unit per transaksi
- Filter sidebar: kategori, produk, rentang tanggal
- 5 tab: Kategorik, Numerik, Waktu, Korelasi & Uji, Data
- Tren harian, mingguan, dan bulanan dengan rata-rata bergerak, serta heatmap hari × bulan
- Uji statistik: Spearman dan Kruskal-Wallis
- Unduh data hasil filter dalam format CSV

## Temuan utama

- Elektronik menyumbang sekitar 92% pendapatan. Laptop saja sekitar 56%, dan Laptop bersama Smartphone sekitar 81% (prinsip Pareto).
- Kategori Pendidikan paling banyak transaksinya (42,6%), tetapi hanya menyumbang sekitar 4% pendapatan.
- Harga miring ke kanan (skewness 1,55) dan tidak normal, sehingga median atau skala log lebih tepat daripada rata-rata.
- Pendapatan bulanan memuncak pada Agustus (sekitar Rp12,8 miliar), diikuti Desember.
- Korelasi Spearman gabungan harga dan jumlah terjual −0,87, tetapi di dalam tiap produk hanya −0,16 sampai −0,73. Angka gabungan dibesar-besarkan oleh perbedaan skala antarproduk (Simpson's paradox).
- Pendapatan dan jumlah terjual berbeda signifikan antar kategori (Kruskal-Wallis, p < 0,001).

## Struktur file

| File | Fungsi |
|---|---|
| `generate_data.py` | Membangkitkan 1.000 data sintesis |
| `analisis.py` | Analisis statistik detail di terminal |
| `app.py` | Dashboard Streamlit |
| `data_penjualan_sintesis.csv` | Dataset hasil sintesis |
| `hasil_analisis.txt` | Keluaran `analisis.py` |
| `requirements.txt` | Daftar library |

## Cara menjalankan

```bash
pip install -r requirements.txt
python generate_data.py      # opsional, untuk membuat ulang data
python analisis.py           # opsional, analisis di terminal
streamlit run app.py
```

## Teknologi

Python · Pandas · NumPy · SciPy · Plotly · Streamlit
