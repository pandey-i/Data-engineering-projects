import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import datetime
from dotenv import load_dotenv
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Retail Analytics", layout="wide")

# ---------- DB ----------
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM fact_orders", engine)

df = load_data()



# ---------- PREPROCESS ----------
if "order_purchase_timestamp" in df.columns:
    df["order_date"] = pd.to_datetime(df["order_purchase_timestamp"])

# ---------- SIDEBAR ----------
st.sidebar.title("Filters")

customers = st.sidebar.multiselect(
    "Customer",
    df["customer_id"].unique(),
    default=df["customer_id"].unique()[:20]
)

df = df[df["customer_id"].isin(customers)]

# ---------- KPI ----------
total_orders = len(df)
total_customers = df["customer_id"].nunique()

if "total_revenue" in df.columns:
    total_revenue = df["total_revenue"].sum()
    AOV = total_revenue / total_orders if total_orders else 0
else:
    total_revenue, AOV = 0, 0

repeat_customers = df["customer_id"].value_counts()
repeat_rate = (repeat_customers > 1).sum() / total_customers if total_customers else 0

# ---------- TITLE ----------
st.title("📊 Retail Analytics System")

col1, col2, col3, col4 = st.columns(4)

st.subheader("📌 Key Insights")

top_customer = df.groupby("customer_id")["total_revenue"].sum().idxmax()
top_revenue = df.groupby("customer_id")["total_revenue"].sum().max()

st.info(f"Top customer: {top_customer} with revenue ${int(top_revenue)}")

high_value_pct = (df["customer_id"].value_counts() > 1).sum() / df["customer_id"].nunique()

st.info(f"{round(high_value_pct*100,2)}% customers are repeat buyers")

col1.metric("Revenue", f"${int(total_revenue)}")
col2.metric("Orders", total_orders)
col3.metric("AOV", f"${round(AOV,2)}")
col4.metric("Repeat Rate", f"{round(repeat_rate*100,2)}%")

# ---------- TABS ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "👥 Customers",
    "📦 Products",
    "📊 Trends",
    "🧠 Advanced"
])



# =========================
# TAB 1: OVERVIEW
# =========================
with tab1:
    st.subheader("Revenue Distribution")

    fig = px.histogram(df, x="total_revenue", nbins=30, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 2: CUSTOMER ANALYTICS
# =========================
with tab2:
    st.subheader("Top Customers")

    cust_rev = df.groupby("customer_id")["total_revenue"].sum().reset_index()

    top_customers = cust_rev.sort_values(
        by="total_revenue", ascending=False
    ).head(10)

    fig = px.bar(
        top_customers,
        x="customer_id",
        y="total_revenue",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer Segmentation")

    cust_rev["segment"] = cust_rev["total_revenue"].apply(
        lambda x: "High Value" if x > cust_rev["total_revenue"].median() else "Low Value"
    )

    fig2 = px.pie(cust_rev, names="segment")
    st.plotly_chart(fig2)

    # -------- Drill Down --------
    st.subheader("Customer Drill-down")

    selected_customer = st.selectbox(
        "Select Customer",
        df["customer_id"].unique()
    )

    cust_df = df[df["customer_id"] == selected_customer]

    fig3 = px.line(
        cust_df,
        x="order_date",
        y="total_revenue",
        title="Customer Purchase Trend",
        template="plotly_dark"
    )
    st.plotly_chart(fig3)

    st.dataframe(cust_df)

# =========================
# TAB 3: PRODUCT ANALYTICS
# =========================
with tab3:
    if "category" in df.columns:
        st.subheader("Revenue by Category")

        cat_rev = df.groupby("category")["total_revenue"].sum().reset_index()

        fig = px.bar(
            cat_rev,
            x="category",
            y="total_revenue",
            color="total_revenue",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 4: TIME TRENDS
# =========================
with tab4:
    if "order_date" in df.columns:
        st.subheader("Revenue Trend + Forecast")

        trend = df.groupby("order_date")["total_revenue"].sum().reset_index()

        # Forecast (rolling avg)
        trend["forecast"] = trend["total_revenue"].rolling(7).mean()

        fig = px.line(
            trend,
            x="order_date",
            y=["total_revenue", "forecast"],
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

        # -------- ALERT --------
        latest = trend.iloc[-1]["total_revenue"]
        avg = trend["total_revenue"].mean()

        if latest < 0.7 * avg:
            st.error("⚠️ Revenue dropped significantly!")
        else:
            st.success("✅ Revenue stable")

# =========================
# TAB 5: ADVANCED (RFM)
# =========================
with tab5:
    st.subheader("RFM Segmentation")

    today = datetime.datetime.now()

    rfm = df.groupby("customer_id").agg({
        "order_date": lambda x: (today - x.max()).days,
        "customer_id": "count",
        "total_revenue": "sum"
    })

    rfm.columns = ["Recency", "Frequency", "Monetary"]

    rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=[4,3,2,1])
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1,2,3,4])
    rfm["M"] = pd.qcut(rfm["Monetary"], 4, labels=[1,2,3,4])

    rfm["Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)

    fig = px.scatter(
        rfm,
        x="Recency",
        y="Monetary",
        size="Frequency",
        color="Monetary",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(rfm)

# ---------- DOWNLOAD ----------
st.subheader("Download Data")

csv = df.to_csv(index=False)
st.download_button("Download CSV", csv, "data.csv", "text/csv")