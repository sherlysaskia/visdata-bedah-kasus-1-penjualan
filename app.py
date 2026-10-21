import pandas as pd, numpy as np, plotly.express as px, plotly.graph_objects as go
import streamlit as st
from scipy import stats

st.set_page_config(page_title="Dashboard Penjualan", page_icon="📊", layout="wide")
rp = lambda x: f"Rp{x:,.0f}".replace(",", ".")
TIPE = {"Produk": "Nominal", "Kategori": "Nominal", "Harga (Rp)": "Rasio (Kontinu)",
        "Jumlah Terjual": "Rasio (Diskrit)", "Tanggal": "Interval"}

@st.cache_data
def load():
    d = pd.read_csv("data_penjualan_sintesis.csv", parse_dates=["Tanggal"])
    d["Pendapatan"] = d["Harga (Rp)"] * d["Jumlah Terjual"]
    d["Bulan"] = d["Tanggal"].dt.to_period("M").dt.to_timestamp()
    return d
df = load()

# ---------- Sidebar filter ----------
st.sidebar.header("🔎 Filter")
kat = st.sidebar.multiselect("Kategori", sorted(df.Kategori.unique()), default=sorted(df.Kategori.unique()))
prod_opts = sorted(df[df.Kategori.isin(kat)].Produk.unique())
prod = st.sidebar.multiselect("Produk", prod_opts, default=prod_opts)
tgl = st.sidebar.date_input("Rentang tanggal", (df.Tanggal.min(), df.Tanggal.max()),
                            min_value=df.Tanggal.min(), max_value=df.Tanggal.max())
f = df[df.Kategori.isin(kat) & df.Produk.isin(prod)]
if len(tgl) == 2:
    f = f[(f.Tanggal >= pd.Timestamp(tgl[0])) & (f.Tanggal <= pd.Timestamp(tgl[1]))]
if f.empty:
    st.warning("Tidak ada data untuk filter ini."); st.stop()

st.title("📊 Dashboard Operasional Penjualan-Sherly Saskia Rani-241051002")
st.caption("Bedah Kasus 1 · Data sintesis 1.000 transaksi (dikembangkan dari 2 baris seed: Laptop & Buku)")

# ---------- KPI ----------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Pendapatan", rp(f.Pendapatan.sum()))
c2.metric("Unit Terjual", f"{f['Jumlah Terjual'].sum():,}".replace(",", "."))
c3.metric("Transaksi", f"{len(f):,}".replace(",", "."))
c4.metric("Median Harga", rp(f["Harga (Rp)"].median()))
c5.metric("Rata² Unit/Transaksi", f"{f['Jumlah Terjual'].mean():.1f}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🏷️ Kategorik (Nominal)", "🔢 Numerik (Rasio)", "📈 Waktu (Interval)", "🔗 Korelasi & Uji", "🗂️ Data"])

# ---------- Tab 1: Nominal -> Bar / Pie ----------
with tab1:
    a, b = st.columns(2)
    k = f.groupby("Kategori", as_index=False).Pendapatan.sum()
    a.plotly_chart(px.pie(k, names="Kategori", values="Pendapatan", hole=.45,
                          title="Kontribusi Pendapatan per Kategori"), width='stretch')
    p = f.groupby("Produk", as_index=False)["Jumlah Terjual"].sum().sort_values("Jumlah Terjual")
    b.plotly_chart(px.bar(p, x="Jumlah Terjual", y="Produk", orientation="h", color="Jumlah Terjual",
                          color_continuous_scale="Blues", title="Unit Terjual per Produk"), width='stretch')
    # Pareto
    pr = f.groupby("Produk").Pendapatan.sum().sort_values(ascending=False)
    cum = pr.cumsum() / pr.sum() * 100
    fig = go.Figure()
    fig.add_bar(x=pr.index, y=pr.values, name="Pendapatan", marker_color="#2a9df4")
    fig.add_scatter(x=pr.index, y=cum.values, name="Kumulatif %", yaxis="y2", mode="lines+markers",
                    line=dict(color="#f39c12"))
    fig.update_layout(title="Pareto Pendapatan Produk (80/20)", yaxis2=dict(overlaying="y", side="right", range=[0, 105]),
                      legend=dict(orientation="h"))
    st.plotly_chart(fig, width='stretch')

# ---------- Tab 2: Numerik ----------
with tab2:
    a, b = st.columns(2)
    logx = a.checkbox("Skala log pada Harga", value=True)
    a.plotly_chart(px.histogram(f, x="Harga (Rp)", nbins=40, log_x=logx, color_discrete_sequence=["#f39c12"],
                                title="Histogram Harga (Kontinu)"), width='stretch')
    b.plotly_chart(px.histogram(f, x="Jumlah Terjual", nbins=30, color_discrete_sequence=["#e67e22"],
                                title="Distribusi Jumlah Terjual (Diskrit)"), width='stretch')
    st.plotly_chart(px.box(f, x="Produk", y="Harga (Rp)", color="Kategori", log_y=True,
                           title="Sebaran Harga per Produk (box plot, skala log)"), width='stretch')
    st.subheader("Statistik Deskriptif")
    d = f[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].describe().T
    d["skewness"] = f[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].skew()
    st.dataframe(d.round(2), width='stretch')

# ---------- Tab 3: Waktu ----------
with tab3:
    gran = st.radio("Granularitas", ["Harian", "Mingguan", "Bulanan"], index=2, horizontal=True)
    rule = {"Harian": "D", "Mingguan": "W", "Bulanan": "MS"}[gran]
    metrik = st.radio("Metrik", ["Pendapatan", "Jumlah Terjual"], horizontal=True)
    t = f.set_index("Tanggal")[metrik].resample(rule).sum().reset_index()
    fig = px.line(t, x="Tanggal", y=metrik, markers=True, title=f"Tren {metrik} ({gran})")
    if len(t) > 3:
        t["MA3"] = t[metrik].rolling(3).mean()
        fig.add_scatter(x=t.Tanggal, y=t.MA3, name="Rata² bergerak 3", line=dict(dash="dash"))
    st.plotly_chart(fig, width='stretch')
    a, b = st.columns(2)
    pk = f.groupby(["Bulan", "Kategori"], as_index=False).Pendapatan.sum()
    a.plotly_chart(px.area(pk, x="Bulan", y="Pendapatan", color="Kategori", title="Pendapatan Bulanan per Kategori"),
                   width='stretch')
    hm = f.assign(Hari=f.Tanggal.dt.day_name(), Bln=f.Tanggal.dt.month).pivot_table(
        index="Hari", columns="Bln", values="Pendapatan", aggfunc="sum").reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    b.plotly_chart(px.imshow(hm, aspect="auto", color_continuous_scale="YlOrRd",
                             title="Heatmap Pendapatan: Hari × Bulan"), width='stretch')

# ---------- Tab 4: Korelasi ----------
with tab4:
    a, b = st.columns(2)
    sc = px.scatter(f, x="Harga (Rp)", y="Jumlah Terjual", color="Produk", log_x=True, opacity=.7,
                    title="Harga vs Jumlah Terjual (skala log harga)")
    a.plotly_chart(sc, width='stretch')
    cm = f[["Harga (Rp)", "Jumlah Terjual", "Pendapatan"]].corr(method="spearman")
    b.plotly_chart(px.imshow(cm.round(2), text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                             title="Korelasi Spearman"), width='stretch')
    if f.Kategori.nunique() > 1:
        h, pv = stats.kruskal(*[g["Pendapatan"].values for _, g in f.groupby("Kategori")])
        st.info(f"**Kruskal-Wallis** Pendapatan antar kategori: H = {h:.1f}, p = {pv:.3g} → "
                f"{'ada perbedaan signifikan' if pv < .05 else 'tidak ada perbedaan signifikan'} (α = 0,05).")
    r, pv = stats.spearmanr(f["Harga (Rp)"], f["Jumlah Terjual"])
    st.info(f"**Spearman** Harga vs Jumlah: ρ = {r:.2f} (p = {pv:.3g}). Korelasi gabungan bisa menyesatkan "
            "karena beda produk punya skala harga berbeda (Simpson's paradox); cek per produk di bawah.")
    per = pd.DataFrame({"Produk": g, "ρ": stats.spearmanr(x["Harga (Rp)"], x["Jumlah Terjual"])[0]}
                       for g, x in f.groupby("Produk") if len(x) > 3)
    if not per.empty:
        st.plotly_chart(px.bar(per.sort_values("ρ"), x="ρ", y="Produk", orientation="h",
                               title="Spearman Harga vs Jumlah per Produk"), width='stretch')

# ---------- Tab 5: Data ----------
with tab5:
    st.markdown("**Tipe data tiap kolom**")
    st.table(pd.DataFrame({"Kolom": TIPE.keys(), "Skala Pengukuran": TIPE.values()}))
    st.dataframe(f.drop(columns="Bulan"), width='stretch', height=350)
    st.download_button("⬇️ Unduh CSV (terfilter)", f.to_csv(index=False).encode(), "penjualan_filtered.csv", "text/csv")
