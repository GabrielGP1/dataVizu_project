import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

import preProcessData
from sankey import create_sankey
from bar_chart import create_bar_chart
from map import create_map
from lineChart import create_interactive_hour_chart

app = dash.Dash(__name__)
app.title = 'Project | INF8808'

# Load all processed data
df_dic = preProcessData.preprocess_all()
preProcessData.show_total_memory_usage(df_dic)

sankey_df = df_dic["sankey"]
sankey_fig = create_sankey(sankey_df)

bar_chart_df = df_dic["bar"]
bar_fig = create_bar_chart(bar_chart_df)

lineChart_df = df_dic["line"]

map_df = df_dic["map"]
map_df['primary_type'] = map_df['primary_type'].astype(str).str.title()
year_options = sorted(map_df['year'].dropna().unique())
crime_counts = map_df['primary_type'].value_counts()
default_crimes = crime_counts.nlargest(5).index.tolist()
crime_options = crime_counts.nlargest(15).index.tolist()
default_year = max(year_options)
map_fig = create_map(map_df, selected_year=default_year, selected_crimes=default_crimes)

# Layout
app.layout = html.Div([

    html.Div([
        html.Div([
            html.H1("Seven Years of Crime in Chicago", style={"fontSize": "3.5rem", "color": "white", "textAlign": "center"}),
            html.P("Chicago Crime Data: 2018–2024", style={"fontSize": "1.3rem", "color": "white", "textAlign": "center"}),
            html.A("Explore the Data Visualization", href="#section-data", style={"padding": "1rem 2.5rem", "backgroundColor": "#0A84FF", "color": "white", "borderRadius": "40px", "textDecoration": "none", "fontWeight": "bold", "marginTop": "2rem", "display": "inline-block", "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"})
        ], style={"zIndex": 2, "position": "relative", "textAlign": "center", "display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center", "height": "100vh"}),

        html.Div(style={"backgroundImage": 'url("/assets/chicago.jpg")', "backgroundSize": "cover", "backgroundPosition": "center", "position": "absolute", "top": 0, "left": 0, "width": "100%", "height": "100vh", "zIndex": 1, "filter": "brightness(0.4)"})
    ], className="hero-fade", style={"position": "relative", "height": "100vh", "overflow": "hidden"}),

    html.Div([
        html.H2("Which crimes are most associated with arrests?", style={"color": "white", "textAlign": "center", "fontSize": "2rem"}),
        dcc.Graph(figure=sankey_fig, config={"displayModeBar": False}, style={"height": "75vh", "marginTop": "30px"})
    ], id="section-data", style={"backgroundColor": "#111111", "padding": "80px 0"}),

    html.Div([
        html.H2("Are weekends more dangerous?", style={"color": "white", "textAlign": "center", "fontSize": "2rem"}),
        dcc.Graph(id='bar-weekend-chart', config={"displayModeBar": False}, figure=bar_fig, style={"height": "75vh", "marginTop": "30px"})
    ], id="section-weekend", style={"backgroundColor": "#111111", "padding": "80px 0"}),

    html.Div([
        html.H2("Where are crimes located in Chicago?", style={"color": "white", "textAlign": "center", "fontSize": "2rem"}),

       html.P(
        "Each circle on the map represents a group of nearby crimes clustered within roughly 750 meters. "
        "The size of the circle reflects the number of crimes in that area, and the color shows the selected crime type.",
        style={
            "color": "white",
            "fontSize": "1.4rem", 
            "textAlign": "center",
            "maxWidth": "800px",
            "margin": "0 auto 30px"
             }
        ),

        html.Div([
            html.Div([
                html.Label("Select Year", style={"color": "white", "fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[{"label": str(y), "value": y} for y in year_options],
                    value=default_year,
                    clearable=False,
                    style={"width": "100%"}
                )
            ], style={"flex": "1", "marginRight": "20px"}),

            html.Div([
                html.Label("Select Crime Types", style={"color": "white", "fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Dropdown(
                    id="crime-dropdown",
                    options=[{"label": c, "value": c} for c in crime_options],
                    value=default_crimes,
                    multi=True,
                    style={"width": "100%"}
                )
            ], style={"flex": "2"})
        ], style={
            "display": "flex",
            "gap": "20px",
            "padding": "0 10% 30px",
            "flexWrap": "wrap"
        }),

        dcc.Graph(
            id="map-figure",
            figure=map_fig,
            config={"displayModeBar": False},
            style={"height": "80vh", "marginTop": "10px", "maxWidth": "90%", "marginLeft": "auto", "marginRight": "auto"}
        )
    ], id="section-map", style={"backgroundColor": "#111111", "padding": "80px 0"}),

    html.Div([
        html.H2("When Does Crime Peak?", style={"color": "white", "textAlign": "center", "fontSize": "2rem"}),

        html.Div([
            html.Label("Select Time Unit", style={"color": "white", "fontWeight": "bold", "marginRight": "10px"}),
            dcc.Dropdown(
                id="time-unit-dropdown",
                options=[
                    {"label": "Hour", "value": "hour"},
                    {"label": "Month", "value": "month"},
                    {"label": "Year", "value": "year"},
                ],
                value="hour",
                clearable=False,
                style={"width": "200px", "display": "inline-block", "marginRight": "40px"}
            )
        ], style={"textAlign": "center", "marginBottom": "20px"}),

        dcc.Graph(
            id="lichart_fig",
            figure=create_interactive_hour_chart(lineChart_df, "hour"),
            config={"displayModeBar": False},
            style={"height": "75vh", "marginTop": "30px"}
        )
    ], id="section-hourly", style={"backgroundColor": "#111111", "padding": "80px 0"})
])

@app.callback(
    Output("map-figure", "figure"),
    [Input("year-dropdown", "value"), Input("crime-dropdown", "value")]
)
def update_map(selected_year, selected_crimes):
    return create_map(map_df, selected_year, selected_crimes)

@app.callback(
    Output("lichart_fig", "figure"),
    [Input("time-unit-dropdown", "value")]  
)
def update_chart(time_unit):
    return create_interactive_hour_chart(lineChart_df, time_unit)

