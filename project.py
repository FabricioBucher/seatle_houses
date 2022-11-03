import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import folium

from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

st.set_page_config(
    page_title='Seatle Houses',
    layout='wide')

@st.cache( allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    data['date'] = pd.to_datetime(data['date']).dt.date
    data = data.loc[data['bedrooms'] != 33].reset_index(drop=True)
    data.drop(columns=['sqft_living15', 'sqft_lot15'], inplace=True)
    data = data.drop_duplicates(subset=['id'], keep='last')

    return data

def introduction(data):

    # Título
    st.markdown("<h1 style='text-align: center; color: darkgreen;'>Projeto - Seatle Houses</h1>",
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c2.image('seatle.jpg')

    # descrição do projeto
    st.write('')
    st.write('Seatle Houses é uma empresa fictícia do mercado imobiliário - \
        seu modelo de negócio envolve comprar e revender imóveis.')
    st.write('Porém, o time de negócios precisa analisar uma grande quantidade\
        de dados para decidir quais imóveis comprar e levaria muito tempo \
        para fazer o trabalho manualmente.')
    st.write('Portanto, esse projeto tem o objetivo de gerar insights \
        através da análise e manipulação dos dados para auxiliar na tomada de decisão do time de negócios.')
    st.write('Para tanto temos as seguintes perguntas a serem respondidas:')
    st.write(':one: Quais são os imóveis que a empresa deveria comprar e por qual preço?')
    st.write(':two: Uma vez a casa comprada, qual o melhor momento para vendê-las e por qual preço?')

    # mostrar dados
    st.header('Dados')
    st.write('Os dados foram obtidos do link: https://www.kaggle.com/datasets/harlfoxem/housesalesprediction')
    st.write('Após a obtenção realizamos um tratamento nos dados, retirando imóveis duplicados e realizando tratamento de outliers.')

    show_data = st.checkbox('Mostrar dados')
    if show_data:
        st.dataframe(data, height=600)
        st.write('Dimensão da tabela:',data.shape)

    # Mostrar legenda
    df = pd.DataFrame({'Coluna':['id', 'date', 'price', 'bedrooms', 'bathrooms','sqft_living','sqft_lot',
                'floors','waterfront','view','condition','grade','sqft_above','sqft_basement',
                'yr_built','yr_renovated','zipcode','lat','long'],
                'Descrição':['Identificação do imóvel a cada venda', 'Data da venda', 'Preço do imóvel',
                'Quantidade de quartos', 'Quantidade de banheiros', 'Área interna do imóvel',
                'Área do lote/terreno','Quantidade de andares','Indicador de vista para o lago da cidade',
                'Indicador de 0 a 4 avaliando a vista do imóvel','Indicador de 1 a 5 avaliando o estado do imóvel',
                'Indicador de 1 a 13 avaliando o design e construção do imóvel','Área acima do nível do solo',
                'Área abaixo do nível do solo','Ano de construção do imóvel','Ano da última reforma do imóvel',
                'Equivalente ao CEP','Latitude','Longitude']})

    show_leg = st.checkbox('Mostrar Legenda')
    if show_leg:
        st.dataframe(df, width=650)

    # premissas
    st.header('Premissas')
    st.write(':arrow_right: As features `sqft_living15` e `sqft_lot15`, \
        que correspondem a área dos imóveis vizinhos, foram desconsideradas nesta análise.')
    st.write(':arrow_right: Imóveis com ano de renovação igual a 0 foram considerados sem reforma.')
    st.write(':arrow_right: Para os ids repetidos, foi considerada a venda mais recente do imóvel.')
    st.write(':arrow_right: Com relação aos outliers só removemos o imóvel com 33 quartos.')

    # Entregas
    st.header('Produto Final')

    st.write('Serão entregues os seguintes produtos:')
    st.write('')
    st.write(':pushpin: Relatório com sugestões de compra de imóveis por um determinado valor.')
    st.write(':pushpin: Relatório com sugestões de venda de imóveis por um determinado valor.')

    return None

def rel_compra(data):
    st.title('Relatório de Compra de imóveis')
    st.write('')
    st.write('Aqui mostraremos os melhores imóveis a serem comprados.')

    st.header('Premissas utilizadas para seleção da compra dos imóveis')
    st.write('')
    st.write(':memo: Tomamos por base o preço mediano das casas em cada região.')
    st.write(':memo: Para selecionar as casas, utilizamos dois critérios:','\n',
                '1. A condição da casa ser maior que 3;','\n',
                '2. A casa estar com o preço menor ou igual a 90% do preço da mediana da região;')

    df = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()
    df.columns = ['zipcode', 'median_price_region']

    data = data.merge(df, how='inner')

    df = data.loc[(data['price'] <= (data['median_price_region']*0.9)) & (data['condition'] >= 3)]

    # Mostrar tabela
    tabela = st.checkbox('Mostrar tabela')
    if tabela:
        st.write('dimensões da tabela:', f'{df.shape[0]} linhas e {df.shape[1]} colunas')
        st.dataframe(df)

    # plotando imóveis no mapa
    st.header('Mostrando os imóveis no mapa')
    
    c1, c2 = st.columns((1,1))

    density_map = folium.Map( location=[ df['lat'].mean(), df['long'].mean() ], default_zoom_start=15)
    
    marker_cluster = MarkerCluster().add_to( density_map )

    for name, row in df.iterrows():
        folium.Marker( [row['lat'], row['long']],popup='Sold $ {0:,.2f} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(
                        row['price'], row['date'], row['sqft_living'],row['bedrooms'],
                        row['bathrooms'],row['yr_built'])).add_to(marker_cluster)

    with c1:
        folium_static( density_map )

    with c2:
        st.subheader('Informações sobre os imóveis:')

        a = df.shape[0]
        b = (df.price.sum())/int(df.shape[0])
        c = (df.median_price_region.sum())/int(df.shape[0])

        st.write(f':pushpin: Temos {a} imóveis alvos para compra.')
        st.write(f':pushpin: Custam em média USD {b:,.2f} por imóvel.')
        st.write(f':pushpin: Possuem valor de venda médio de USD {c:,.2f} por imóvel.')
        st.write(f':pushpin: Ganho bruto médio por imóvel: USD {(c - b):,.2f}. \
                    (Considerando somente o valor de venda mediano por região)')

    return None

def rel_venda(data):
    st.title('Relatório de Venda de imóveis')
    st.write('')
    st.write('Aqui mostraremos os melhores imóveis a serem vendidos.')
    st.write('Primeiro verificaremos se a época do ano inflencia no preço dos imóveis.')
    data['seasons'] = pd.to_datetime(data['date']).dt.month
    data['seasons'] = data['seasons'].map({1: 'winter',
                                           2: 'winter',
                                           3: 'spring',
                                           4: 'spring',
                                           5: 'spring',
                                           6: 'summer',
                                           7: 'summer',
                                           8: 'summer',
                                           9: 'autumm',
                                           10: 'autumm',
                                           11: 'autumm',
                                           12: 'winter'})
    grouped = data[['price', 'seasons']].groupby(by='seasons').mean().reset_index()
    media_preco_inverno = float(grouped.loc[grouped['seasons'] == 'winter', 'price'])
    media_preco_primavera = float(grouped.loc[grouped['seasons'] == 'spring', 'price'])
    c1, c2 = st.columns((1,1))
    fig = px.line(grouped, x='seasons', y='price', title="Média de preços por estações")
    c1.plotly_chart(fig, use_container_width=True)
    c2.subheader('observações:')
    c2.write(f':pushpin:Podemos ver que a primavera e o verão são as melhores épocas para venda de imóveis;')
    c2.write(f':pushpin:Podemos ver que o inverno é a pior época para venda de imóveis;')
    c2.write(f':pushpin:Os preços no inverno são {(100 - media_preco_inverno*100/media_preco_primavera): .2f}% menores que na primavera;')

    st.header('Premissas utilizadas para definição do valor de venda dos imóveis')
    st.write('')
    st.write(':memo: Consideramos somente os imóveis com recomendação de compra.')
    st.write(':memo: Tomamos por base o valor da casa acrescido de 30% para as vendas na primavera e verão.')
    st.write(':memo: Já para o inverno e outono acresceremos o valor do imóvel em apenas 10%.')
    st.write(':memo: Caso o cálculo acima fique menor que o preço mediano da região, o valor de venda será o preço mediano da região.')

    df = data[['zipcode', 'price']].groupby('zipcode').median().reset_index()
    df.columns = ['zipcode', 'median_price_region']

    data = data.merge(df, how='inner')

    df = data.loc[(data['price'] <= (data['median_price_region']*0.9)) & (data['condition'] >= 3)]


    df['sales_price'] = df[['price', 'seasons']].apply(lambda x: x['price'] * 1.3 if x['seasons'] =='spring'
                                                        else x['price'] * 1.3 if x['seasons'] =='summer'
                                                        else x['price']*1.1    
                                                        ,axis=1)
    df['sales_price'] = df[['sales_price', 'median_price_region']].apply(lambda x: x['sales_price'] 
                                                        if x['sales_price'] >= x['median_price_region']
                                                        else x['median_price_region'], axis=1)
    df['profit'] = df['sales_price'] - df['price']
    df['percent_profit'] = df['profit']/df['price']*100
    df = df.sort_values(by=['percent_profit'], ascending=False)

    # Mostrar tabela
    tabela = st.checkbox('Mostrar tabela')
    if tabela:
        st.write('dimensões da tabela:', f'{df.shape[0]} linhas e {df.shape[1]} colunas')
        st.dataframe(df)

    # plotando imóveis no mapa
    st.header('Mostrando os imóveis no mapa')
    
    c1, c2 = st.columns((1,1))

    density_map = folium.Map( location=[ df['lat'].mean(), df['long'].mean() ], default_zoom_start=15)
    
    marker_cluster = MarkerCluster().add_to( density_map )

    for name, row in df.iterrows():
        folium.Marker( [row['lat'], row['long']],popup='Sales price $ {0:,.2f}, and profit {1:,.2f}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(
                        row['sales_price'], row['profit'], row['sqft_living'],row['bedrooms'],
                        row['bathrooms'],row['yr_built'])).add_to(marker_cluster)

    with c1:
        folium_static( density_map )

    with c2:
        st.subheader('Informações sobre os imóveis:')

        a = df.shape[0]
        b = (df.sales_price.sum())/int(df.shape[0])
        c = (df.profit.sum())/int(df.shape[0])

        st.write(f':pushpin: Temos {a} imóveis alvos para venda.')
        st.write(f':pushpin: Possuem valor de venda médio de USD {b:,.2f} por imóvel.')
        st.write(f':pushpin: Com o lucro médio de USD {c:,.2f} por imóvel.')

    return None

def insights(data):
    st.title('Insights')
    st.write('')
    st.write('Aqui mostraremos alguns insigths que tivemos ao analisar o Dataset.')

    c1, c2 = st.columns((1,1))

    with c1:
        st.subheader('Hipótese 1: Imóveis com vista para água são em média mais caros')

        df = data[['price', 'waterfront']].groupby('waterfront').mean().reset_index()
        fig = px.bar(df, x='waterfront', y='price', title='Média de preços por tipo de vista')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader('Conclusões Hipótese 1:')
        st.write('')
        a = df.loc[df.waterfront==0,'price'].values[0]
        b = df.loc[df.waterfront==1,'price'].values[0]
        st.write('Realmente imóveis com vista para água são em média mais caros')
        st.write(f':pushpin: A média de preços para imóveis sem vista para água é de USD {a:,.2f}')
        st.write(f':pushpin: A média de preços para imóveis com vista para água é de USD {b:,.2f}')
        st.write(f':pushpin: Isto representa um aumento de {(b/a-1):.0%} para imóveis com vista para água.')

    c1, c2 = st.columns((1,1))

    with c1:
        st.subheader('Hipótese 2: Imóveis com porão são em média mais caros')

        data['basement'] = data['sqft_basement'].apply(lambda x: 0 if x == 0 else 1)
        df = data[['price', 'basement']].groupby('basement').mean().reset_index()
        fig = px.bar(df, x='basement', y='price', title='Média de preços de imóveis sem porão e com porão')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader('Conclusões Hipótese 2:')
        st.write('')
        a = df.loc[df.basement==0,'price'].values[0]
        b = df.loc[df.basement==1,'price'].values[0]
        st.write('Realmente imóveis com porão são em média mais caros')
        st.write(f':pushpin: A média de preços para imóveis sem porão é de USD {a:,.2f}')
        st.write(f':pushpin: A média de preços para imóveis com porão é de USD {b:,.2f}')
        st.write(f':pushpin: Isto representa um aumento de {(b/a-1):.0%} para imóveis com porão.')
        
    c1, c2 = st.columns((1,1))

    with c1:
        st.subheader('Hipótese 3: Imóveis térreos são em média mais baratos')

        data['ground'] = data['floors'].apply(lambda x: 1 if x <= 1 else 0)
        df = data[['price', 'ground']].groupby('ground').mean().reset_index()
        fig = px.bar(df, x='ground', y='price', title='Média de preços de imóveis térreos')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader('Conclusões Hipótese 3:')
        st.write('')
        a = df.loc[df.ground==0,'price'].values[0]
        b = df.loc[df.ground==1,'price'].values[0]
        st.write('Realmente imóveis térreos são em média mais baratos')
        st.write(f':pushpin: A média de preços para imóveis com andares é de USD {a:,.2f}')
        st.write(f':pushpin: A média de preços para imóveis térreos é de USD {b:,.2f}')
        st.write(f':pushpin: Isto representa uma diminuição de {(1-b/a):.0%} para imóveis térreos.')

    c1, c2 = st.columns((1,1))

    with c1:
        st.subheader('Hipótese 4: Imóveis com até 2 quartos são em média mais baratos')

        data['twobedrooms'] = data['bedrooms'].apply(lambda x: 1 if x <= 2 else 0)
        df = data[['price', 'twobedrooms']].groupby('twobedrooms').mean().reset_index()
        fig = px.bar(df, x='twobedrooms', y='price', title='Média de preços de imóveis com até dois quartos')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader('Conclusões Hipótese 4:')
        st.write('')
        a = df.loc[df.twobedrooms==0,'price'].values[0]
        b = df.loc[df.twobedrooms==1,'price'].values[0]
        st.write('Realmente imóveis com até dois quartos são em média mais baratos')
        st.write(f':pushpin: A média de preços para imóveis com mais de dois quartos é de USD {a:,.2f}')
        st.write(f':pushpin: A média de preços para imóveis com até dois quartos é de USD {b:,.2f}')
        st.write(f':pushpin: Isto representa uma diminuição de {(1-b/a):.0%} para imóveis com até dois quartos.')

    c1, c2 = st.columns((1,1))

    with c1:
        st.subheader('Hipótese 5: Imóveis com até 1 banheiro são em média mais baratos')

        data['onebath'] = data['bathrooms'].apply(lambda x: 1 if x <= 1 else 0)
        df = data[['price', 'onebath']].groupby('onebath').mean().reset_index()
        fig = px.bar(df, x='onebath', y='price', title='Média de preços de imóveis com até 1 banheiro')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader('Conclusões Hipótese 5:')
        st.write('')
        a = df.loc[df.onebath==0,'price'].values[0]
        b = df.loc[df.onebath==1,'price'].values[0]
        st.write('Realmente imóveis com porão são em média mais caros')
        st.write(f':pushpin: A média de preços para imóveis com mais de 1 banheiro é de USD {a:,.2f}')
        st.write(f':pushpin: A média de preços para imóveis com até 1 banheiro é de USD {b:,.2f}')
        st.write(f':pushpin: Isto representa uma diminuição de {(1-b/a):.0%} para imóveis com até 1 banheiro.')
    return None

def conclusion(data):
    st.title('Conclusão')
    st.write('')
    st.write('Após analisarmos os relatórios apresentados, foram identificados cerca de 7.568 imóveis\
         com potencial de compra, a um custo médio de cerca de 368 mil dólares.')
    st.write('Com relação as vendas destes imóveis, identificamos que podem ser vendidos a um preço\
         médio de 509 mil dólares.')
    st.write('Caso a equipe consiga comprar e vender cerca de 100 imóveis durante um ano,\
         estimamos que será necessário:')
    st.write(':pushpin: Um investimento de cerca de 51 milhões de dólares;')
    st.write(':pushpin: Teremos um retorno esperado de cerca de 14 milhões de dólares, ou seja, 27,45% sobre o valor investido;')

    return None





if __name__ == '__main__':

    # Barra Lateral
    page = st.sidebar.selectbox("Selecione uma página", 
                        ['Introdução', 'Relatório - Compra', 'Relatório - Venda', 'Insights', 'Conclusão'])
    
    # carregar dados
    path = 'kc_house_data.csv'
    data = get_data(path)

    if page == 'Introdução':
        introduction(data)
    elif page == 'Relatório - Compra':
        rel_compra(data)
    elif page == 'Relatório - Venda':
        rel_venda(data)
    elif page == 'Insights':
        insights(data)
    elif page == 'Conclusão':
        conclusion(data)
    else:
        introduction(data)
