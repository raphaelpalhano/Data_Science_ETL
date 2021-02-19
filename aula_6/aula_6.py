# Packages
import folium
import geopandas
import ipywidgets as widgets
from folium.plugins import MarkerCluster
from matplotlib import pyplot as plt
from ipywidgets import fixed
from matplotlib import gridspec
import pandas as pd
import streamlit as st
import numpy as np
from streamlit_folium import folium_static
import plotly.express as px

# configurando tamanho da página:
st.set_page_config(layout='wide')


#functions

def show_types(data):
    dt = data.dtypes
    st.dataframe(dt)


# show_titles:

def titles_paraph():
    st.title('APP - Analysis DataSet')
    st.markdown('Data Structures')


# extractiona:

@st.cache(allow_output_mutation=True)
def data_collect(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date'])
    return data

@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)
    return geofile

def transform_data(data):
    pd.set_option('display.float.format', lambda x: '%3.f' % x)
    # new columns date:
    data['year'] = pd.to_datetime(data['date']).dt.strftime('%Y')
    data['day'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    data['week'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

    # get price and disivion for sqft = square feet = pés quadrados
    data['price_m2'] = data['price'] / data['sqft_lot']

    # new columns level and dormitory_type
    data['level'] = data['price'].apply(lambda x: 0 if x <= 321950
    else 1 if (x > 321950) & (x <= 450000) else 2 if (x > 450000) & (x <= 645000) else 3)
    data['dormitory_type'] = data['bedrooms'].apply(lambda x: 'studio' if x == 1
    else 'apartament' if x == 2 else 'house')

    return data




def load_process(data, geofile):
    try:
        st.sidebar.title('Region Price')
        filter_Atributtes = st.sidebar.multiselect('Enter Columns', data.columns)
        filter_zip_code = st.sidebar.multiselect('Enter Code', data['zipcode'].unique())
        st.write(filter_zip_code)
        st.write(filter_Atributtes)
        if (filter_zip_code != []) & (filter_Atributtes != []):
            data = data.loc[data['zipcode'].isin(filter_zip_code), filter_Atributtes]
        elif (filter_zip_code != []) & (filter_Atributtes == []):
            data = data.loc[data['zipcode'].isin(filter_zip_code), :]

        elif (filter_zip_code == []) & (filter_Atributtes != []):
            data = data.loc[:, filter_Atributtes]

        else:
            data = data.copy()

        st.dataframe(data.head(100), height=600)

        c1, c2 = st.beta_columns((1, 1))

        df1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
        df2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        df3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
        df4 = data[['price_m2', 'zipcode']].groupby('zipcode').mean().reset_index()

        # merge df
        m1 = pd.merge(df1, df2, on='zipcode', how='inner')
        m2 = pd.merge(m1, df3, on='zipcode', how='inner')
        df = pd.merge(m2, df4, on='zipcode', how='inner')

        df.columns = ['zipcode', 'TOTAL_HOUSES', 'PRICE', 'SQRT_LIVING', 'PRICE/M2']
        c1.header("AVG Values")
        c1.dataframe(df, height=600)

        # selecionando pelos tipos primitivos int, float
        select_atributes = data.select_dtypes(include=['int64', 'float64'])

        # media mediana e desvio padrao STD
        media = pd.DataFrame(select_atributes.apply(np.mean, axis=0))

        # Dataframe com valor mediano
        mediana = pd.DataFrame(select_atributes.apply(np.median))

        # Dataframe com o valor do desvio-padrão
        STD = pd.DataFrame(select_atributes.apply(np.std))

        # Df com valor máximo
        maxim = pd.DataFrame(select_atributes.apply(np.max))

        # Df com valor mínimo dos elementos
        minim = pd.DataFrame(select_atributes.apply(np.min))

        # Criando um ponto de ligação entre os DataFrame
        df1_values = pd.concat([maxim, minim, media, mediana, STD], axis=1).reset_index()

        # nomeando as colunas:
        df1_values.columns = ['attributes', 'maximo', 'minimo', 'media', 'mediana', 'std']

        c2.header("Descripitve Analysis")
        c2.dataframe(df1_values, height=600)

        st.title("Region Overview")
        c1, c2 = st.beta_columns((1, 1))
        c1.header("Portifolio Density")

        #amostra dos dados
        new_data = data.sample(100)
        #mapa vazio (base_map)
        density_map = folium.Map(location=[data['lat'].mean(), data['long'].mean()],
                   default_zoom_start=15)

        #adicionando os pontos dentro do mapa
        marker_cluster = MarkerCluster().add_to(density_map)

        # popup==quando clica aparece um card
        for name, row in new_data.iterrows():
            folium.Marker([row['lat'], row['long']],
                          popup=f'Sold R${row["price"]} on {row["date"]}. Features:  sqft_living: {row["sqft_living"]}, '
                                f'bedrooms: {row["bedrooms"]},  bathrooms: {row["bathrooms"]} year_built: '
                                f'{row["yr_built"]}').add_to(marker_cluster)

        # close_with gerar o map
        # folium_static() == não é uma função do streamlit; from streamlit_folium import folium_static
        with c1:
            folium_static(density_map)

        # Region Map
        c2.header("Price Density")

        # zipcode == CEP
        #filtrando preços por região groupby(zipcode)
        new_data = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()

        #pegando amostra(100)
        new_data = new_data.sample(100, replace=True)

        #renomeando as colunas Zip e price:
        new_data.columns = ['ZIP', 'PRICE']

        #filtrando para fazer relação do dataset com Geofile, para pegar todas as regiões que o Geofile abrange
        file_geo = geofile[geofile['ZIP'].isin(new_data['ZIP'].tolist())]

        #map base
        region_price_map = folium.Map(location=[data['lat'].mean(), data['long'].mean()],
                                 default_zoom_start=15)

        #colorindo e gerando a relação de cores por preco. Key_on== faz um join com os dt e geofile
        #opacity: vai deixar um pouco mais claro ; lengend_name== Uma legenda na parte superior;
        region_price_map.choropleth(data = new_data, geo_data=file_geo, columns=['ZIP', 'PRICE'],
                                    key_on='feature.properties.ZIP', fill_color='YlOrRd', fill_opacity= 0.7,
                                    line_opacity=0.2, legend_name='AVG PRICE')

        with c2:
            folium_static(region_price_map)

        #============== Variação anual e diária dos preços=======================================================
        st.title('Commercial Attributes')
        st.sidebar.title('Commercial Options')

        #Filters
        #.....


        # AVG price Year

        # filtrando por ano
        df2 = data[['price', 'yr_built']].groupby('yr_built').mean().reset_index()

        # configurando o gráfico lateralidade==x e horizontal==y
        fig = px.line(df2, x='yr_built', y='price')

        st.markdown('Per Year')
        # desenhando o gráfico use_container_width == ajustar a largura
        st.plotly_chart(fig, use_container_width=True)

        #AVG price Day
        df2 = data[['price', 'day']].groupby('day').mean().reset_index()
        fig = px.line(df2, x='day', y='price')
        st.markdown('Per Day')
        st.plotly_chart(fig, use_container_width=True)


    except Exception as error:
        st.write(f"Valores diferentes {error}")




if __name__ == '__main__':

    titles_paraph()
    #extraction:
    data = data_collect('C://TABELAS_DT/kc_house_data.csv')
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
    geofile = get_geofile(url)

    #Transform
    dt_transformed = transform_data(data)

    # load:
    load_process(dt_transformed, geofile)
