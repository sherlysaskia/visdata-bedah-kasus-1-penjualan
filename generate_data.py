"""Membangkitkan 1000 data sintesis dari 2 baris seed pada Bedah Kasus 1."""
import numpy as np, pandas as pd

rng = np.random.default_rng(42)

# (produk, kategori, harga_dasar, rata2_terjual, sebaran_harga)
# Baris 1-2 = SEED ASLI dari tugas. Sisanya = ekstensi asumsi agar data variatif.
CATALOG = [
    ("Laptop",      "Elektronik", 8_500_000, 45,  0.18),   # seed
    ("Buku",        "Pendidikan",    75_000, 120, 0.25),   # seed
    ("Smartphone",  "Elektronik", 4_200_000, 60,  0.30),
    ("Headphone",   "Elektronik",   650_000, 85,  0.35),
    ("Monitor",     "Elektronik", 2_300_000, 40,  0.22),
    ("Alat Tulis",  "Pendidikan",    25_000, 300, 0.20),
    ("Tas Sekolah", "Pendidikan",   180_000, 90,  0.25),
    ("Kalkulator",  "Pendidikan",   150_000, 70,  0.20),
    ("Kemeja",      "Fashion",      220_000, 80,  0.30),
    ("Sepatu",      "Fashion",      550_000, 55,  0.35),
]
PROD_W = np.array([.14, .16, .10, .09, .07, .12, .08, .07, .09, .08])
PROD_W = PROD_W / PROD_W.sum()

N = 1000
dates = pd.date_range("2024-01-01", "2024-12-31")
# musiman: lonjakan Jan (tahun baru), Jul-Agu (tahun ajaran), Des (akhir tahun); akhir pekan sedikit naik
month_w = np.array([1.2, .9, .95, .95, 1.0, 1.0, 1.25, 1.3, 1.0, 1.0, 1.1, 1.4])
date_w = np.array([month_w[d.month-1] * (1.15 if d.weekday() >= 5 else 1.0) for d in dates])
date_w /= date_w.sum()

idx = rng.choice(len(CATALOG), size=N, p=PROD_W)
rows = []
for i in idx:
    p, c, base, lam, sd = CATALOG[i]
    d = rng.choice(dates, p=date_w)
    price = base * rng.lognormal(0, sd)                     # harga kontinu, miring kanan
    price = round(price / 500) * 500                        # pembulatan ke Rp500
    mult = month_w[pd.Timestamp(d).month - 1]
    qty = max(1, rng.poisson(lam * mult * (price/base) ** -0.4))  # harga naik -> jumlah turun (elastisitas)
    rows.append((p, c, price, qty, pd.Timestamp(d)))

df = pd.DataFrame(rows, columns=["Produk", "Kategori", "Harga (Rp)", "Jumlah Terjual", "Tanggal"])
# tanam 2 baris seed asli apa adanya
df.loc[0] = ["Laptop", "Elektronik", 8_500_000, 45, pd.Timestamp("2024-01-01")]
df.loc[1] = ["Buku", "Pendidikan", 75_000, 120, pd.Timestamp("2024-01-02")]
df = df.sort_values("Tanggal").reset_index(drop=True)
df.to_csv("data_penjualan_sintesis.csv", index=False)
print(df.head(), "\nBaris:", len(df))
