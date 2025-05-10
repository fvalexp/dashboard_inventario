import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import logging

# Activar logs para depuración
logging.basicConfig(level=logging.DEBUG)

# Cargar y limpiar los datos
try:
    df = pd.read_excel("Listado de piezas por vehiculos.xlsx", engine="openpyxl")
    df = df.iloc[2:].copy()

    df = df.rename(columns={
        'Unnamed: 3': 'Codigo',
        'Unnamed: 7': 'Descripcion',
        'Unnamed: 10': 'Existencia',
        'Unnamed: 11': 'Costo_Unitario_Local',
        'Unnamed: 15': 'Bodega'
    })

    df = df[['Codigo', 'Descripcion', 'Existencia', 'Costo_Unitario_Local', 'Bodega']]
    df = df.dropna(subset=['Codigo', 'Descripcion'])

    df['Existencia'] = pd.to_numeric(df['Existencia'], errors='coerce').fillna(0).astype(int)
    df['Costo_Unitario_Local'] = pd.to_numeric(df['Costo_Unitario_Local'], errors='coerce').fillna(0)

    print("Filas cargadas:", len(df))
    print(df.head())

except Exception as e:
    print("❌ Error al cargar o procesar el archivo Excel:", e)
    df = pd.DataFrame(columns=['Codigo', 'Descripcion', 'Existencia', 'Costo_Unitario_Local', 'Bodega'])

# Crear app de Dash
app = dash.Dash(__name__)
app.title = "Dashboard de Piezas"

# Gráfico solo si hay datos
if not df.empty:
    grouped = df.groupby('Codigo', as_index=False)['Existencia'].sum()
    fig = px.bar(grouped, x='Codigo', y='Existencia', title='Existencias por Código de Parte')
else:
    fig = px.bar(title='Sin datos para mostrar')

# Layout de la app
app.layout = html.Div([
    html.H1("Dashboard de Piezas por Vehículos", style={'textAlign': 'center'}),

    dcc.Graph(figure=fig),

    html.H2("Tabla Detallada", style={'marginTop': 40}),
    dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        filter_action='native',
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    )
])

print("✅ App layout cargado correctamente")

# Ejecutar servidor
if __name__ == '__main__':
    app.run(debug=False)
    



