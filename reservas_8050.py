import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("🚤 HotBoat Reservas", 
            style={'color': 'white', 'textAlign': 'center', 'marginTop': '50px'}),
    html.H2("✅ Puerto 8050 Funcionando", 
            style={'color': 'green', 'textAlign': 'center'}),
    html.Div([
        html.A("💰 Utilidad (8055)", href="http://localhost:8055",
               style={'color': 'white', 'margin': '10px', 'padding': '10px', 'border': '1px solid white'}),
        html.A("📈 Marketing (8056)", href="http://localhost:8056",
               style={'color': 'white', 'margin': '10px', 'padding': '10px', 'border': '1px solid white'})
    ], style={'textAlign': 'center', 'marginTop': '30px'})
], style={'backgroundColor': 'black', 'minHeight': '100vh'})

if __name__ == '__main__':
    print("🚤 Iniciando Dashboard Reservas en puerto 8050")
    app.run(debug=False, port=8050) 