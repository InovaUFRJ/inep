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
  is_dollar = False
  if isinstance(money, str):
    is_dollar = any(character in money.lower() for character in 'usdUSD')
    if 'sem repasse' in money.lower(): return 0.0
    money = re.sub(r'[^\d,.-]', '', money)
    if money.count(',') == 1 and money.count('.') == 0:
      money = money.replace(',', '.')
    elif money.count('.') > 1 or (money.count(',') > 0 and money.count('.') > 0):
      money = money.replace('.', '').replace(',', '.')
  try: return float(money) * (5.5 if is_dollar else 1)
  except: return 0.0

def float_to_money(money : float) -> str:
  parts = str(money).split('.')
  result = ''
  for i in range(len(parts[0])):
    if i != 0 and (len(parts[0]) - i) % 3 == 0: result += '.'
    result += parts[0][i]
  result += ',' + parts[1][:2]
  return result