
## Introdução

Seatle Houses é uma empresa fictícia do mercado imobiliário - seu modelo de negócio envolve comprar e revender imóveis. Porém, o time de negócios enfrenta um mercado com diversas variáveis que influenciam o preço - a quantidade de dados é grande e levaria muito tempo para fazer o trabalho manualmente.

Portanto, esse projeto tem o objetivo de gerar insights através da análise e manipulação dos dados para auxiliar na tomada de decisão do time de negócios.

## Produto Final

Com o objetivo de encontrar quais imóveis a House Rocket deveria comprar e por qual valor deveriamos comprar, uma vez comprados, em qual momento deveria vendê-los e por qual preço, serão entregues os seguintes produtos:

* Relatório com as sugestões de compra do imóvel com um valor recomendado;

* Relatório com as sugestões de venda do imóvel com um valor recomendado e o melhor momento para a venda;

* Visualização no mapa com os dados de cada imóvel indicado nos relatórios.

## Dados

A base de dados corresponde a imóveis vendidos na região de King County, Seattle, entre 2014 e 2015. Todas as informações estão disponíveis no Kaggle (https://www.kaggle.com/datasets/harlfoxem/housesalesprediction):

| Coluna        | Descrição                                                             |
|---------------|-----------------------------------------------------------------------|
| id            | Identificação do imóvel a cada venda                                  |
| date          | Data da venda                                                         |
| price         | Preço do imóvel                                                       |
| bedrooms      | Quantidade de quartos                                                 |
| bathrooms     | Quantidade de banheiros                                               |
| sqft_living   | Área interna do imóvel                                                |
| sqft_lot      | Área do lote/terreno                                                  |
| floors        | Quantidade de andares                                                 |
| waterfront    | Indicador de vista para o lago da cidade                              |
| view          | Indicador de 0 a 4 avaliando a vista do imóvel                        |
| condition     | Indicador de 1 a 5 avaliando o estado do imóvel                       |
| grade         | Indicador de 1 a 13 avaliando o design e construção do imóvel         |
| sqft_above    | Área acima do nível do solo                                           |
| sqft_basement | Área abaixo do nível do solo                                          |
| yr_built      | Ano de construção do imóvel                                           |
| yr_renovated  | Ano da última reforma do imóvel                                       |
| zipcode       | Equivalente ao CEP                                                    |
| lat           | Latitude                                                              |
| long          | Longitude                                                             |

## Premissas

* As features sqft_living15 e sqft_lot15, que correspondem a área dos imóveis vizinhos, foram desconsideradas nesta análise;

* Imóveis com ano de renovação igual a 0 foram considerados sem reforma;

* Para os id’s repetidos, foi considerada a venda mais recente do imóvel;

* Com relação a outliers só removemos o imóvel com 33 quartos;

## Ferramentas

* Python 3.9

* Jupyter

* VSCode

* Streamlit

* Streamlit Cloud

## Desenvolvimento da Solução

A solução foi dividida em duas etapas: a etapa de compra e a etapa de venda do imóvel. Além disso, considerei como premissa do negócio a sazonalidade de vendas desse segmento de mercado imobiliário.

Para a compra, com os dados tratados e organizados, durante a análise exploratória levantei algumas hipóteses - que serão abordadas no item “Insights”. As hipóteses mais relevantes, como a que se referia à condição do imóvel, foram levadas em consideração para a compra do mesmo.

Para a venda, agrupei os imóveis por região (zipcode) e por sazonalidade (estação do ano) e retornei a mediana do preço. Imóveis com valor acima do valor mediano da região serão vendidos com acréscimo de 10%. Imóveis com valor abaixo do valor mediano da região serão vendidos com acréscimo de 30%. Sendo assim, considerei a melhor época do ano para venda em cada região.



## Insights

* Imóveis com vista para a água são, em média, 212% mais caros do que imóveis sem vista para a água;

* Imóveis com porão são, em média, 28% mais caros do que imóveis sem porão;

* Imóveis térreos são, em média, 30% mais baratos do que imóveis com andar;

* Imóveis com até 2 quartos são, em média, 30% mais baratos do que imóveis com mais quartos;

* Imóveis com até 1 banheiro são, em média, 40% mais baratos do que imóveis com mais banheiros.

## Resultados Financeiros

Considerando todos os insights descritos anteriormente, identifiquei 7.568 oportunidades de compra. E considerando uma espectativa mais realista de que durante o ano sejam negociados cerca de 100 imóveis prevemos um lucro de cerca de 14 milhões de dólares.

## Conclusão e Próximos Passos

Ao considerar os insights, encontramos boas oportunidades de compra e venda para a Seatle Houses. Os imóveis identificados para a compra foram os com preço abaixo da mediana da região e em boas condições, seguindo o modelo de negócio da empresa.

Como próximo passo, atuaria na melhoria do modelo de precificação dos imóveis (que serviria para identificar imóveis subavaliados, bem como o preço justo para sua venda), aplicaria ferramentas da Ciência de Dados como algoritmos de regressão (machine learning) e realizaria pesquisa de mercado para identificar as principais features consideradas pelos clientes.

## App

* https://fabriciobucher-seatle-houses-dashboard-0k90x0.streamlitapp.com/
