import pandas as pd
import streamlit as st
from datetime import date
import utils
from typing import Literal

process_initial_date : date
process_final_date : date
agency_initial_date : date
signed_initial_date : date
agency_final_date : date
signed_final_date : date

center : list[str]
unity : list[str]
contract : list[str]
unique : Literal['first', 'last', 'none', 'all']
money : Literal['free', 'money', 'all']

def apply(dataframe : pd.DataFrame) -> pd.DataFrame:
  get(dataframe)

  df = dataframe.copy()

  df[utils.COLUMN_PROCESS_DATE] = pd.to_datetime(df[utils.COLUMN_PROCESS_DATE], errors='coerce')
  df[utils.COLUMN_ENTERED_AGENCY] = pd.to_datetime(df[utils.COLUMN_ENTERED_AGENCY], errors='coerce')
  df[utils.COLUMN_EXITED_AGENCY] = pd.to_datetime(df[utils.COLUMN_EXITED_AGENCY], errors='coerce')
  df[utils.COLUMN_SIGNED_DATE] = pd.to_datetime(df[utils.COLUMN_SIGNED_DATE], errors='coerce')

  match unique:
    case 'first': df.drop_duplicates(utils.COLUMN_PROCESS, keep='first', inplace=True)
    case 'last': df.drop_duplicates(utils.COLUMN_PROCESS, keep='last', inplace=True)
    case 'all': df.drop_duplicates(utils.COLUMN_PROCESS, keep=False, inplace=True)
  
  match money:
    case 'free': df = df[df[utils.COLUMN_MONEY].apply(utils.clean_money) == 0]
    case 'money': df = df[df[utils.COLUMN_MONEY].apply(utils.clean_money) > 0]

  if center: df = df[df[utils.COLUMN_CENTER].isin(center)]
  if unity: df = df[df[utils.COLUMN_UNITY].isin(unity)]
  if contract: df = df[(df[utils.COLUMN_CONTRACT_TYPE].isin(contract)) & (df[utils.COLUMN_CONTRACT_TYPE] != 0)]

  if process_initial_date < process_final_date: df = df[
    (df[utils.COLUMN_PROCESS_DATE] >= pd.to_datetime(process_initial_date)) &
    (df[utils.COLUMN_PROCESS_DATE] <= pd.to_datetime(process_final_date))
  ]
  if agency_initial_date < agency_final_date: df = df[
    (df[utils.COLUMN_ENTERED_AGENCY] >= pd.to_datetime(agency_initial_date)) &
    (df[utils.COLUMN_EXITED_AGENCY] <= pd.to_datetime(agency_final_date))
  ]
  if signed_initial_date < signed_final_date: df = df[
    (df[utils.COLUMN_SIGNED_DATE] >= pd.to_datetime(signed_initial_date)) &
    (df[utils.COLUMN_SIGNED_DATE] <= pd.to_datetime(signed_final_date))
  ]
    
  return df

def get(dataframe : pd.DataFrame) -> None:
  global process_initial_date
  global process_final_date
  global agency_initial_date
  global signed_initial_date
  global agency_final_date
  global signed_final_date
  global center
  global unity
  global contract
  global unique
  global money

  left, right = st.sidebar.columns(2)

  with left:
    process_initial_date = st.date_input('Início Processo', value=date(2024,1,1), format='DD/MM/YYYY')
    agency_initial_date = st.date_input('Início Tramitação Inova', value = date(2020, 1, 1), format='DD/MM/YYYY')
    signed_initial_date = st.date_input('Início Assinatura', value = date(2024, 12, 31), format='DD/MM/YYYY')

  with right:
    process_final_date = st.date_input('Fim Processo', value=date(2024,12,31), format='DD/MM/YYYY')
    agency_final_date = st.date_input('Fim Tramitação Inova', value = date(2024, 12, 31), format='DD/MM/YYYY')
    signed_final_date = st.date_input('Fim Assinatura', value = date(2020, 1, 1), format='DD/MM/YYYY')
  
  contracts = dataframe[dataframe[utils.COLUMN_CONTRACT_TYPE] != '0'][utils.COLUMN_CONTRACT_TYPE]

  center = st.sidebar.multiselect('Centros', dataframe[utils.COLUMN_CENTER].dropna().unique().tolist())
  unity = st.sidebar.multiselect('Unidades', dataframe[utils.COLUMN_UNITY].dropna().unique().tolist())
  contract = st.sidebar.multiselect('Contratos', contracts.dropna().unique().tolist())

  match st.sidebar.selectbox('Duplicação de Processos', ['Pegar o primeiro', 'Pegar o último', 'Remover todos', 'Manter todos'], 1):
    case 'Pegar o primeiro': unique = 'first'
    case 'Pegar o último': unique =  'last'
    case 'Remover todos': unique = 'all'
    case 'Manter todos': unique = 'none'
  
  money = 'all'
  x =  st.sidebar.multiselect('Contrapartida', ['Sem repasse', 'Com repasse'])
  if 'Sem repasse' in x and 'Com repasse' in x: money = 'all'
  elif 'Sem repasse' in x: money = 'free'
  elif 'Com repasse' in x: money = 'money'
