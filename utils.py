import streamlit as st
import pandas as pd
import re
from typing import Any

COLUMN_SIGNED = 'Contrato assinado?'
COLUMN_SIGNED_DATE = 'Data de assinatura do contrato'
COLUMN_MONEY = 'Valor do Projeto'
COLUMN_PROCESS_DATE = 'Data Abertura do processo no SEI'
COLUMN_ENTERED_ATTORNEY = 'Entrada na Procuradoria'
COLUMN_EXIED_ATTORNEY = 'Saída da Procuradoria'
COLUMN_ENTERED_AGENCY = 'Data de Entrada AGI'
COLUMN_EXITED_AGENCY = 'Data de Saída AGI'
COLUMN_CONTRACT_TYPE = 'Tipo de Contrato'

@st.cache_resource
def read_dataset() -> pd.DataFrame:
  return pd.read_csv('juridico.csv', sep=';')

def clean_money(money : Any) -> float:
  if isinstance(money, str):
    if 'sem repasse' in money.lower(): return 0.0
    money = re.sub(r'[^\d,.-USDusd$ ]', '', money)
    if money.count(',') == 1 and money.count('.') == 0:
      money = money.replace(',', '.')
    elif money.count('.') > 1 or (money.count(',') > 0 and money.count('.') > 0):
      money = money.replace('.', '').replace(',', '.')
  try: return float(money)
  except: return 0.0