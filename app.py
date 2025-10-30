import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Cargar los datos
df_vehicles = pd.read_csv('vehicles_us.csv')

# Comenzamos corrigiendo los valores nulos
df_vehicles.fillna({'model_year': 0}, inplace=True)
df_vehicles.fillna({'cylinders': 0}, inplace=True)
df_vehicles.fillna({'odometer': 0}, inplace=True)
df_vehicles.fillna({'paint_color': 'unknown'}, inplace=True)

# Rellenamos los valores nulos de is_4wd con False
df_vehicles.fillna({'is_4wd': 0}, inplace=True)

# cambiamos los tipos de datos de las columnas que lo requieren
df_vehicles['price'] = df_vehicles['price'].astype(float)
df_vehicles['model_year'] = df_vehicles['model_year'].astype(int)
df_vehicles['cylinders'] = df_vehicles['cylinders'].astype(int)
df_vehicles['date_posted'] = pd.to_datetime(df_vehicles['date_posted'])

# cambiamos el tipo de dato de is_4wd a booleano
df_vehicles['is_4wd'] = df_vehicles['is_4wd'].astype(bool)

# separamos la columna model en manufacturer y model_name
df_vehicles['manufacturer'] = df_vehicles['model'].apply(
    lambda x: x.split(' ')[0] if isinstance(x, str) else 'unknown')
df_vehicles['model_name'] = df_vehicles['model'].apply(
    lambda x: ' '.join(x.split(' ')[1:]) if isinstance(x, str) else 'unknown')

# Movemos las columnas de manufacturer y model_name al inicio del dataframe
cols = df_vehicles.columns.tolist()
cols.insert(1, cols.pop(cols.index('manufacturer')))
cols.insert(2, cols.pop(cols.index('model_name')))
df_vehicles = df_vehicles[cols]

# eliminamos la columna model original
df_vehicles.drop(columns=['model'], inplace=True)


''' Interfaz de Streamlit '''
st.title("Proyecto Sprint 7 - Análisis Exploratorio de Datos")
st.write("Análisis exploratorio de datos del conjunto de datos de vehículos en EE.UU.")

st.selectbox("Selecciona un fabricante:",
             options=df_vehicles['manufacturer'].unique(), key='manufacturer_select')
selected_manufacturer = st.session_state['manufacturer_select']
st.selectbox("Selecciona un modelo:",
             options=df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer]['model_name'].unique(), key='model_select')
selected_model = st.session_state['model_select']
st.selectbox("Selecciona un año:",
             options=sorted(df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer][df_vehicles['model_name'] == selected_model]['model_year'].unique()), key='year_select')
selected_year = st.session_state['year_select']
st.selectbox("Selecciona una condicion:",
             options=df_vehicles[df_vehicles['manufacturer'] == selected_manufacturer][df_vehicles['model_name'] == selected_model][df_vehicles['model_year'] == selected_year]['condition'].unique(), key='condition_select')
selected_condition = st.session_state['condition_select']
# filtramos el dataframe
filtered_df = df_vehicles[
    (df_vehicles['manufacturer'] == selected_manufacturer) &
    (df_vehicles['model_name'] == selected_model) &
    (df_vehicles['model_year'] == selected_year) &
    (df_vehicles['condition'] == selected_condition)
]
st.write("Mostrando datos filtrados:")
st.dataframe(filtered_df)
st.write(f"Total de vehículos encontrados: {len(filtered_df)}")
st.write("¡Gracias por usar la aplicación!")
