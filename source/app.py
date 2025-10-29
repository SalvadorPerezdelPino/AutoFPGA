from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import os
from dash.exceptions import PreventUpdate

app = Dash()

app.layout = html.Div([
    html.Div(children=[
        html.Label('Arquitectura'),
        dcc.Dropdown(id='architecture-dropdown'),
        html.Br(),
        html.Label('Tipo de experimento'),
        dcc.Dropdown(id='experiment-type-dropdown'),
        html.Br(),
        html.Label('Archivo de experimento'),
        dcc.Dropdown(id='experiment-file-dropdown'),
        html.Br(),
        html.Button('Añadir', id='add-button')

    ], style={'padding': 10, 'flex': 1}),
    html.Div(children=[
        #dcc.Graph(id='box-plot'),
        dcc.Graph(id="sweep-graph")
        #px.box()
    ], style={'padding': 10, 'flex': 1})
], style={
        'display': 'flex',
        'height': '90vh',  # ocupa toda la ventana
        'padding': '10px',
        'gap': '15px'
    })

@callback(
    Output('architecture-dropdown', 'options'),
    Input('architecture-dropdown', 'search_value'))
def update_architecture_options(search_value):
    if not search_value:
        raise PreventUpdate
    
    architectures = os.listdir("../data/")
    return [arch for arch in architectures]

@callback(
    Output('experiment-type-dropdown', 'options'),
    Input('experiment-type-dropdown', 'search_value'),
    State('architecture-dropdown', 'value'))
def update_experiment_type_options(search_value, value):
    if not search_value:
        raise PreventUpdate
    
    experiments = os.listdir(f"../data/{value}/experiments/")
    return [exp for exp in experiments]

@callback(
    Output('experiment-file-dropdown', 'options'),
    Input('experiment-file-dropdown', 'search_value'),
    State('architecture-dropdown', 'value'),
    State('experiment-type-dropdown', 'value'))
def update_experiment_file_options(search_value, value, value2):
    if not search_value:
        raise PreventUpdate
    
    files = os.listdir(f"../data/{value}/experiments/{value2}")
    return [file for file in files]

@callback(
    Output('sweep-graph', 'figure'),
    Input('add-button', 'n_clicks'),
    State('architecture-dropdown', 'value'),
    State('experiment-type-dropdown', 'value'),
    State('experiment-file-dropdown', 'value'),
    State('sweep-graph', 'figure'),
    prevent_initial_call=True)
def update_graph(n_clicks, arch, exp_type, exp_file, fig):
    import plotly.graph_objs as go
    from plotly.graph_objs import Figure

    experiment_path = os.path.join("..", "data", arch, "experiments", exp_type, exp_file)
    file = os.path.join(experiment_path, "average.csv")
    if not os.path.exists(file):
        raise PreventUpdate

    data = pd.read_csv(file, sep=';', decimal=',')
    tmp = px.line(data, x="items", y="execution_time", markers=True)
    new_trace = tmp.data[0]
    new_trace.name = f"{arch}/{exp_type}/{exp_file}"

    # si fig viene vacío o None, devolvemos la figura nueva completa
    if not fig:
        return tmp

    # si fig es dict, convertir a Figure para poder usar add_trace
    if isinstance(fig, dict):
        fig = Figure(fig)

    # evitar duplicados por nombre
    existing_names = {t.name for t in fig.data}
    if new_trace.name in existing_names:
        return fig

    fig.add_trace(new_trace)
    return fig


"""@callback(
    Output('sweep-graph', 'figure'),
    Input('experiment-path', 'value'))
def update_sweep_graph(sweep_path):
    experiment_path = ""
    file = experiment_path + "average.csv"

    data = pd.read_csv(file, sep=';', decimal=',')
    fig = px.line(
        data,
        x = "items",
        y = "execution_time"
    )
    return fig"""

@callback(
    Output('box-plot', 'figure'),
    Input('experiment-path', 'value'))
def update_box_plot(experiment_path):
    # Buscar todos los CSV menos average.csv
    experiment_path = ""
    files = [
        f for f in os.listdir(experiment_path)
        if f.endswith(".csv") and f != "average.csv"
    ]

    # Leerlos y añadir una columna con el nombre del fichero
    dfs = []
    for f in files:
        path = os.path.join(experiment_path, f)
        df = pd.read_csv(path, sep=';', decimal=',')
        df["file"] = f  # nombre del fichero como etiqueta
        dfs.append(df)

    # Combinar todo en un único DataFrame
    data = pd.concat(dfs, ignore_index=True)

    # Crear el boxplot
    fig = px.box(
        data,
        x="file",           # cada fichero = una caja
        y="cycles",          # columna con los datos numéricos
        points="all",       # muestra todos los puntos
        title=f"Distribución de {len(files)} iteraciones"
    )

    fig.update_layout(xaxis_title="Fichero", yaxis_title="Valor")
    return fig

if __name__ == '__main__':
    app.run(debug=True)
    