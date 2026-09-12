import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Karachi Heat Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("karachi_heat_data_with_predictions.csv")

df = load_data()

st.title("🌡️ Karachi Heatwave Risk & Vulnerability Dashboard")
st.markdown("GeoAI-based tool identifying heat-vulnerable zones in Karachi using satellite data.")

st.sidebar.header("Filters")
category_filter = st.sidebar.multiselect("Heat Vulnerability Category", options=df["HVI_Category"].unique(), default=list(df["HVI_Category"].unique()))
cluster_filter = st.sidebar.multiselect("Heat Zone", options=df["Cluster_Label"].unique(), default=list(df["Cluster_Label"].unique()))

filtered_df = df[df["HVI_Category"].isin(category_filter) & df["Cluster_Label"].isin(cluster_filter)]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg LST", f"{filtered_df['LST_Celsius'].mean():.1f} °C")
col2.metric("Max LST", f"{filtered_df['LST_Celsius'].max():.1f} °C")
col3.metric("Extreme Risk Points", f"{(filtered_df['HVI_Category']=='Extreme').sum()}")
col4.metric("Total Points", f"{len(filtered_df)}")

st.subheader("Interactive Heat Vulnerability Map")
color_map = {"Low": "green", "Medium": "yellow", "High": "orange", "Extreme": "red"}
m = folium.Map(location=[24.9, 67.05], zoom_start=11, tiles="OpenStreetMap")
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=4,
        color=color_map.get(row["HVI_Category"], "gray"),
        fill=True, fill_opacity=0.7,
        popup=f"HVI: {row['HVI']:.2f} ({row['HVI_Category']})<br>LST: {row['LST_Celsius']:.1f}°C"
    ).add_to(m)
st_folium(m, width=1200, height=550)

st.subheader("Key Insight: What Drives Heat in Karachi?")
st.image("feature_importance.png")

st.subheader("Priority Recommendations")
extreme_zones = filtered_df[filtered_df["HVI_Category"] == "Extreme"]
if len(extreme_zones) > 0:
    st.markdown(f"**{len(extreme_zones)} extreme-risk points identified.** Priority actions:\n- Cooling centers\n- Urban tree plantation\n- Cool/reflective roofing\n- Targeted heat-alert messaging")
    st.dataframe(extreme_zones[["Latitude","Longitude","LST_Celsius","NDVI","Population","Cluster_Label"]].sort_values("LST_Celsius", ascending=False).head(20))
else:
    st.info("No extreme-risk points in current filter.")

st.caption("Data: Landsat 8/9, WorldPop, SRTM. Built with Google Earth Engine + Random Forest.")
