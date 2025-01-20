from dash import Dash, html, dcc, Input, Output, State
import dash  # Import necessário para usar dash.no_update
import pandas as pd

# Carregar os dados
file_path = "caracteristicas_fechaduras.xlsx"
df = pd.read_excel(file_path)

# Certifique-se de que "Modelo" é a primeira coluna
df.rename(columns={df.columns[0]: "Modelo"}, inplace=True)

# Inicializar o app
app = Dash(__name__)

# Layout do aplicativo
app.layout = html.Div(
    style={"display": "flex", "font-family": "'Arial', sans-serif"},
    children=[
        # Menu lateral
        html.Div(
            style={
                "width": "20%",
                "background-color": "#4CAF50",
                "padding": "20px",
                "color": "white",
                "height": "100vh",
                "overflow-y": "auto",
            },
            children=[
                html.H2("Filtros de Características", style={"text-align": "center"}),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    [
                                        html.Span(
                                            f"{coluna}",
                                            style={
                                                "cursor": "pointer",
                                                "font-weight": "bold",
                                                "margin-right": "10px",
                                                "font-size": "16px",
                                            },
                                        ),
                                        html.Span(
                                            "►",
                                            id=f"seta-{coluna}",
                                            style={
                                                "cursor": "pointer",
                                                "font-size": "16px",
                                                "transition": "transform 0.3s",
                                            },
                                        ),
                                    ],
                                    id=f"menu-{coluna}",
                                    style={"margin-bottom": "10px"},
                                ),
                                html.Div(
                                    id=f"submenu-{coluna}",
                                    style={
                                        "display": "none",
                                        "background-color": "#fff",
                                        "color": "#000",
                                        "padding": "10px",
                                        "border-radius": "5px",
                                    },
                                    children=[
                                        dcc.Checklist(
                                            id=f"checklist-{coluna}",
                                            options=[
                                                {"label": str(valor), "value": valor}
                                                for valor in sorted(
                                                    df[coluna].dropna().unique()
                                                )
                                            ],
                                            value=[],
                                            style={"margin-bottom": "10px"},
                                        )
                                    ],
                                ),
                            ]
                        )
                        for coluna in df.columns[1:]
                    ]
                ),
                # Botão para limpar filtros
                html.Button(
                    "Limpar",
                    id="limpar-filtros",
                    style={
                        "margin-top": "20px",
                        "background-color": "#ff4d4d",
                        "color": "white",
                        "border": "none",
                        "padding": "10px",
                        "width": "100%",
                        "border-radius": "5px",
                        "cursor": "pointer",
                    },
                ),
            ],
        ),
        # Conteúdo principal
        html.Div(
            style={
                "width": "80%",
                "padding": "20px",
                "background-color": "#fff",
            },
            children=[
                html.H1("Escolha Sua Fechadura Digital", style={"color": "#4CAF50"}),
                html.P(
                    "Selecione os filtros no menu lateral para encontrar a fechadura ideal.",
                    style={"font-size": "16px", "color": "#555"},
                ),
                html.Div(
                    id="tabela-resultados",
                    children=[],
                ),
            ],
        ),
    ],
)

# Callbacks para alternar visibilidade dos menus
for coluna in df.columns[1:]:
    @app.callback(
        [Output(f"submenu-{coluna}", "style"), Output(f"seta-{coluna}", "children")],
        [Input(f"menu-{coluna}", "n_clicks")],
        [State(f"submenu-{coluna}", "style"), State(f"seta-{coluna}", "children")],
    )
    def toggle_menu(n_clicks, style, seta):
        if not n_clicks:
            return {"display": "none"}, "►"
        if style["display"] == "none":
            return {"display": "block"}, "▼"
        return {"display": "none"}, "►"

# Callback para atualizar a tabela com os filtros
@app.callback(
    Output("tabela-resultados", "children"),
    [Input(f"checklist-{coluna}", "value") for coluna in df.columns[1:]],
)
def atualizar_tabela(*filtros):
    df_filtrado = df.copy()
    colunas_selecionadas = ["Modelo"]  # Sempre incluir a coluna "Modelo"
    for coluna, valores in zip(df.columns[1:], filtros):
        if valores:
            df_filtrado = df_filtrado[df[coluna].isin(valores)]
            colunas_selecionadas.append(coluna)
    
    if df_filtrado.empty:
        return html.P("Nenhum produto corresponde aos critérios selecionados.", style={"color": "red"})
    
    # Exibir somente as colunas selecionadas
    df_filtrado = df_filtrado[colunas_selecionadas]
    return html.Table(
        style={
            "width": "100%",
            "border-collapse": "collapse",
            "margin-top": "20px",
        },
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th(
                            col,
                            style={
                                "border": "1px solid #4CAF50",
                                "padding": "10px",
                                "background-color": "#4CAF50",
                                "color": "white",
                                "text-align": "center",
                            },
                        )
                        for col in df_filtrado.columns
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                str(df_filtrado.iloc[i][col]),
                                style={
                                    "border": "1px solid #4CAF50",
                                    "padding": "10px",
                                    "text-align": "center",
                                    "word-wrap": "break-word",
                                },
                            )
                            for col in df_filtrado.columns
                        ]
                    )
                    for i in range(len(df_filtrado))
                ]
            ),
        ],
    )

# Callback para limpar todos os filtros
@app.callback(
    [Output(f"checklist-{coluna}", "value") for coluna in df.columns[1:]],
    Input("limpar-filtros", "n_clicks"),
)
def limpar_filtros(n_clicks):
    if n_clicks:
        return [[] for _ in range(len(df.columns[1:]))]
    return dash.no_update  # Corrigido para usar dash.no_update


# Rodar o aplicativo
if __name__ == "__main__":
    app.run_server(debug=True)
