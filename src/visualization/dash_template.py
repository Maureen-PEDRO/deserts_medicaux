# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

# pydata stack
import pandas as pd

# Mise en place du dashboard + css
app = dash.Dash("Déserts médicaux")
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

# Création de la structure de la page
app.layout = html.Div(children=[
    # Entête de page
    html.H1(children='Déserts médicaux',
            style={'textAlign': 'center'}
           ),
    # Onglets
    dcc.Tabs(id='tabs', children=[
        
        # Onglet visualisation
        dcc.Tab(label='Visualisation', children=[
            html.Div([
                dcc.Input(
                    id='profession-visualisation',
                    placeholder='Choississez une profession',
                    type='text',
                    value='Généraliste'
                ),
                html.Button('Visualiser', id='btn-visualiser'),
            ]),
        ]),

        # Onglet Analyse
        dcc.Tab(label='Analyse', children=[
            html.Div([
                dcc.Input(
                    id='profession-analyse',
                    placeholder='Choississez une profession',
                    type='text',
                    value='Généraliste'
                ),
                html.Button('Analyser', id='btn-analyse'),
            ]),
        ]),
    ]),
])


#############################################
# Interaction Between Components / Controller
#############################################

# Template
#@app.callback(
#    Output(component_id='selector-id', component_property='figure'),
#    [
#        Input(component_id='input-selector-id', component_property='value')
#    ]
#)
#def ctrl_func(input_selection):
#    return None


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )