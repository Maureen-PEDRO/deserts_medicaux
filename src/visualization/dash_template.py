# standard library
import os

# dash libs
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# pydata stack
import pandas as pd


# Chemin d'accès
# A adapter car utilisation d'un jeu de test
PROCESSED_DIR = './src/data'
PROCESSED_DIR = '../data'
ANALYSIS_FILENAME = 'analyse.csv'

# Déclaration des constantes
LOCATION_VAR = 'departement'
POPULATION_VAR = 'NBPERSMENFISC15'
PS_COL_LIST = ['ambulance', 'analyse_medicale', 'autre', 'autre_specialiste',
               'chirurgien', 'dentiste', 'generaliste', 'hopital',
               'infirmiers', 'organe', 'radiologiste', 'reeducateur_podologue',]


# Fonctions spécifiques à l'application
def compute_metrics(df):
    """Calcul des métriques de nombre de PS par habitant
    """
    for c in PS_COL_LIST:
        df[c + '_habitant'] = (df[c] * 100_000 / df[POPULATION_VAR]).round(0)
    return df


# Lecture des données résultant du pré-traitement
# On effectue ces opérations ici car souvent il faut avoir les données
# pour initialiser les widgets de l'application
# (exemple : liste de valeur provenant du fichier)
analyse_df = pd.read_csv(os.path.join(PROCESSED_DIR, ANALYSIS_FILENAME),
                         sep=';',
                         dtype={'CODGEO': str, 'codecommuneetablissement': str},
                        )
dept_df = (analyse_df
           .dropna(subset=['CODGEO', 'NBPERSMENFISC15'])
           .assign(departement = lambda df: df.CODGEO.str[:2]) # LOCATION_VAR
           .groupby(LOCATION_VAR)
           [['NBPERSMENFISC15', 'ambulance', 'analyse_medicale', 'autre',
             'autre_specialiste', 'chirurgien', 'dentiste', 'generaliste', 'hopital',
             'infirmiers', 'organe', 'radiologiste', 'reeducateur_podologue',]]
           .sum()
           .pipe(compute_metrics)
          )


# Liste  pour sélecteur de métier
METIERS_LIST = [
    {'label': 'Ambulanciers', 'value': 'ambulance_habitant'},
    {'label': 'Laboratoires d\'analyse', 'value': 'analyse_medicale_habitant'},
    {'label': 'Chirurgiens', 'value': 'chirurgien_habitant'},
    {'label': 'Dentistes', 'value': 'dentiste_habitant'},
    {'label': 'Généralistes', 'value': 'generaliste_habitant'},
    {'label': 'Hopitaux, cliniques', 'value': 'hopital_habitant'},
    {'label': 'Infirmiers', 'value': 'infirmiers_habitant'},
    {'label': 'Dons d\'organe', 'value': 'organe_habitant'},
    {'label': 'Radiologues', 'value': 'radiologiste_habitant'},
    {'label': 'Rééducateurs, podologues', 'value': 'reeducateur_podologue_habitant'},
    {'label': 'Autres spécialistes', 'value': 'autre_specialiste_habitant'},
    {'label': 'Autres', 'value': 'autre_habitant'},
]

TABLE_COLS_LIST = [
    (LOCATION_VAR, 'Département'),
    (POPULATION_VAR, 'Habitants'),
    ('effectifs', 'Effectifs'),
    ('densite', 'Pour 100 000 habitants'),
]


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
                dcc.Dropdown(options=METIERS_LIST, value='generaliste_habitant',
                             id='select-metier'),
                dcc.RadioItems(
                    options=[
                        {'label': 'Top', 'value': 'top'},
                        {'label': 'Flop', 'value': 'flop'},
                    ],
                    value='top',
                    id='radio-metier'),
                dash_table.DataTable(
                    id='metrics-table',
                    columns=[{"name": n, "id": i} for i, n in TABLE_COLS_LIST],
                    #data=recos_df.to_dict("rows"),
                    #columns=[{"name": i, "id": i} for i in df.columns],
                    #data=df.to_dict("rows"),
                    # Style : https://dash.plot.ly/datatable/style
                ),
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


# Fonctions de callback
#
# Attention à la forme particulière due à l'utilisation d'une annotation (@)
# Principe d'écriture :
# @app.callback(
#  Ouput(<identifiant du composant à mettre à jour>),
#  [Input(<idenfiant des entrées nécessitant la mise à jour>), Input()...]
#)
# def(les paramètres sont les valeurs des Input()):
#   ...

@app.callback(
    Output('metrics-table', 'data'),
    [
        Input('radio-metier', 'value'),
        Input('select-metier', 'value'),
    ]
)
def update_table(ordre, metier):
    _cols = [LOCATION_VAR, POPULATION_VAR, metier[:-len('_habitant')], metier]
    print('Metier : {}'.format(metier))
    print('Colonnes : {}'.format(_cols))
    metrics_df = (dept_df
                  .sort_values(by=metier, ascending=(ordre == 'flop'))
                  .head()
                  .reset_index()
                  [_cols]
                  .rename(columns=dict(zip(_cols, [c for c, _ in TABLE_COLS_LIST])))
                 )
    return metrics_df.to_dict('rows')


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
