from operator import ge
from re import T
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import folium
import geopandas
from datetime import datetime

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(layout='wide')

# Read data
@st.cache( allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date'])

    return data

@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url )

    return geofile

# load data
path = 'kc_house_data.csv'
data = get_data(path)

# get goefile
url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
geofile = get_geofile( url )

# add new features
data['price_sqft'] = data['price'] / data['sqft_lot']

st.title('Seatle Houses Overview')

# filter
f_attributes = st.sidebar.multiselect( 'Enter Columns', data.columns)
f_zipcode = st.sidebar.multiselect('Enter Zipcode', data['zipcode'].unique())

if (f_attributes != []) & (f_zipcode != []):
    data = data.loc[ data['zipcode'].isin(f_zipcode), f_attributes ]

elif (f_attributes == []) & (f_zipcode != []):
    data = data.loc[ data['zipcode'].isin(f_zipcode), : ]

elif (f_attributes != []) & (f_zipcode == []):
    data = data.loc[ :, f_attributes ]

else:
    data = data.copy()


st.dataframe(data, height=300)

c1, c2 = st.columns((1,1))
# Average Metrics
df1 = data[['id','zipcode']].groupby('zipcode').count().reset_index()
df2 = data[['price','zipcode']].groupby('zipcode').mean().reset_index()
df3 = data[['sqft_living','zipcode']].groupby('zipcode').mean().reset_index()
df4 = data[['price_sqft','zipcode']].groupby('zipcode').mean().reset_index()

# merge
n1 = pd.merge( df1, df2, on='zipcode', how='inner' )
n2 = pd.merge( n1, df3, on='zipcode', how='inner' )
df = pd.merge( n2, df4, on='zipcode', how='inner' )
df.columns = ['ZIPCODE', 'TOTAL HOUSES', 'PRICE', 'SQFT LIVING','PRICE/SQFT']


c1.header('Average Values')
c1.dataframe(df, height=300)

# Statistic Descriptive
df1 = data.describe().T.reset_index()
df1.drop(columns=['count', '25%', '75%'], inplace=True)
df1.columns = ['ATTRIBUTES','MEAN', 'STD', 'MIN', 'MEDIAN', 'MAX']
df1 = df1[['ATTRIBUTES', 'MAX', 'MIN', 'MEAN', 'MEDIAN', 'STD']]

c2.header('Statistic Descriptive')
c2.dataframe(df1, height=300)

# Portifolio density map
st.title('Region Overview')

c1, c2 = st.columns((1,1))
c1.header('Portifolio Density')

# df = data.copy()
df = data.sample(10)

#Base map - Folium
density_map = folium.Map( location=[ data['lat'].mean(), data['long'].mean() ],
            default_zoom_start=15
)

marker_cluster = MarkerCluster().add_to( density_map )

for name, row in df.iterrows():
    folium.Marker( [row['lat'], row['long']],
                    popup='Sold R$ {0} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(
                        row['price'], row['date'], row['sqft_living'],row['bedrooms'],
                        row['bathrooms'],row['yr_built'])).add_to(marker_cluster)

with c1:
    folium_static( density_map )

region_price_map = folium.Map( location=[ data['lat'].mean(), data['long'].mean() ],
            default_zoom_start=15
)

# Region Price Map
c2.header('Price Density')

df = data[['price','zipcode']].groupby('zipcode').mean().reset_index()
df.columns = ['ZIP', 'PRICE']

geofile = geofile[ geofile['ZIP'].isin( df['ZIP'].tolist())]

region_price_map = folium.Map( location= [ data['lat'].mean(), data['long'].mean()], 
                                default_zoom_start=15 )

region_price_map.choropleth( data=df,
                            geo_data= geofile,
                            columns=['ZIP', 'PRICE'],
                            key_on='feature.properties.ZIP',
                            fill_color='YlOrRd',
                            fill_opacity = 0.7,
                            line_opacity = 0.2,
                            legend_name='AVG PRICE')


with c2:
    folium_static( region_price_map )

# Distribuíção de imóveis por categorias comerciais

st.sidebar.title('Commercial Options')
st.title('Commercial Attributes')

# average price per year

data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

#filters
min_year_built = int(data['yr_built'].min())
max_year_built = int(data['yr_built'].max())

st.sidebar.subheader('Select Max Year Built')
f_year_built = st.sidebar.slider('Year Built', min_year_built, 
                max_year_built, max_year_built)

st.header('Average Price per Year Built')

# data selection
df = data.loc[data['yr_built'] <= f_year_built]
df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

# plot
fig = px.line(df, x='yr_built', y='price')
st.plotly_chart( fig, use_container_width=True)


# average price per day
st.header('Average Price per Year Built')
st.sidebar.subheader('Select Max Date')

# filters
min_date = datetime.strptime(data['date'].min(),'%Y-%m-%d')
max_date = datetime.strptime(data['date'].max(),'%Y-%m-%d')

f_date = st.sidebar.slider('Date', min_date, max_date, max_date)

# data filtering
data['date'] = pd.to_datetime(data['date'])
df = data.loc[data['date'] <= f_date]
df = df[['date', 'price']].groupby('date').mean().reset_index()

fig = px.line(df, x='date', y='price')
st.plotly_chart( fig, use_container_width=True)

# Histogram
st.header('Price Distribution')
st.sidebar.subheader('Select Max price')

# filters
min_price = int(data['price'].min())
max_price = int(data['price'].max())
avg_price = int(data['price'].mean())

# data filtering
f_price = st.sidebar.slider('Price', min_price, max_price, avg_price)
df = data.loc[data['price'] <= f_price]

fig = px.histogram(df, x='price', nbins=50 )
st.plotly_chart( fig, use_container_width=True)

# Distribuição dos imoveis por categorias físicas
st.header('Attributes Options')
st.sidebar.subheader('House Attributes')

# filters
f_bedrooms = st.sidebar.selectbox('Max number of bedrooms',
                                  sorted(set(data['bedrooms'].unique())))
f_bathrooms = st.sidebar.selectbox('Max number of bathrooms',
                                  sorted(set(data['bathrooms'].unique())))
f_floors = st.sidebar.selectbox('Max number of floors',
                                  sorted(set(data['floors'].unique())))
f_waterview = st.sidebar.checkbox('Only houses with Water View')

c1, c2 = st.columns((1,1))

# House per bedrooms
c1.header('Houses per bedrooms')
df = data[ data['bedrooms'] <= f_bedrooms ]
fig = px.histogram(df, x='bedrooms', nbins=19 )
c1.plotly_chart( fig, use_container_width=True)

# House per bathrooms
c2.header('Houses per bathrooms')
df = data[ data['bathrooms'] <= f_bathrooms ]
fig = px.histogram(df, x='bathrooms', nbins=19 )
c2.plotly_chart( fig, use_container_width=True)

c1, c2 = st.columns((1,1))

# House per floors
c1.header('Houses per floor')
df = data[ data['floors'] <= f_floors ]
fig = px.histogram(df, x='floors', nbins=19 )
c1.plotly_chart( fig, use_container_width=True)

# House per water view
if f_waterview:
    df = data[ data['waterfront'] == 1 ]
    
else:
    df = data.copy()

c2.header('Water Front Houses')
fig = px.histogram(df, x='waterfront', nbins=10)
c2.plotly_chart( fig, use_container_width=True)






