"""Analisis detail dataset penjualan sintesis."""
import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv("data_penjualan_sintesis.csv", parse_dates=["Tanggal"])
df["Pendapatan"] = df["Harga (Rp)"] * df["Jumlah Terjual"]
df["Bulan"] = df["Tanggal"].dt.to_period("M").astype(str)
rp = lambda x: f"Rp{x:,.0f}".replace(",", ".")

def judul(t): print("\n" + "="*70 + f"\n{t}\n" + "="*70)

judul("1. KUALITAS DATA")
print(df.dtypes, "\nMissing:\n", df.isna().sum(), "\nDuplikat:", df.duplicated().sum())

judul("2. STATISTIK DESKRIPTIF (numerik)")
desc = df[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].describe().T
desc["skewness"] = df[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].skew()
desc["kurtosis"] = df[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].kurt()
print(desc.round(2))

judul("3. KATEGORIK (Nominal): frekuensi & proporsi")
for c in ["Kategori", "Produk"]:
    f = df[c].value_counts(); print(pd.DataFrame({"n": f, "%": (f/len(df)*100).round(1)}), "\n")

judul("4. PENDAPATAN PER KATEGORI & PRODUK")
k = df.groupby("Kategori").agg(transaksi=("Produk","size"), unit=("Jumlah Terjual","sum"),
        pendapatan=("Pendapatan","sum"), harga_rata2=("Harga (Rp)","mean"))
k["kontribusi_%"] = (k.pendapatan/k.pendapatan.sum()*100).round(1)
print(k.sort_values("pendapatan", ascending=False).round(0))
p = df.groupby("Produk")["Pendapatan"].sum().sort_values(ascending=False)
pareto = (p.cumsum()/p.sum()*100).round(1)
print("\nPareto produk (kumulatif %):\n", pareto)

judul("5. TREN WAKTU (Interval)")
m = df.groupby("Bulan").agg(pendapatan=("Pendapatan","sum"), unit=("Jumlah Terjual","sum"))
m["MoM_%"] = (m.pendapatan.pct_change()*100).round(1)
print(m)
print("Bulan puncak:", m.pendapatan.idxmax(), rp(m.pendapatan.max()))
hari = df.groupby(df.Tanggal.dt.day_name())["Pendapatan"].mean().round(0)
print("\nRata-rata pendapatan/transaksi per hari:\n", hari)

judul("6. DISTRIBUSI & NORMALITAS")
for col in ["Harga (Rp)", "Jumlah Terjual"]:
    s, pv = stats.shapiro(df[col].sample(500, random_state=1))
    print(f"{col}: Shapiro p={pv:.4g} -> {'normal' if pv>.05 else 'tidak normal'}; skew={df[col].skew():.2f}")
print("Harga setelah log: skew =", round(np.log(df["Harga (Rp)"]).skew(), 2))

judul("7. KORELASI")
print("Pearson :\n", df[["Harga (Rp)","Jumlah Terjual","Pendapatan"]].corr().round(2))
r, pv = stats.spearmanr(df["Harga (Rp)"], df["Jumlah Terjual"])
print(f"\nSpearman Harga vs Jumlah: rho={r:.2f}, p={pv:.3g}")
# korelasi di dalam produk (menghindari Simpson's paradox)
print("\nSpearman Harga vs Jumlah per produk:")
for prod, g in df.groupby("Produk"):
    print(f"  {prod:12s} rho={stats.spearmanr(g['Harga (Rp)'], g['Jumlah Terjual'])[0]:+.2f}")

judul("8. UJI HIPOTESIS ANTAR KATEGORI")
grp = [g["Jumlah Terjual"].values for _, g in df.groupby("Kategori")]
h, pv = stats.kruskal(*grp); print(f"Kruskal-Wallis Jumlah Terjual ~ Kategori: H={h:.1f}, p={pv:.3g}")
grp = [g["Pendapatan"].values for _, g in df.groupby("Kategori")]
h, pv = stats.kruskal(*grp); print(f"Kruskal-Wallis Pendapatan ~ Kategori   : H={h:.1f}, p={pv:.3g}")

judul("9. OUTLIER (IQR) per produk")
def iqr_out(g):
    q1, q3 = g["Harga (Rp)"].quantile([.25,.75]); i = q3-q1
    return ((g["Harga (Rp)"]<q1-1.5*i)|(g["Harga (Rp)"]>q3+1.5*i)).sum()
print(df.groupby("Produk").apply(iqr_out, include_groups=False).rename("outlier_harga"))

judul("10. INSIGHT OTOMATIS")
print(f"- Total pendapatan {rp(df.Pendapatan.sum())} dari {df['Jumlah Terjual'].sum():,} unit.")
print(f"- Kategori terbesar: {k.pendapatan.idxmax()} ({k['kontribusi_%'].max()}% pendapatan).")
print(f"- {(pareto<=80).sum()+1} produk menyumbang ~80% pendapatan (prinsip Pareto).")
print(f"- Produk paling laris (unit): {df.groupby('Produk')['Jumlah Terjual'].sum().idxmax()}.")
print(f"- Harga miring ke kanan (skew {df['Harga (Rp)'].skew():.2f}) -> gunakan median/log, bukan hanya mean.")
