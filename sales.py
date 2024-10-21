# SALES DASHBOARD: RADIO 80S80S

########### Librairies ###########

import pandas as pd
import folium
import streamlit as st
from folium import Popup
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import plotly.express as px
import plotly.graph_objs as go

########### CSV reading ###########
df = pd.read_csv('sales_data.csv')  

st.title('Streamlit Application')

# Loading data
st.write(df.head())

st.title("Sales Representatives Contribution to Baget:")

# Convert 'NETTONETTO' column to numeric data type
df['NETTONETTO'] = pd.to_numeric(df['NETTONETTO'], errors='coerce')

# Group by year and media sales representative
contribution = df.groupby(['JAHR', 'MEDIABERATUNG'])['NETTONETTO'].sum().reset_index()

# Get unique years
years = contribution['JAHR'].unique()

fig_data = []

# Create a bar chart for each year
for year in years:
    yearly_data = contribution[contribution['JAHR'] == year]
    top_contributors = yearly_data.nlargest(10, 'NETTONETTO')  # Get the top 10 contributors
    
    # Create a bar graph for each year
    fig_data.append(
        go.Bar(
            x=top_contributors['MEDIABERATUNG'],
            y=top_contributors['NETTONETTO'],
            name=str(year)
        )
    )

# Layout for the chart
layout = go.Layout(
    title="Sales Representatives Contribution to Budget",
    xaxis={'title': 'Sales Representatives'},
    yaxis={'title': 'Net Cash to Register (NETTONETTO)'},
    updatemenus=[{
        'buttons': [
            {'label': str(year), 'method': 'update', 'args': [{'visible': [i == idx for i in range(len(years))]}]}
            for idx, year in enumerate(years)
        ],
        'direction': 'down',
        'showactive': True,
    }],
)

# Create the figure
fig = go.Figure(data=fig_data, layout=layout)

# Display the chart in the Streamlit application
st.plotly_chart(fig)

####################### Top 5 Sales Representatives Changes (2018-2023 ######################################

st.title("Top 5 Sales Representatives Changes (2018-2023):")

# Selecting the sales representative and customer columns
sales_data = df[['MEDIABERATUNG', 'KUNR', 'AUFTRAGSNR', 'JAHR', 'NETTONETTO']]

# Finding the number of new customers each sales representative brought in within the year
unique_customers = sales_data.drop_duplicates(subset=['MEDIABERATUNG', 'KUNR', 'JAHR'])
new_customers_per_rep = unique_customers.groupby(['MEDIABERATUNG', 'JAHR']).size().reset_index(name='New_Customers')

# Finding the number of orders from new customers
new_customer_orders = sales_data[sales_data['KUNR'].isin(unique_customers['KUNR'])]
new_customer_orders_per_rep = new_customer_orders.groupby(['MEDIABERATUNG', 'JAHR']).size().reset_index(name='New_Customer_Orders')

# Total net revenue generated from new customers
new_customer_value = new_customer_orders.groupby(['MEDIABERATUNG', 'JAHR'])['NETTONETTO'].sum().reset_index(name='Total_New_Customer_Value')

# Merging data for each sales rep, including new customers, new customer orders, and total revenue from new customers
sales_rep_analysis = pd.merge(new_customers_per_rep, new_customer_orders_per_rep, on=['MEDIABERATUNG', 'JAHR'])
sales_rep_analysis = pd.merge(sales_rep_analysis, new_customer_value, on=['MEDIABERATUNG', 'JAHR'])

# Sorting sales reps based on customer value generated
sales_rep_analysis = sales_rep_analysis.sort_values(by=['JAHR', 'Total_New_Customer_Value'], ascending=[True, False])

# Creating a table for 2018
sales_rep_2018 = sales_rep_analysis[sales_rep_analysis['JAHR'] == 2018]

# Selecting the top 5 sales representatives
top_5_sales_rep_2018 = sales_rep_2018.head(5)

# Determining rankings for all years
ranking_data = {}
for year in range(2018, 2024):
    yearly_data = sales_rep_analysis[sales_rep_analysis['JAHR'] == year]
    yearly_data = yearly_data.sort_values(by='Total_New_Customer_Value', ascending=False)
    yearly_data['Rank'] = range(1, len(yearly_data) + 1)
    ranking_data[year] = yearly_data[['MEDIABERATUNG', 'Rank']]

# Finding rank changes of the top 5 reps from 2018 across the years
rank_changes = pd.DataFrame({'MEDIABERATUNG': top_5_sales_rep_2018['MEDIABERATUNG']})
for year in range(2018, 2024):
    rank_changes = pd.merge(rank_changes, ranking_data[year], on='MEDIABERATUNG', how='left')
    rank_changes.rename(columns={'Rank': f'Rank_{year}'}, inplace=True)

# Creating the rank change plot using Plotly
fig = go.Figure()
for _, row in rank_changes.iterrows():
    fig.add_trace(go.Scatter(
        x=list(range(2018, 2024)),
        y=row[[f'Rank_{year}' for year in range(2018, 2024)]],
        mode='lines+markers',
        name=row['MEDIABERATUNG']
    ))

fig.update_layout(
    title='Top 5 Sales Representatives Rank Changes (2018-2023)',
    xaxis_title='Year',
    yaxis_title='Rank',
    yaxis=dict(autorange='reversed'),  # Higher ranks (1st place) appear at the top
    xaxis=dict(tickmode='linear', tick0=2018, dtick=1),
    legend_title='Sales Representative',
    template='plotly_white'
)

# Display the Plotly figure in Streamlit
st.plotly_chart(fig)

####################### How many new customers do we generate on average every year? #############################


st.title('How many new customers do we generate on average every year?')

data = df[['KUNDE', 'KUNR', 'JAHR']]

years = sorted(data['JAHR'].unique())

new_customers_per_year = {}

initial_year = years[0]
initial_year_customers = data[data['JAHR'] == initial_year]['KUNDE'].unique()
new_customers_per_year[initial_year] = len(initial_year_customers)


for year in years[1:]:

    current_year_customers = data[data['JAHR'] == year]['KUNDE'].unique()


    previous_customers = data[data['JAHR'] < year]['KUNDE'].unique()

    new_customers = [customer for customer in current_year_customers if customer not in previous_customers]


    new_customers_per_year[year] = len(new_customers)

new_customers_df = pd.DataFrame(list(new_customers_per_year.items()), columns=['Year', 'New_Customers'])
print(new_customers_df)


st.write("how many new customers do we generate on average every year:")
st.dataframe(new_customers_df)

fig = px.bar(new_customers_df, 
             x='Year', 
             y='New_Customers', 
             title='Number of New Customers Acquired Each Year',
             labels={'Year': 'Year', 'New_Customers': 'Number of New Customers'},
             text='New_Customers')

fig.update_traces(texttemplate='%{text}', textposition='outside')
fig.update_layout(xaxis_tickangle=-45)


st.plotly_chart(fig)

####################### Loyalty Score ####################################

# to st the title of the dashboard:
st.title("Active Year Distribution for Customers")

df_sales_dashboard = pd.read_csv('sales_data.csv')

data = df_sales_dashboard[['KUNDE', 'KUNR', 'JAHR', 'AUFTRAGSNR', 'NETTONETTO']]

active_years = data.groupby(['KUNDE', 'KUNR'])['JAHR'].nunique().reset_index(name='Active_Years')

total_bookings = data.groupby(['KUNDE', 'KUNR'])['AUFTRAGSNR'].nunique().reset_index(name='Total_Bookings')

total_revenue = data.groupby(['KUNDE', 'KUNR'])['NETTONETTO'].sum().reset_index(name='Total_Net_Revenue')
customer_metrics = active_years.merge(total_bookings, on=['KUNDE', 'KUNR']).merge(total_revenue, on=['KUNDE', 'KUNR'])

customer_metrics['Loyalty_Score'] = (
    customer_metrics['Active_Years'] * 0.4 +
    customer_metrics['Total_Bookings'] * 0.3 +
    customer_metrics['Total_Net_Revenue'] * 0.3
)

customer_metrics = customer_metrics.sort_values(by='Loyalty_Score', ascending=False)

fig_hist = px.histogram(
    customer_metrics,
    x='Active_Years',
    nbins=6,  
    title='Distribution of Number of Years Customers Have Been Active',
    labels={'Active_Years': 'Number of Years Active'},
    opacity=0.75,
)

fig_hist.update_layout(
    xaxis_title='Number of Years Active',
    yaxis_title='Number of Customers',
    title_font_size=16,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14
)

st.plotly_chart(fig_hist)


########################### Map with Kunde, Nettonetto, and Sekunden ###########################################

# Data preparation
coordinates = pd.read_csv("coordinates.csv")

# Group by postal code (PLZ_K), city information (STADT_K), and customer (KUNDE), then sum the 'SEKUNDEN' column
grouped_df = df.groupby(['PLZ_K', 'STADT_K', 'KUNDE', 'NETTONETTO']).agg({'SEKUNDEN': 'sum'}).reset_index()

# Merge the total 'SEKUNDEN' values with the coordinates data
map_df = pd.merge(coordinates, grouped_df, on='PLZ_K', how='left')

# Convert latitude and longitude columns to float (decimal) type
map_df['lat'] = map_df['lat'].astype(float)
map_df['lon'] = map_df['lon'].astype(float)

# Remove rows with NaN (missing) values for Latitude and Longitude
map_df_cleaned = map_df.dropna(subset=['lat', 'lon'])

# Initialize the Streamlit app and add filter options
st.title("Map with Kunde, Nettonetto, and Sekunden")

# Initialize a Folium map centered on Germany
m = folium.Map(location=[51.1657, 10.4515], zoom_start=6)

# Use MarkerCluster for better performance
marker_cluster = MarkerCluster(maxClusterRadius=30, disableClusteringAtZoom=10).add_to(m)

# Group by city and postal code to collect customer data for each city
city_grouped = map_df_cleaned.groupby(['PLZ_K', 'STADT_K_x'])

# Add circle markers to the map based on customer count for each city
for (plz, city), group in city_grouped:
    lat = group['lat'].iloc[0]
    lon = group['lon'].iloc[0]
    
    # Get the number of unique customers (KUNDE)
    customer_count = group['KUNDE'].nunique()
    
    # Calculate the total 'SEKUNDEN' and 'NETTONETTO' for this city
    total_sekunden = group['SEKUNDEN'].sum()
    total_nettonetto = group['NETTONETTO'].sum()
    
    # Dynamically set the radius based on the number of customers (KUNDE)
    radius_value = min(max(customer_count * 2, 5), 20)  # Scale radius based on customer count
    
    # Create an HTML table for the popup showing KUNDE, NETTONETTO, and SEKUNDEN
    popup_info = "<table><tr><th>KUNDE</th><th>NETTONETTO</th><th>SEKUNDEN</th></tr>"
    displayed_entries = group.groupby('KUNDE').agg({'NETTONETTO': 'sum', 'SEKUNDEN': 'sum'}).reset_index()
    for idx, row in displayed_entries.iterrows():
        popup_info += f"<tr><td>{row['KUNDE']}</td><td>{row['NETTONETTO']}</td><td>{row['SEKUNDEN']}</td></tr>"
    popup_info += "</table>"

    popup = Popup(popup_info, max_width=500)

    # Add a circle marker for each city with the customized popup
    folium.CircleMarker(
        location=(lat, lon),
        radius=radius_value,  # Radius is based on the number of customers
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=popup
    ).add_to(marker_cluster)

# Display the map in Streamlit using st_folium
st_folium(m, width=725, key="map_visualization")

############################ Active Year Distribution for Customers ####################################

# Başlığı ayarla
st.title("Active Year Distribution for Customers")

data = df[['KUNDE', 'KUNR', 'JAHR', 'AUFTRAGSNR', 'NETTONETTO']]

active_years = data.groupby(['KUNDE', 'KUNR'])['JAHR'].nunique().reset_index(name='Active_Years')

total_bookings = data.groupby(['KUNDE', 'KUNR'])['AUFTRAGSNR'].nunique().reset_index(name='Total_Bookings')

total_revenue = data.groupby(['KUNDE', 'KUNR'])['NETTONETTO'].sum().reset_index(name='Total_Net_Revenue')

customer_metrics = active_years.merge(total_bookings, on=['KUNDE', 'KUNR']).merge(total_revenue, on=['KUNDE', 'KUNR'])

customer_metrics['Loyalty_Score'] = (
    customer_metrics['Active_Years'] * 0.4 +
    customer_metrics['Total_Bookings'] * 0.3 +
    customer_metrics['Total_Net_Revenue'] * 0.3
)

customer_metrics = customer_metrics.sort_values(by='Loyalty_Score', ascending=False)

# Histogram grafiğini oluştur
fig_hist = px.histogram(
    customer_metrics,
    x='Active_Years',
    nbins=6,  
    title='Distribution of Number of Years Customers Have Been Active',
    labels={'Active_Years': 'Number of Years Active'},
    opacity=0.75,
)

fig_hist.update_layout(
    xaxis_title='Number of Years Active',
    yaxis_title='Number of Customers',
    title_font_size=16,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14
)

# Grafiği çizdirirken unique bir key ver
st.plotly_chart(fig_hist, key="active_year_histogram")

