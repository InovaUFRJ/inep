import streamlit as st
import pandas as pd
import utils, charts, filters

dataframe = utils.read_dataset()
filtered_dataframe = filters.apply(dataframe)

st.title('Contratos e Parcerias UFRJ')
st.dataframe(filtered_dataframe)

charts.signed_contracts(filtered_dataframe)
charts.project_values(filtered_dataframe)
charts.life_cicle(filtered_dataframe)