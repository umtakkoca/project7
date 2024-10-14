import snowflake.connector
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static

# Snowflake bağlantısı
conn = snowflake.connector.connect(
    user='umtakkoca',
    password='Umtcan050699.',  
    account='ov92823.europe-west3.gcp',  
    warehouse='MY_WAREHOUSE', 
    database='MY_DATABASE', 
    schema='PUBLIC'  
)

cur = conn.cursor()

# SQL query to retrieve data
query = "SELECT * FROM auftragsbuch;"
cur.execute(query)
sales = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

# Data preparation
df = sales.copy()
coordinates = pd.read_csv("coordinates.csv")

# Group by postal code (PLZ_K) and city information (STADT_K), then sum the 'SEKUNDEN' column
grouped_df = df.groupby(['PLZ_K', 'STADT_K'])['SEKUNDEN'].sum().reset_index()

# Merge the total 'SEKUNDEN' values with the coordinates data
map_df = pd.merge(coordinates, grouped_df, on='PLZ_K', how='left')

# Convert latitude and longitude columns to float (decimal) type
map_df['lat'] = map_df['lat'].astype(float)
map_df['lon'] = map_df['lon'].astype(float)

# Clean the data for missing lat/lon values
map_df_cleaned = map_df.dropna(subset=['lat', 'lon'])

# Initialize a Folium map centered on Germany
m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

# Add circle markers to the map based on 'SEKUNDEN' values
for idx, row in map_df_cleaned.iterrows():
    sekunden_value = row['SEKUNDEN']
    
    # Set a minimum radius for markers when 'SEKUNDEN' is 0
    if sekunden_value > 0:
        radius_value = min(sekunden_value / 100000, 20)  # Scale radius based on 'SEKUNDEN'
    else:
        radius_value = 2  # Set a small radius when 'SEKUNDEN' is 0
    
    # Add circle markers to the map with a popup containing STADT_K, PLZ_K, and SEKUNDEN
    folium.CircleMarker(
        location=(row['lat'], row['lon']),
        radius=radius_value,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"STADT: {row['STADT_K_x']}, PLZ: {row['PLZ_K']}, SEKUNDEN: {sekunden_value}"
    ).add_to(m)

# Display the map in Streamlit using folium_static
folium_static(m)
