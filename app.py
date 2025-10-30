import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.title("Proyecto Sprint 7 - Análisis Exploratorio de Datos")
st.write("Análisis exploratorio de datos del conjunto de datos de vehículos en EE.UU.")
# Cargar los datos
df_vehicles = pd.read_csv('vehicles_us.csv')
