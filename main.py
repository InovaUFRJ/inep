import streamlit as st
import pandas as pd
import utils, charts, filters

dataframe = utils.read_database()
filtered_dataframe = filters.apply(dataframe)

# st.write(dataframe[utils.COLUMN_MONEY])

st.title('Contratos e Parcerias UFRJ')
st.dataframe(filtered_dataframe)

st.write(f'Existem {len(filtered_dataframe)} processos tramitados de acordo com o filtro selecionado.')
charts.signed_contracts(filtered_dataframe)
charts.project_values(filtered_dataframe)
charts.life_cicle(filtered_dataframe)
charts.organization(filtered_dataframe)