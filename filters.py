import pandas as pd
import streamlit as st
from datetime import date
import utils

initial_date = date.today()
final_date = date.today()
center : list[str]

def apply(dataframe : pd.DataFrame) -> pd.DataFrame:
  get(dataframe)

  df = dataframe.copy()
  df[utils.COLUMN_PROCESS_DATE] = pd.to_datetime(df[utils.COLUMN_PROCESS_DATE], errors='coerce')

  if center: df = df[df['Centro'].isin(center)]
  if initial_date < final_date: df = df = df[
            (df[utils.COLUMN_PROCESS_DATE] >= pd.to_datetime(initial_date)) &
            (df[utils.COLUMN_PROCESS_DATE] <= pd.to_datetime(final_date))
  ]
  return df

def get(dataframe : pd.DataFrame) -> None:
  global initial_date
  global final_date
  global center

  left, right = st.sidebar.columns(2)

  with left:
    initial_date = st.date_input('Início Data Processo', value=date(2024,1,1), format='DD/MM/YYYY')
  with right:
    final_date = st.date_input('Fim Data Processo', value=date(2024,12,31), format='DD/MM/YYYY')
  
  center = st.sidebar.multiselect('Centros', dataframe['Centro'].dropna().unique().tolist())

