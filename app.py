import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Buyer Segmentation Dashboard", layout="wide")
st.title("Buyer Segmentation & Investment Profiling - Real Estate")

df = pd.read_csv("buyers_clustered.csv")

SEGMENTS = ["Apartment Buyers", "Mixed-Use Buyers", "Premium Buyers", "Multi-Unit Buyers"]
COLORS = {"Apartment Buyers": "#0072B2", "Mixed-Use Buyers": "#E69F00",
          "Premium Buyers": "#009E73", "Multi-Unit Buyers": "#CC79A7"}

# ---- Sidebar filters ----
st.sidebar.header("Filters")

countries = sorted(df["country"].unique())
country_sel = st.sidebar.multiselect("Country", countries, default=countries)

regions = sorted(df.loc[df["country"].isin(country_sel), "region"].unique())
region_sel = st.sidebar.multiselect("Region (leave empty for all)", regions)

purposes = sorted(df["acquisition_purpose"].unique())
purpose_sel = st.sidebar.multiselect("Acquisition purpose", purposes, default=purposes)

types = sorted(df["client_type"].unique())
type_sel = st.sidebar.multiselect("Client type", types, default=types)

filtered = df[
    df["country"].isin(country_sel)
    & df["acquisition_purpose"].isin(purpose_sel)
    & df["client_type"].isin(type_sel)
]
if region_sel:
    filtered = filtered[filtered["region"].isin(region_sel)]

if filtered.empty:
    st.warning("No buyers match these filters. Please widen your selection.")
    st.stop()

# ---- KPIs ----
k1, k2, k3, k4 = st.columns(4)
k1.metric("Buyers", f"{len(filtered):,}")
k2.metric("Investment buyers", f"{(filtered['acquisition_purpose'] == 'Investment').mean() * 100:.1f}%")
k3.metric("Avg units bought", f"{filtered['units_bought'].mean():.2f}")
k4.metric("Avg satisfaction", f"{filtered['satisfaction_score'].mean():.2f}")

# ---- Module 1: segmentation overview ----
st.subheader("Buyer segmentation overview")
seg_counts = filtered["segment"].value_counts().reindex(SEGMENTS, fill_value=0).reset_index()
seg_counts.columns = ["Segment", "Buyers"]
fig = px.bar(seg_counts, x="Segment", y="Buyers", color="Segment",
             color_discrete_map=COLORS, text="Buyers")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, width="stretch")

# ---- Module 2: investor behaviour ----
st.subheader("Investor behaviour")
c1, c2 = st.columns(2)

inv = (filtered.assign(is_investment=filtered["acquisition_purpose"].eq("Investment"))
       .groupby("segment")["is_investment"].mean().mul(100)
       .reindex(SEGMENTS).reset_index())
inv.columns = ["Segment", "Investment buyers (%)"]
fig_inv = px.bar(inv, x="Segment", y="Investment buyers (%)", color="Segment",
                 color_discrete_map=COLORS, text_auto=".1f")
fig_inv.update_layout(showlegend=False, title="Share of investment buyers")
c1.plotly_chart(fig_inv, width="stretch")

spend = filtered.groupby("segment")["total_spend"].mean().reindex(SEGMENTS).reset_index()
spend.columns = ["Segment", "Average total spend"]
fig_spend = px.bar(spend, x="Segment", y="Average total spend", color="Segment",
                   color_discrete_map=COLORS, text_auto=",.0f")
fig_spend.update_layout(showlegend=False, title="Average total spend per buyer")
c2.plotly_chart(fig_spend, width="stretch")

# ---- Module 3: segment insights panel ----
st.subheader("Segment insights")
insights = filtered.groupby("segment").agg(
    Buyers=("client_id", "count"),
    Avg_age=("age", "mean"),
    Avg_units=("units_bought", "mean"),
    Avg_unit_price=("avg_price", "mean"),
    Avg_total_spend=("total_spend", "mean"),
    Office_share=("office_share", "mean"),
    Avg_satisfaction=("satisfaction_score", "mean"),
).reindex(SEGMENTS).round(2)
insights["Share_of_buyers_%"] = (insights["Buyers"] / insights["Buyers"].sum() * 100).round(1)
insights = insights.rename(columns=lambda c: c.replace("_", " "))
st.dataframe(insights, width="stretch")
st.caption("Each row summarises one buyer segment for the current filters.")

# ---- Module 4: geographic buyer analysis ----
st.subheader("Geographic buyer analysis")
g1, g2 = st.columns(2)

# Left: segment mix inside each country (each bar adds up to 100%)
geo_country = (filtered.groupby(["country", "segment"]).size()
               .reset_index(name="Buyers"))
geo_country["Share %"] = (geo_country["Buyers"]
                          / geo_country.groupby("country")["Buyers"].transform("sum") * 100)
fig_c = px.bar(geo_country, x="country", y="Share %", color="segment",
               color_discrete_map=COLORS,
               category_orders={"segment": SEGMENTS},
               labels={"country": "Country", "segment": "Segment"})
fig_c.update_layout(title="Segment mix by country (%)", barmode="stack")
g1.plotly_chart(fig_c, width="stretch")

# Right: buyer count per region and segment (heatmap)
# Right: top 10 regions by buyers, split by segment
top_regions = filtered["region"].value_counts().head(10).index
geo_region = (filtered[filtered["region"].isin(top_regions)]
              .groupby(["region", "segment"]).size().reset_index(name="Buyers"))
fig_r = px.bar(geo_region, y="region", x="Buyers", color="segment",
               orientation="h", color_discrete_map=COLORS,
               category_orders={"segment": SEGMENTS},
               labels={"region": "Region", "segment": "Segment"})
fig_r.update_layout(title="Top 10 regions by buyers", yaxis={"categoryorder": "total ascending"})
g2.plotly_chart(fig_r, width="stretch")

# Table: which segment dominates each country
top = (geo_country.sort_values("Buyers", ascending=False)
       .groupby("country").head(1)
       .rename(columns={"segment": "Largest segment"})
       [["country", "Largest segment", "Share %"]]
       .round(1))
st.caption("Largest segment in each country for the current filters:")
st.dataframe(top.set_index("country"), width="stretch")