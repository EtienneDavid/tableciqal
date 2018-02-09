# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import requests
from pandas.io.json import json_normalize
import re

r = requests.get(
    "https://plateforme.api-agro.fr/api/records/1.0/search/?dataset=tables-ciqual&sort=-origfdcd&facet=origgpfr&rows=3000").json()

df = json_normalize(r['records'])

app = dash.Dash()
app.title = "Table CIQUAL servie par API-AGRO"
available_indicators = []

for i in df.columns:
    m = re.search(r"\d+", i)
    if m != None:
        available_indicators.append(i)
intro = '''
# Table CIQUAL
## Données sur API-AGRO [links](plateforme.api-agro.com)
Ce tableau de bord pernet de visualiser rapidement les groupes d'aliments par rapport  à leur composition. Notamment l'apport en nutriments par rapport à l'apport en énergie. 
'''
app.layout = html.Div([
    dcc.Markdown(intro),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value='fields.energie_n_x_facteur_jones_avec_fibres_kcal_100g'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Log',
                labelStyle={'display': 'inline-block'}
            )
        ],
            style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i}
                         for i in available_indicators],
                value=available_indicators[0]
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Log',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

])


@app.callback(
    dash.dependencies.Output('indicator-graphic', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('yaxis-type', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type):
    data = []
    for i in df['fields.origgpfr'].unique():
        dff = df[df['fields.origgpfr'] == i]
        data.append(go.Scatter(
            x=dff[xaxis_column_name],
            y=dff[yaxis_column_name],
            text=dff['fields.origfdnm'],
            mode='markers',
            name=i,
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        ))

    return {
        'data': data,
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

my_css_url = "https://unpkg.com/normalize.css@5.0.0"
app.css.append_css({
    "external_url": my_css_url
})

if __name__ == '__main__':
    app.run_server(debug=True)
