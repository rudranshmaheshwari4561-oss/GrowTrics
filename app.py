import pandas as pd
# pyrefly: ignore [missing-import]
import plotly.express as px
import streamlit as st

import theme
import utils as u

st.set_page_config(page_title="GrowTrics | Growth with Analytics", layout="wide")
theme.apply()
theme.hero("GrowTrics",
           "Upload raw sales data. Get insights, a forecast, customer segments and a growth plan.",
           tagline="Growth with Analytics")

# ---- Sidebar Branding ----
st.sidebar.markdown(
    """
    <div style="padding: 4px 0 14px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px;">
      <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #EDE9FE; font-family: 'Space Grotesk', sans-serif;">
        GrowTrics
      </h2>
      <p style="margin: 2px 0 0 0; font-size: 0.82rem; color: #C4B5FD; font-weight: 500;">
        Growth with Analytics
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

file = st.sidebar.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"])
if file is None:
    st.info("Upload a sales file in the sidebar to begin (try data/Superstore.csv).")
    st.stop()

raw = u.load_file(file)
cols = list(raw.columns)

# ---- column mapping ----
st.sidebar.subheader("Map your columns")


def pick(label, keywords, optional=False):
    """Sidebar dropdown with an auto-guessed default."""
    options = (["(none)"] + cols) if optional else cols
    guess = u.guess_column(cols, keywords)
    idx = options.index(guess) if guess in options else 0
    val = st.sidebar.selectbox(label, options, index=idx)
    return None if val == "(none)" else val


c = {
    "date": pick("Date *", ["order date", "date"]),
    "sales": pick("Sales / Revenue *", ["sales", "revenue", "amount", "total"]),
    "order": pick("Order ID", ["order id", "invoice", "order"], True),
    "customer": pick("Customer ID", ["customer id", "customer"], True),
    "product": pick("Product", ["product name", "product", "item"], True),
    "category": pick("Category", ["category"], True),
    "region": pick("Region", ["region", "country", "state"], True),
}
dayfirst = st.sidebar.checkbox("Dates are day-first (DD/MM/YYYY)", value=True)

# ---- clean + analyse ----
df = u.clean_data(raw, c, dayfirst)
if df.empty:
    st.error("No valid rows after cleaning. Check the Date and Sales column mapping.")
    st.stop()

k = u.kpis(df, c)
monthly = u.monthly_sales(df, c)
rfm = u.rfm_segments(df, c) if c["customer"] else None

tabs = st.tabs(["Overview", "Forecast", "Products & Regions",
                "Customers", "Growth Plan", "Data"])

# ---- Overview ----
with tabs[0]:
    a, b, d, e = st.columns(4)
    a.metric("Revenue", f"{k['revenue']:,.0f}")
    b.metric("Orders", f"{k['orders']:,}")
    d.metric("Avg Order Value", f"{k['aov']:,.2f}")
    e.metric("Customers", f"{k['customers']:,}" if k["customers"] else "n/a")
    st.plotly_chart(px.line(monthly, x="month", y="sales", markers=True,
                            title="Monthly Revenue"))

# ---- Forecast ----
with tabs[1]:
    future, r2 = u.forecast(monthly)
    if future is None:
        st.warning("Need at least 6 months of data to forecast.")
    else:
        hist = monthly.assign(type="Actual")
        fut = future.assign(type="Forecast")
        st.plotly_chart(px.line(pd.concat([hist, fut]), x="month", y="sales",
                                color="type", markers=True,
                                title="Next 3 Months Forecast"))
        st.caption(f"Linear Regression trend fit (R² = {r2:.2f}). "
                   "A simple trend-based forecast that ignores seasonality.")
        show = future.assign(month=future["month"].dt.strftime("%b %Y"),
                             sales=future["sales"].round(0))
        st.dataframe(show)

# ---- Products & Regions ----
with tabs[2]:
    left, right = st.columns(2)
    if c["product"]:
        left.plotly_chart(px.bar(u.top_n(df, c["product"], c["sales"]),
                                 x=c["sales"], y=c["product"], orientation="h",
                                 title="Top 10 Products"))
    if c["category"]:
        right.plotly_chart(px.pie(u.top_n(df, c["category"], c["sales"], 20),
                                  names=c["category"], values=c["sales"],
                                  title="Sales by Category"))
    if c["region"]:
        st.plotly_chart(px.bar(u.top_n(df, c["region"], c["sales"], 20),
                               x=c["region"], y=c["sales"], title="Sales by Region"))

# ---- Customers ----
with tabs[3]:
    if rfm is None:
        st.warning("Map a Customer ID column to unlock segmentation.")
    else:
        st.write("Customers grouped by Recency, Frequency and Monetary value (RFM + KMeans).")
        seg = rfm.groupby("segment").agg(customers=("monetary", "size"),
                                         avg_spend=("monetary", "mean"),
                                         avg_orders=("frequency", "mean"),
                                         avg_days_since=("recency", "mean")).round(1)
        st.dataframe(seg)
        st.plotly_chart(px.scatter(rfm, x="frequency", y="monetary", color="segment",
                                   title="Customer Segments"))

# ---- Growth Plan ----
with tabs[4]:
    st.subheader("Data-driven growth plan")
    for tip in u.recommendations(df, c, monthly, rfm):
        st.info(tip)

# ---- Data ----
with tabs[5]:
    st.write(f"Raw rows: {len(raw):,} → Clean rows: {len(df):,}")
    st.dataframe(df.head(100))
    st.download_button("Download cleaned CSV", df.to_csv(index=False), "cleaned_sales.csv")