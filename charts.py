import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime
import utils

def signed_contracts(dataframe: pd.DataFrame) -> None:
  signed, types = st.tabs(['Situação dos Contratos', 'Tipos de Contratos'])

  with signed:
    status_counts = dataframe[utils.COLUMN_SIGNED].value_counts(dropna=False).reset_index()
    status_counts.columns = ['Status', 'Quantidade']
    status_counts['Status'] = status_counts['Status'].map({
      'Sim': 'Assinado',
      'Não': 'Não assinado',
      None: 'Em aberto',
      float('nan'): 'Em aberto',
    })

    st.plotly_chart(px.pie(
      status_counts,
      names='Status',
      values='Quantidade',
      title='Situação dos Contratos',
    ))
  
  with types:
    status_counts = dataframe[utils.COLUMN_CONTRACT_TYPE].value_counts().reset_index()
    status_counts.columns = ['Tipo', 'Quantidade']

    st.plotly_chart(px.pie(
      status_counts,
      names='Tipo',
      values='Quantidade',
      title='Tipos de Contratos',
    ))

def project_values(dataframe : pd.DataFrame) -> None:
  df = dataframe.copy()
  df[utils.COLUMN_MONEY] = df[utils.COLUMN_MONEY].apply(utils.clean_money)

  st.write(f'O valor total dos projetos é de R$ {utils.float_to_money(df[utils.COLUMN_MONEY].sum())}')
  st.write(f'O valor médio dos projetos é de R$ {utils.float_to_money(df[utils.COLUMN_MONEY].mean())}')
  st.write(f'Quantidade de projetos sem repasse {len(df[df[utils.COLUMN_MONEY]==0])}')
  st.plotly_chart(px.histogram(
    df,
    x=utils.COLUMN_MONEY,
    nbins=30,
    title='Valores de Projetos',
    labels={ utils.COLUMN_MONEY: 'Valor (R$)' },
  ).update_layout(bargap=0.1, yaxis_title='Quantidade'))

def life_cicle(dataframe : pd.DataFrame) -> None:
  life, attorney, agency = st.tabs(['Assinaturas', 'Tramitação Procuradoria', 'Tramitação Inova'])

  with life:
    df = dataframe[dataframe[utils.COLUMN_SIGNED] == 'Sim']
    df = df[df[utils.COLUMN_SIGNED_DATE].notna()]

    df[utils.COLUMN_PROCESS_DATE] = pd.to_datetime(df[utils.COLUMN_PROCESS_DATE], errors='coerce')
    df[utils.COLUMN_SIGNED_DATE] = pd.to_datetime(df[utils.COLUMN_SIGNED_DATE], errors='coerce')

    df['Dias Processo'] = (df[utils.COLUMN_SIGNED_DATE] - df[utils.COLUMN_PROCESS_DATE]).dt.days
    df = df[df['Dias Processo'] >= 0]
    
    st.write(f'Existem {len(df)} processos assinados. Leva aproximadamente {df['Dias Processo'].mean():.2f} dias para um processo ser assinado.')
    st.plotly_chart(px.histogram(
      df,
      x='Dias Processo',
      nbins=30,
      title='Tempo para Assinatura do Processo',
    ).update_layout(bargap=0.1, yaxis_title='Frequência'))


  with attorney:
    df = dataframe.copy()

    for col in [utils.COLUMN_ENTERED_ATTORNEY, utils.COLUMN_EXIED_ATTORNEY]:
      df = df[df[col].notna() & (df[col] != "-")]
      df[col] = pd.to_numeric(df[col], errors='coerce')
      df[col] = pd.to_datetime("1899-12-30") + pd.to_timedelta(df[col], unit="D")

    df['Dias na Procuradoria'] = (df[utils.COLUMN_EXIED_ATTORNEY] - df[utils.COLUMN_ENTERED_ATTORNEY]).dt.days

    st.write(f'Existem {len(df)} processos que passaram pela procuradoria. Leva aproximadamente {df['Dias na Procuradoria'].mean():.2f} dias para sair da procuradoria')
    st.plotly_chart(px.histogram(
      df,
      x='Dias na Procuradoria',
      nbins=30,
      title='Dias na Procuradoria',
    ).update_layout(bargap=0.1, yaxis_title='Frequência'))
  
  with agency:
    df = dataframe.copy()
    for col in [utils.COLUMN_EXITED_AGENCY, utils.COLUMN_ENTERED_AGENCY]:
      df = df[df[col].notna()]
      df[col] = pd.to_datetime(df[col], errors='coerce')
    df['Dias na Agência'] = (df[utils.COLUMN_EXITED_AGENCY] - df[utils.COLUMN_ENTERED_AGENCY]).dt.days

    st.write(f'Existem {len(df)} processos que passaram pela Inova. Leva aproximadamente {df['Dias na Agência'].mean():.2f} dias para sair da Inova')
    st.plotly_chart(px.histogram(
      df,
      x='Dias na Agência',
      nbins=30,
      title='Dias na InovaUFRJ',
    ).update_layout(bargap=0.1, yaxis_title='Frequência'))

def organization(dataframe : pd.DataFrame) -> None:
  foreigner, best, cnaes = st.tabs(['Contratos Internacionais', 'Melhores Empresas', 'Melhores CNAEs'])

  df = dataframe[dataframe[utils.COLUMN_ORGANIZATION].notna()]

  with foreigner:
    status_counts = dataframe[utils.COLUMN_CNPJ].dropna().apply(
      lambda x: 'Nacional' if utils.is_cnpj(x) else 'Estrangeiro'
    ).value_counts().reset_index()

    status_counts.columns = ['Empresa', 'Quantidade']

    st.plotly_chart(px.pie(
      status_counts,
      names='Empresa',
      values='Quantidade',
      title='Empresa Estrangeira',
    ))
  
  with best:
    df[utils.COLUMN_ORGANIZATION] = df[utils.COLUMN_ORGANIZATION].str.upper()
    status_counts = df[utils.COLUMN_ORGANIZATION].dropna().value_counts().reset_index().head(10)
    status_counts.columns = [utils.COLUMN_ORGANIZATION, 'Quantidade']

    st.plotly_chart(px.bar(
      status_counts,
      x= utils.COLUMN_ORGANIZATION,
      y='Quantidade',
      title='Top 10 Empresas',
    ))

  with cnaes:
    cnaes_df = utils.read_organizations().copy()

    if st.checkbox('Remover empresas duplicadas', True): df.drop_duplicates(utils.COLUMN_CNPJ, inplace=True)

    cnaes_df['cnpj'] = cnaes_df['cnpj'].astype(str)
    cnaes_df['cnae_1'] = cnaes_df['cnae_1'].apply(lambda x: str(x)[:5] if pd.notna(x) else '')
    cnae_map = dict(zip(cnaes_df['cnpj'], cnaes_df['cnae_1']))
    df[utils.COLUMN_CNPJ] = df[utils.COLUMN_CNPJ].astype(str).apply(lambda x: re.sub(r'[.,/]', '', x)[:8].lstrip('0') if pd.notna(x) else '')
    df['CNAE'] = df[utils.COLUMN_CNPJ].map(cnae_map)
    
    status_counts = df['CNAE'].dropna().value_counts().reset_index()
    status_counts.columns = ['CNAE', 'Quantidade']
    status_counts['CNAE'] = status_counts['CNAE'].astype(str).apply(lambda x: f'CNAE {x}')

    st.plotly_chart(px.bar(
      status_counts,
      x= 'CNAE',
      y='Quantidade',
      title='Principais CNAEs',
    ))
