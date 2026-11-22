import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


# ---------- 1. LOAD ----------
def load_file(file):
    """Read an uploaded CSV or XLSX file into a DataFrame."""
    if file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(file)
        except UnicodeDecodeError:
            file.seek(0)
            return pd.read_csv(file, encoding="latin-1")
    return pd.read_excel(file)


def guess_column(columns, keywords):
    """Auto-detect a column by trying keywords in priority order."""
    for k in keywords:
        for col in columns:
            if k in col.lower():
                return col
    return None


# ---------- 2. CLEAN ----------
def clean_data(df, c, dayfirst=True):
    """Remove duplicates, fix dates and numbers, drop invalid rows."""
    df = df.drop_duplicates().copy()
    df[c["date"]] = pd.to_datetime(df[c["date"]], errors="coerce", dayfirst=dayfirst)
    df[c["sales"]] = pd.to_numeric(df[c["sales"]], errors="coerce")
    df = df.dropna(subset=[c["date"], c["sales"]])
    df = df[df[c["sales"]] > 0]
    return df


# ---------- 3. KPIs AND AGGREGATIONS ----------
def kpis(df, c):
    """Headline numbers: revenue, orders, average order value, customers."""
    revenue = df[c["sales"]].sum()
    orders = df[c["order"]].nunique() if c["order"] else len(df)
    customers = df[c["customer"]].nunique() if c["customer"] else None
    return {
        "revenue": revenue,
        "orders": orders,
        "aov": revenue / orders,
        "customers": customers,
    }


def monthly_sales(df, c):
    """Total sales per month."""
    m = df.set_index(c["date"]).resample("MS")[c["sales"]].sum().reset_index()
    m.columns = ["month", "sales"]
    return m


def top_n(df, group_col, sales_col, n=10):
    """Top n groups (products, regions...) by total sales."""
    return (df.groupby(group_col)[sales_col].sum()
              .sort_values(ascending=False).head(n).reset_index())


# ---------- 4. ML: FORECAST ----------
def forecast(monthly, n=3):
    """Fit a straight trend line to monthly sales and predict the next n months."""
    if len(monthly) < 6:
        return None, None
    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly["sales"].values
    model = LinearRegression().fit(X, y)
    r2 = model.score(X, y)
    future_X = np.arange(len(monthly), len(monthly) + n).reshape(-1, 1)
    future_dates = pd.date_range(
        monthly["month"].iloc[-1] + pd.offsets.MonthBegin(1), periods=n, freq="MS")
    future = pd.DataFrame({"month": future_dates,
                           "sales": model.predict(future_X)})
    return future, r2


# ---------- 5. ML: RFM + KMEANS ----------
def rfm_segments(df, c):
    """Group customers by Recency, Frequency, Monetary value using KMeans."""
    snapshot = df[c["date"]].max() + pd.Timedelta(days=1)
    freq_col = c["order"] if c["order"] else c["date"]
    freq_func = "nunique" if c["order"] else "count"
    g = df.groupby(c["customer"]).agg(
        recency=(c["date"], lambda x: (snapshot - x.max()).days),
        frequency=(freq_col, freq_func),
        monetary=(c["sales"], "sum"),
    )
    k = min(4, len(g))
    # log + scaling so one huge spender does not dominate the clusters
    X = StandardScaler().fit_transform(np.log1p(g[["recency", "frequency", "monetary"]]))
    g["cluster"] = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)

    # name clusters by average spend (lowest to highest)
    order = g.groupby("cluster")["monetary"].mean().sort_values().index
    names = ["Low Value", "Occasional", "Loyal", "Champions"][4 - k:]
    g["segment"] = g["cluster"].map(dict(zip(order, names)))
    return g.reset_index()


# ---------- 6. RECOMMENDATIONS ----------
def recommendations(df, c, monthly, rfm):
    """Turn the numbers into a plain-English growth plan."""
    tips = []

    # month-over-month trend
    if len(monthly) >= 2 and monthly["sales"].iloc[-2] > 0:
        last, prev = monthly["sales"].iloc[-1], monthly["sales"].iloc[-2]
        change = (last - prev) / prev * 100
        if change < 0:
            tips.append(f"Sales fell {abs(change):.1f}% in the latest month. "
                        "Run a promotion or re-engagement campaign.")
        else:
            tips.append(f"Sales grew {change:.1f}% in the latest month. "
                        "Identify what drove the growth and repeat it.")

    # Pareto (80/20) on products
    if c["product"]:
        rev = df.groupby(c["product"])[c["sales"]].sum().sort_values(ascending=False)
        top = max(1, int(len(rev) * 0.2))
        share = rev.head(top).sum() / rev.sum() * 100
        tips.append(f"The top 20% of products ({top} items) generate {share:.0f}% of revenue. "
                    "Keep them in stock and promote them first.")

    # weakest vs strongest category
    if c["category"]:
        cat = df.groupby(c["category"])[c["sales"]].sum().sort_values()
        tips.append(f"'{cat.index[0]}' is the weakest category. "
                    f"Consider bundling it with '{cat.index[-1]}', the strongest.")

    # weakest region
    if c["region"]:
        reg = df.groupby(c["region"])[c["sales"]].sum().sort_values()
        tips.append(f"'{reg.index[0]}' is the lowest-selling region. "
                    "Test local advertising or offers there.")

    # customer segments
    if rfm is not None:
        champs = rfm[rfm["segment"] == "Champions"]
        share = champs["monetary"].sum() / rfm["monetary"].sum() * 100
        tips.append(f"{len(champs)} Champion customers generate {share:.0f}% of revenue. "
                    "Launch a VIP or loyalty program for them.")
        low = rfm[rfm["segment"] == "Low Value"]
        tips.append(f"{len(low)} customers are Low Value (inactive or low spend). "
                    "Send them win-back discount offers.")
    return tips