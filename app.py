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
st.write("Análisis exploratorio del conjunto de datos de vehículos en EE.UU.")

select_all = st.checkbox("Seleccionar todos los vehiculos", value=True)

if not select_all:
    # Selección filtrada

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
else:
    # Mostrar todos los datos
    st.write("Mostrando todos los datos:")
    st.dataframe(df_vehicles)
    st.write(f"Total de vehículos encontrados: {len(df_vehicles)}")

# mostramos algunos graficos basicos
st.subheader("Análisis Gráfico")

# Boton para mostrar los vehiculos disponibles por fabricante
if st.button("Mostrar vehículos disponibles por fabricante"):

    # Vehículos disponibles por fabricante
    fig1 = go.Figure(data=[go.Bar(x=df_vehicles['manufacturer'].value_counts().index,
                                  y=df_vehicles['manufacturer'].value_counts().values)],
                     layout=go.Layout(title='Vehículos disponibles por fabricante',
                                      xaxis_title='Fabricante',
                                      yaxis_title='Cantidad de vehículos'))
    st.plotly_chart(fig1)

# Boton para mostrar los tipos de vehiculo por fabricante
if st.button("Mostrar tipos de vehículo por fabricante"):

    # Tipos de vehículo por fabricante
    fig2 = go.Figure()
    for manufacturer in df_vehicles['manufacturer'].unique():
        type_counts = df_vehicles[df_vehicles['manufacturer']
                                  == manufacturer]['type'].value_counts()
        fig2.add_trace(go.Bar(x=type_counts.index,
                       y=type_counts.values, name=manufacturer))
    fig2.update_layout(title='Tipos de vehículo por fabricante',
                       xaxis_title='Tipo de vehículo',
                       yaxis_title='Cantidad de vehículos',
                       barmode='stack')
    st.plotly_chart(fig2)

# checkbox para comparar la distribucion de precios entre fabricantes
dist_comparison = st.checkbox(
    "Comparar distribución de precios entre fabricantes")

if dist_comparison:
    # selecciona los fabricantes a comparar
    manufacturer1 = st.selectbox("Selecciona el primer fabricante:",
                                 options=df_vehicles['manufacturer'].unique(), key='manuf1_select', index=0)
    manufacturer1_selected = st.session_state['manuf1_select']
    manufacturer2 = st.selectbox("Selecciona el segundo fabricante:",
                                 options=df_vehicles['manufacturer'].unique(), key='manuf2_select', index=1)
    manufacturer2_selected = st.session_state['manuf2_select']

    # Distribución de precios entre fabricantes
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=df_vehicles[df_vehicles['manufacturer'] == manufacturer1_selected]['price'],
                                name=manufacturer1_selected, opacity=0.7))
    fig3.add_trace(go.Histogram(x=df_vehicles[df_vehicles['manufacturer'] == manufacturer2_selected]['price'],
                                name=manufacturer2_selected, opacity=0.7))
    fig3.update_layout(title='Comparación de distribución de precios entre fabricantes',
                       xaxis_title='Precio',
                       yaxis_title='Cantidad de vehículos',
                       barmode='overlay')
    st.plotly_chart(fig3)

# Boton para mostrar la distribucion de precios sin outliers
if st.button("Mostrar distribución de precios sin outliers"):

    # Eliminamos outliers usando el metodo del rango intercuartil
    Q1 = df_vehicles['price'].quantile(0.25)
    Q3 = df_vehicles['price'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_no_outliers = df_vehicles[(df_vehicles['price'] >= lower_bound) &
                                 (df_vehicles['price'] <= upper_bound)]

    # Distribución de precios sin outliers
    fig4 = go.Figure(data=[go.Box(x=df_no_outliers['price'])],
                     layout=go.Layout(title='Distribución de Precios sin Outliers',
                                      xaxis_title='Precio',
                                      yaxis_title='Cantidad de Vehículos'))
    st.plotly_chart(fig4)

# boton para mostrar la distribucion de precios por fabricante sin outliers
if st.button("Mostrar distribución de precios por fabricante sin Outliers"):

    # Distribución de precios por fabricante sin outliers
    fig4b = go.Figure()
    for manufacturer in df_vehicles['manufacturer'].unique():
        df_manufacturer = df_vehicles[df_vehicles['manufacturer']
                                      == manufacturer]
        # Eliminamos outliers usando el metodo del rango intercuartil
        Q1 = df_manufacturer['price'].quantile(0.25)
        Q3 = df_manufacturer['price'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_manufacturer_no_outliers = df_manufacturer[(df_manufacturer['price'] >= lower_bound) &
                                                      (df_manufacturer['price'] <= upper_bound)]
        fig4b.add_trace(go.Box(x=df_manufacturer_no_outliers['price'],
                               name=manufacturer))
    fig4b.update_layout(title='Distribución de Precios por Fabricante sin Outliers',
                        xaxis_title='Precio',
                        yaxis_title='Fabricante')
    st.plotly_chart(fig4b)

# Boton para mostrar el histograma de condicion vs año
if st.button("Mostrar histograma de condición vs año"):

    # Histograma de condicion vs año
    fig5 = go.Figure()
    # Removemos valores de model_year iguales a 0
    df_vehicles_no0 = df_vehicles[df_vehicles['model_year'] != 0]
    for condition in df_vehicles_no0['condition'].unique():
        df_condition = df_vehicles_no0[df_vehicles_no0['condition'] == condition]
        fig5.add_trace(go.Histogram(x=df_condition['model_year'],
                                    name=condition,
                                    autobinx=True, opacity=0.7))
        fig5.update_layout(title='Condicion vs Año ',
                           xaxis_title='Año',
                           yaxis_title='Cantidad de Vehiculos',
                           barmode='overlay')
    # mostramos el grafico
    st.plotly_chart(fig5)

# Boton para mostrar el grafico de dispersion entre odometro y precio
if st.button("Mostrar dispersión entre odómetro y precio"):

    # Gráfico de dispersión entre odómetro y precio
    fig6 = go.Figure(data=go.Scatter(
        x=df_vehicles['odometer'],
        y=df_vehicles['price'],
        mode='markers',
        marker=dict(size=5, color='blue', opacity=0.5)
    ))
    fig6.update_layout(title='Relación entre Odómetro y Precio',
                       xaxis_title='Odómetro',
                       yaxis_title='Precio')
    # mostramos el grafico
    st.plotly_chart(fig6)

# Finalizamos la aplicacion
st.write("¡Gracias por usar la aplicación!")
