# Import required libraries
from dash import no_update
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash.dependencies import Input, Output, State
from dash import html
from dash import dcc
import dash
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# Create a dash application
app = JupyterDash(__name__)
JupyterDash.infer_jupyter_proxy_config()

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Reading the data and narrowing it down
# https://www.kaggle.com/datasets/jameslko/gun-violence-data?select=gun-violence-data_01-2013_03-2018.csv
gun = pd.read_csv('gun_violence_data.csv')
gun_data = gun[['incident_id', 'date', 'state',
                'n_killed', 'n_injured', 'latitude', 'longitude']]

# Putting day and month and changing date to datetime
gun_data['date'] = pd.to_datetime(gun_data['date'])
gun_data['day'] = gun_data['date'].dt.day_name()
gun_data['month'] = gun_data['date'].dt.month
gun_data['year'] = gun_data['date'].dt.year

# year list
year_list = [i for i in range(2013, 2019, 1)]

us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

gun_data['state_code'] = gun_data['state'].map(
    lambda x: us_state_to_abbrev.get(x, x))

"""Compute graph data for report on killed people

Function that takes gun data as input and create 2 dataframes based on the grouping condition to be used for plottling charts and grphs.

Argument:
     
    df: Filtered dataframe
    
Returns:
   Dataframes to create graph. 
"""


def compute_data_choice_1(df):
    # bar chart of top 5 states with kills
    state_bar_kill = df.groupby(['state_code', 'state'])['n_killed'].mean(
    ).reset_index().sort_values(by='n_killed', ascending=False).head()
    # map of violent incidents by state
    map_count_kill = df.groupby(['state_code', 'state'])['n_killed'].sum(
    ).reset_index().sort_values(by='n_killed', ascending=False)
    return state_bar_kill, map_count_kill


"""Compute graph data for report on injured people

Function that takes gun data as input and create 2 dataframes based on the grouping condition to be used for plottling charts and grphs.

Argument:
     
    df: Filtered dataframe
    
Returns:
   Dataframes to create graph. 
"""


def compute_data_choice_2(df):
    # bar chart of top 5 states with injuries
    state_bar_injury = df.groupby(['state_code', 'state'])['n_injured'].mean(
    ).reset_index().sort_values(by='n_injured', ascending=False).head()
    # map of violent incidents by state
    map_count_injury = df.groupby(['state_code', 'state'])['n_injured'].sum(
    ).reset_index().sort_values(by='n_injured', ascending=False)
    return state_bar_injury, map_count_injury


app.layout = html.Div(children=[
    html.Div([
        html.H1("Gun Violence in USA"),
        html.P("Dashboard of gun violence incidents by states"),
        html.Img(src="assets/no_gun_violence.jpg"),
        html.Label("Fatalities or Injuries", className='dropdown-labels'),
        dcc.Dropdown(id='input-type', className='dropdown',
                     options=[
                        {'label': 'Yearly Killing Report', 'value': 'OPT1'},
                        {'label': 'Yearly Injury Report', 'value': 'OPT2'}],
                     placeholder='Select a report type'),
        html.Label("Year", className='dropdown-labels'),
        dcc.Dropdown(id='input-year', className='dropdown',
                     # Update dropdown values using list comphrehension
                     options=[{'label': i, 'value': i} for i in year_list],
                     placeholder="Select a year"),
        html.Button(id='update-button', children="Update", n_clicks=0)
    ], id='left-container'),
    html.Div([
        html.Div([
            html.Div([], id='plot1')
        ], id='plot1parent'),
        html.Div([
            html.Div([], id='plot2')
        ], id='plot2parent')
    ], id='right-container')
], id='container')


@app.callback([
    Output(component_id='plot1', component_property='children'),
    Output(component_id='plot2', component_property='children')
],
    [Input(component_id='input-type', component_property='value'),
     Input(component_id='input-year', component_property='value')],
    # Holding output state till user enters all the form information. In this case, it will be chart type and year
    [State("plot1", 'children'), State("plot2", "children")]
)
def get_graph(chart, year, children1, children2):

    # Select data
    df = gun_data[gun_data['year'] == int(year)]

    if chart == 'OPT1':
        # Compute required information for creating graph from the data
        state_bar_kill, map_count_kill = compute_data_choice_1(df)

        bar_fig_killed = px.bar(state_bar_kill, x='state',
                                y="n_killed", color_discrete_sequence=['purple'])
        bar_fig_killed.update_traces(
            marker_color='#b51616', marker_line_color='black', marker_line_width=1.5, opacity=1)
        bar_fig_killed.update_layout(title_text=f'People Killed per each Incident of Violence (5 highest states)',
                                     font_family='Tahoma', xaxis={'categoryarray': state_bar_kill['n_killed']},
                                     plot_bgcolor='white')
        bar_fig_killed.update_yaxes(title_text="Mean number of People Killed")

        map_fig_killed = px.choropleth(map_count_kill,
                                       locations='state_code',
                                       color='n_killed',
                                       hover_data=['state', 'n_killed'],
                                       locationmode='USA-states',
                                       scope='usa',
                                       labels={'n_killed': 'Number Killed'},
                                       color_continuous_scale='Reds',
                                       range_color=[0, map_count_kill['n_killed'].max()])

        return [
            dcc.Graph(figure=bar_fig_killed),
            dcc.Graph(figure=map_fig_killed)
        ]

    else:
        state_bar_injury, map_count_injury = compute_data_choice_2(df)

        bar_fig_injury = px.bar(state_bar_injury, x='state', y="n_injured")
        bar_fig_injury.update_traces(
            marker_color='#b51616', marker_line_color='black', marker_line_width=1.5, opacity=1)
        bar_fig_injury.update_layout(title_text=f'People Injured per each Incident of Violence (5 highest states)',
                                     font_family='Tahoma', xaxis={'categoryarray': state_bar_injury['n_injured']},
                                     plot_bgcolor='white')
        bar_fig_injury.update_yaxes(title_text="Mean number of People Injured")

        map_fig_injury = px.choropleth(map_count_injury,
                                       locations='state_code',
                                       color='n_injured',
                                       hover_data=['state', 'n_injured'],
                                       locationmode='USA-states',
                                       scope='usa',
                                       labels={'n_injured': 'Number Injured'},
                                       color_continuous_scale='Reds',
                                       range_color=[0, map_count_injury['n_injured'].max()])

        return [
            dcc.Graph(figure=bar_fig_injury),
            dcc.Graph(figure=map_fig_injury)
        ]


# Run the app
if __name__ == '__main__':
    app.run_server(mode="inline", host="localhost", debug=False,
                   dev_tools_ui=False, dev_tools_props_check=False)
