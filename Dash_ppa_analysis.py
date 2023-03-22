
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import Dash, dcc, html, Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.express as px
import json


path = 'data'


# import ppa parameers data
df_ppa_params = pd.read_excel(f'{path}/PPA Grid search.xlsx')
df_ppa_params = df_ppa_params[df_ppa_params['Run']!='failure'].reset_index(drop=True)
df_ppa_params['Number'] = df_ppa_params['Number'].apply(int)

# import grid search data
sheet_names = ['1','2','4','5','7','8','10','11','13','14','15','16','17','18','19','20','21','22']
list_sheets = []
for sheet in sheet_names:
    list_sheets.append(pd.read_excel(f'{path}/financial_overview_summarized_all.xlsx', sheet_name=sheet))

df_grid_search = pd.concat(list_sheets).reset_index(drop=True)
df_grid_search = df_grid_search.rename(columns={"Unnamed: 1":"design_id"})




# merge grid search and ppa parameters
df_merged = pd.merge(df_ppa_params, df_grid_search, on="Number", suffixes=("_l", "_r"))


df_plot = df_merged[['hydrogen_tank_capacity','electrolyzer_nominal_power','design','irr','Duration (Years)','Volume (%)','Price (€/MWh)']]

dicts_designs = [json.loads(df_plot['design'].unique()[i]) for i in range(len(df_plot['design'].unique()))]


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Grid-search simulations for Solar PPA analysis", style={'textAlign': 'center'})
        ], width=1500)
    ]),
    dcc.Dropdown(
       id="dropdown_design",
       options=[{'label':
                    f"Electrolyzer nominal power = {dicts_designs[i]['electrolyzer_nominal_power']} & Hydrogen tank capacity = {dicts_designs[i]['hydrogen_tank_capacity']}",
                'value':
                    str(dicts_designs[i])} 
                 for i in range(len(df_plot['design'].unique())) ],
       value=str(dicts_designs[0]),
       optionHeight = 30
    ),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='fig_3d')
        ], 
            #width=1500
            style={'width': '60vw', 'height': '70vh'}
        
        ),
    ]),
    html.Br(),
    html.Div(id='my-output'),
   

])

@app.callback(
    #Output(component_id='my-output', component_property='children'),
    Output(component_id='fig_3d', component_property='figure'),
    Input(component_id='dropdown_design', component_property='value')
)


#def update_output_div(dropdown_design):
#    new_output = dropdown_design.replace("'",'"')
#    return f'Output: {new_output}'
def update_3d_graph(dropdown_design):
    new_output = dropdown_design.replace("'",'"')
    df_plot_design = df_plot[df_plot['design']==new_output]
    fig_3d = px.scatter_3d(df_plot_design, x='Volume (%)', y='Duration (Years)', z='irr', color = "Price (€/MWh)", size_max=20)
    return fig_3d

#app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter


if __name__ == "__main__":
    app.run_server(debug=True)