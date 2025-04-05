# Gabriel Resende Spirlandelli
# 4° DSM

import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

st.set_page_config(layout="wide")
vendas_df = pd.read_excel('./vendas_loja_DSM_ADS.xlsx', decimal=",")
vendas_df['Faturamento'] = vendas_df['Preço do Produto'] * vendas_df['Quantidade']
vendas_df['Data'] = pd.to_datetime(vendas_df['Data'])

def calculos (dados): 
    media = dados.mean()
    moda = dados.mode()
    if moda.empty:
        moda_formatada = "Sem moda"
    elif len(moda) == 1:
        moda_formatada = f"{moda.iloc[0]:.2f}"
    else:
        moda_formatada = ", ".join(moda.astype(str))
    mediana = dados.median()
    q1 = dados.quantile(0.25)
    q2 = dados.quantile(0.50)
    q3 = dados.quantile(0.75)
    desvio_padrao = dados.std()
    assimetria = dados.skew() * 100
    curtose = dados.kurt() * 100
    return {
        "media": f'{media:.2f}',
        "moda": moda_formatada,
        "mediana": f'{mediana:.2f}',
        "q1": f'{q1:.2f}',
        "q2": f'{q2:.2f}',
        "q3": f'{q3:.2f}',
        "desvio_padrao": f'{desvio_padrao:.2f}',
        "assimetria": f'{assimetria:.2f}%',
        "curtose": f'{curtose:.2f}%'
    }
    
def exibeCalculos (dados, titulo):
    valores = calculos(dados)
    st.title(titulo)
    col1, col2, col3 = st.columns(3)
    col1.metric('Media', valores['media'])
    col2.metric('Moda', valores['moda'])
    col3.metric('Mediana', valores['mediana'])
    
    col1a, col2a, col3a = st.columns(3)
    col1a.metric('Quartil 1', valores['q1'])
    col2a.metric('Quartil 2', valores['q2'])
    col3a.metric('Quartil 3', valores['q3'])
    
    
    col1b, col2b, col3b = st.columns(3)
    col1b.metric('Desvio Padrão', valores['desvio_padrao'])
    col2b.metric('Assimetria', valores['assimetria'])
    col3b.metric('Curtose', valores['curtose'])
    
# FILTROS

## FILTRO DE LOJA
lojas = vendas_df['Nome da Loja'].sort_values().unique()
lojas = np.insert(lojas, 0, 'Todas')
lojaSelecionada = st.sidebar.selectbox('Filtrar por loja', lojas)
lojaFiltro =  pd.Series(True, index=vendas_df.index)
if(lojaSelecionada != 'Todas'):
    lojaFiltro = vendas_df['Nome da Loja'] == lojaSelecionada

## FILTRO DE PRODUTO
produtos = vendas_df['Produto'].sort_values().unique()
produtos = np.insert(produtos, 0, 'Todos')
produtoSelecionado = st.sidebar.selectbox('Filtrar por produto', produtos)
produtoFiltro =  pd.Series(True, index=vendas_df.index)
if(produtoSelecionado != 'Todos'):
    produtoFiltro = vendas_df['Produto'] == produtoSelecionado

## FILTRO DE DATA
data_inicial, data_final = st.sidebar.date_input(
    "Selecionar período",
    value=[vendas_df['Data'].min(), vendas_df['Data'].max()],
    format="DD/MM/YYYY"
)
data_inicial = pd.to_datetime(data_inicial)
data_final = pd.to_datetime(data_final)
dataFiltro = (vendas_df['Data'] >= data_inicial) & (vendas_df['Data'] <= data_final)

vendas_filtradas = vendas_df
vendas_filtradas = vendas_filtradas[lojaFiltro & produtoFiltro & dataFiltro]
vendas_filtradas

col1, col2 = st.columns(2)


# GRÁFICOS

venda_por_produtos = vendas_filtradas.groupby('Produto')['Quantidade'].sum().sort_values(ascending=False).reset_index()
fig_venda_por_produtos = px.pie(venda_por_produtos, names='Produto', values='Quantidade', title='Vendas por Produto', hole=0.3)
col1.plotly_chart(fig_venda_por_produtos)

faturamento_por_loja = vendas_filtradas.groupby('Nome da Loja')['Faturamento'].sum().sort_values(ascending=False).reset_index()
fig_faturamento_por_loja = px.bar(faturamento_por_loja, x='Nome da Loja', y='Faturamento', title='Faturamento por loja')
col2.plotly_chart(fig_faturamento_por_loja)

vendas_filtradas['Mes'] = vendas_filtradas['Data'].dt.to_period('M').astype(str)

faturamento_por_mes = (vendas_filtradas.groupby('Mes')['Faturamento'].sum().reset_index())

fig_faturamento_por_mes = px.bar(faturamento_por_mes, x='Mes', y='Faturamento')
st.plotly_chart(fig_faturamento_por_mes)

# CALCULOS
exibeCalculos(vendas_filtradas['Faturamento'], 'Faturamento')
exibeCalculos(vendas_filtradas['Preço do Produto'], 'Preço do Produto')
exibeCalculos(vendas_filtradas['Quantidade'], 'Quantidade Vendida')