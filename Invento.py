import dash
from dash import dcc, html, dash_table, Input, Output, State
import pandas as pd
import plotly.express as px

# Cargar y preparar datos
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
df['Valor_Total'] = df['Existencia'] * df['Costo_Unitario_Local']
df['Bodega'] = df['Bodega'].fillna("No especificada").astype(str)

# Crear app Dash
app = dash.Dash(__name__)
app.title = "Dashboard de Piezas"

app.layout = html.Div([
    html.H1("Dashboard de Piezas por Vehículo", style={"textAlign": "center"}),

    html.Div([
        html.Label("Filtrar por Bodega:"),
        dcc.Dropdown(
            options=[{"label": b, "value": b} for b in sorted(df['Bodega'].unique())],
            id='filtro-bodega',
            value=None,
            placeholder="Seleccione una bodega"
        ),
        html.Label("Existencia mayor a (máx: {}):".format(df['Existencia'].max())),
        dcc.Input(
            id='filtro-existencia',
            type='number',
            value=0,
            min=0,
            max=df['Existencia'].max(),
            placeholder='Ingrese cantidad mínima'
        ),
        html.Button("Restablecer Filtros", id='reset-btn', n_clicks=0)
    ], style={"width": "45%", "margin": "auto"}),

    dcc.Graph(id='grafico-valor'),

    html.H2("Tabla de Datos", style={"marginTop": 30}),
    dash_table.DataTable(
        id='tabla-datos',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        filter_action='native',
        sort_action='native',
        export_format='xlsx',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    )
])

@app.callback(
    Output('grafico-valor', 'figure'),
    Output('tabla-datos', 'data'),
    Input('filtro-bodega', 'value'),
    Input('filtro-existencia', 'value'),
    Input('reset-btn', 'n_clicks')
)
def actualizar_dashboard(bodega, existencia_min, n_clicks):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'reset-btn.n_clicks':
        bodega = None
        existencia_min = 0
    filtrado = df.copy()
    if bodega:
        filtrado = filtrado[filtrado['Bodega'] == bodega]
    if existencia_min is not None:
        filtrado = filtrado[filtrado['Existencia'] >= existencia_min]

    fig = px.bar(
        filtrado.groupby('Codigo', as_index=False)['Valor_Total'].sum(),
        x='Codigo', y='Valor_Total',
        title='Valor Total en Inventario por Código'
    )

    return fig, filtrado.to_dict('records')

if __name__ == '__main__':
    app.run(debug=False)
