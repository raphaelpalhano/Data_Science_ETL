import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

#titulo
st.title('House Rocket Company')

#parágrafo

@st.cache(allow_output_mutation=True)

def get_data(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date'])
    return data
# load data
data = get_data('C:/TABELAS_DT/kc_house_data.csv')


#filter bedrooms
bedrooms = st.sidebar.multiselect(
    'Number of Bedrooms',
    data['bedrooms'].unique())

try:
    st.write(f'Your filter is: {bedrooms[0]}')
except IndexError:
    st.write("ERROR: Selecione uma opção de quarto!")


st.title("House Rocket Map")
# se a pessoa clicar na caixa retorna true:
is_check = st.checkbox('Display Map')

price_min = int(data['price'].min())
price_max = int(data['price'].max())
price_avg = int(data['price'].mean())

price_slider = st.slider('Price Range',
                         price_min,
                         price_max,
                         price_avg)

if is_check:
    houses = data[data['price'] < price_slider][['id', 'lat', 'long', 'price']]

    # draw map:
    fig = px.scatter_mapbox(houses,
                            lat='lat',
                            lon='long',
                            size='price',
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15,
                            zoom=10)
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(height=600, margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig)

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

#titulo
st.title('House Rocket Company')

#parágrafo

@st.cache(allow_output_mutation=True)

def get_data(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date'])
    return data
# load data
data = get_data('C:/TABELAS_DT/kc_house_data.csv')


#filter bedrooms
bedrooms = st.sidebar.multiselect(
    'Number of Bedrooms',
    data['bedrooms'].unique())

try:
    st.write(f'Your filter is: {bedrooms[0]}')
except IndexError:
    st.write("ERROR: Selecione uma opção de quarto!")


st.title("House Rocket Map")
# se a pessoa clicar na caixa retorna true:
is_check = st.checkbox('Display Map')

price_min = int(data['price'].min())
price_max = int(data['price'].max())
price_avg = int(data['price'].mean())

price_slider = st.slider('Price Range',
                         price_min,
                         price_max,
                         price_avg)

if is_check:
    houses = data[data['price'] < price_slider][['id', 'lat', 'long', 'price']]

    # draw map:
    fig = px.scatter_mapbox(houses,
                            lat='lat',
                            lon='long',
                            size='price',
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15,
                            zoom=10)
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(height=600, margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    st.plotly_chart(fig)

