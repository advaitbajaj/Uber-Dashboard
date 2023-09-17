from dash import Dash, dcc, html, Input, Output, State
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import json
from shapely import wkt
import psycopg2
import plotly_express as px
from dash_extensions.javascript import Namespace

pickups = pd.read_csv("Required Data\\2014 EDA\\Combined Data.csv")

ns = Namespace("myNamespace", "mySubNamespace")

list_of_locations = {
    "Madison Square Garden": {"lat": 40.7505, "lon": -73.9934},
    "Yankee Stadium": {"lat": 40.8296, "lon": -73.9262},
    "Empire State Building": {"lat": 40.7484, "lon": -73.9857},
    "New York Stock Exchange": {"lat": 40.7069, "lon": -74.0113},
    "JFK Airport": {"lat": 40.644987, "lon": -73.785607},
    "Grand Central Station": {"lat": 40.7527, "lon": -73.9772},
    "Times Square": {"lat": 40.7589, "lon": -73.9851},
    "Columbia University": {"lat": 40.8075, "lon": -73.9626},
    "United Nations HQ": {"lat": 40.7489, "lon": -73.9680},
}

months = {
    4 : ["April", "april14"],
    5 : ["May", "may14"],
    6 : ["June", "june14"],
    7 : ["July", "july14"],
    8 : ["August", "august14"],
    9 : ["September", "september14"]
}

conn = psycopg2.connect(
    host="localhost",
    dbname="uber_nyc",
    user="postgres",
    password="password"
)

cursor = conn.cursor()


app = Dash(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.themes.GRID])

app.layout = html.Div(
    id="main",
    children=[
        # memory storage
        dcc.Store(
            id = "store",
        ),

        # main
        dbc.Container(
            style={
                "background-color":"#1E1E1E"
            },
            fluid=True,
            children=[
                dbc.Row(
                    children=[
                        # sidebar
                        dbc.Col(
                            width=3,
                            class_name="sidebar",
                            children=[
                                # title
                                dbc.Row(
                                    class_name="title",
                                    children=[
                                        dbc.Col(
                                            children=[
                                                html.H2("Uber Rides Dashboard"),
                                                html.Br()
                                            ]
                                        )
                                    ]
                                ),
                                
                                # filters
                                dbc.Row(
                                    class_name="filters",
                                    children=[
                                        dbc.Col(
                                            class_name="dropdown-center",
                                            children=[                                                
                                                html.H4("Month"),
                                                dcc.Dropdown(
                                                    id="month_select",
                                                    placeholder="Select Month",
                                                    value=4,
                                                    clearable=False,
                                                    options=[
                                                        {"label": "April", "value": 4},
                                                        {"label": "May", "value": 5},
                                                        {"label": "June", "value": 6},
                                                        {"label": "July", "value": 7},
                                                        {"label": "August", "value": 8},
                                                        {"label": "September", "value": 9}
                                                    ]
                                                ),
                                                html.Br(),

                                                html.H4("Date"),
                                                dcc.Slider(
                                                    id="date_select",
                                                    min=1,
                                                    max=30,
                                                    value=1,
                                                ),
                                                html.H6(
                                                    children=[
                                                        "Date Selected: ",
                                                        html.Span(
                                                            id="date_selected"
                                                        )    
                                                    ]
                                                ),
                                                html.Br(),

                                                html.H4("Time"),
                                                dcc.Dropdown(
                                                    id="time_select",                                                    
                                                    placeholder="Select Time",
                                                    clearable=False,
                                                    value=str(0),
                                                    # multi=True,
                                                    options=[
                                                        {
                                                            "label": str(n) + ":00",
                                                            "value": n,
                                                        }
                                                        for n in range(24)
                                                    ],
                                                ),                                                
                                                html.Br(),

                                                html.H4("Location"),
                                                dcc.Dropdown(
                                                    id="location_select",                                                    
                                                    placeholder="Select Location",
                                                    clearable=False,
                                                    value="Madison Square Garden",
                                                    options=[
                                                        {"label": i, "value": i}
                                                        for i in list_of_locations
                                                    ],
                                                ),
                                                html.Br()
                                            ]
                                        )
                                    ]
                                ),

                                # kpi
                                dbc.Row(
                                    children=[
                                        dbc.Col( 
                                            class_name="kpi",                        
                                            children=[
                                                html.H6(
                                                    children=[
                                                        "Rides on",
                                                        html.Br(),
                                                        
                                                        html.Span(
                                                            id="kpi_date"
                                                        ),
                                                        html.Br(),

                                                        html.Span(
                                                            id="rides_date_selected",                                                            
                                                        )
                                                    ]
                                                ),                                                
                                            ]
                                        ),

                                        dbc.Col(
                                            class_name="kpi",
                                            children=[
                                                html.H6(
                                                    children=[
                                                        "Hour selected:",
                                                        html.Br(),
                                                        html.Span(
                                                            id="kpi_hour"
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),

                                        dbc.Col(
                                            class_name="kpi",
                                            children=[
                                                html.H6(
                                                    children=[
                                                        "Rides in selection:",
                                                        html.Br(),
                                                        html.Span(
                                                            id="rides_hour_selected"
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),                                        
                                    ]
                                )
                            ]
                        ),

                        # content
                        dbc.Col(
                            style={
                                "background-color":"#31302f"
                            },
                            class_name="content",
                            children=[
                                # Row 1
                                dbc.Row(
                                    class_name="content-row-1",
                                    children=[
                                        # map
                                        dbc.Col(
                                            class_name="map-col",
                                            children=[
                                                dl.Map(
                                                    id="map",                                               
                                                    children=[                                                        
                                                        dl.TileLayer(
                                                            url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
                                                            attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        
                                        # Carousel
                                        dbc.Col(
                                            
                                            children=[
                                                dbc.Carousel(
                                                    id="carousel",
                                                    items=[
                                                        {"key": "1", "src": "/assets/carousel/pickupPointsHeatMap.png", "img_style": {"max-height": "50vh"}},
                                                        {"key": "2", "src": "/assets/carousel/dailyPickupsLine.png", "img_style": {"max-height": "50vh"}},
                                                    ],
                                                    controls=True,
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                
                                # Row 2
                                dbc.Row(
                                    class_name="content-row-2",
                                    # Chart
                                    children=[
                                        dbc.Col(
                                            class_name="chart",
                                            children=[
                                                dcc.Graph(
                                                    id="chart",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    [
        Output(component_id="store", component_property="data"),
    ],
    [
        Input(component_id="month_select", component_property="value"),
        Input(component_id="date_select", component_property="value"),
        Input(component_id="time_select", component_property="value"),
        Input(component_id="location_select", component_property="value"),
    ]
)
def update_store(month, date, time, location):
    startTime = f"{time}:00:00" if (int(time) > 9) else f"0{time}:00:00"
    endTime = "{}:00:00".format(int(time) + 1) if (int(time) > 8) else "0{}:00:00".format(int(time) + 1)
    tableName = months[month][1]

    sql1 = f"SELECT COUNT(*) FROM {tableName} WHERE \"Date\" = {int(date)}"
    cursor.execute(sql1)
    ridesDateSelected = cursor.fetchone()[0] # type: ignore

    sql2 = f"SELECT * FROM {tableName} WHERE \"Date\" = {int(date)} AND \"Time\" BETWEEN \'{startTime}\' AND \'{endTime}\'"
    table = gpd.read_postgis(sql=sql2, con=conn, geom_col="geometry")
    ridesHourSelected = len(table)  # type: ignore

    sql3 = f"SELECT * FROM nyc_locations WHERE \"Location\" = \'{location}\'"
    locationTable = gpd.read_postgis(sql=sql3, con=conn, geom_col="geometry")

    toStore = {
        'month': month,
        'monthName': months[month][0],
        'date': date,
        'startTime': startTime,
        'endTime': endTime,
        'location': location,
        'ridesDateSelected': ridesDateSelected,
        'ridesHourSelected': ridesHourSelected,
        'table': table.to_json(),  # type: ignore
        'locationTable': locationTable.to_json()  # type: ignore
    }    

    return [toStore]

@app.callback(
    [
        Output(component_id="date_select", component_property="max")
    ],
    [
        Input(component_id="store", component_property="data"),
    ]
)
def update_date_slider(data):
    month = data['month']
    if month in [5, 7, 8]:
        return [31]
    return [30]

@app.callback(
    [
        Output(component_id="date_selected", component_property="children")
    ],
    [
        Input(component_id="store", component_property="data"),
    ]
)
def update_date_selected(data):
    date = data['date']
    return [int(date)]

@app.callback(
    [
        Output(component_id="kpi_date", component_property="children"),
        Output(component_id="kpi_hour", component_property="children"),
        Output(component_id="rides_date_selected", component_property="children"),
        Output(component_id="rides_hour_selected", component_property="children")
    ],
    [
        Input(component_id="store", component_property="data"),
    ]
)
def update_kpi(data):
    month = data['monthName']
    date = int(data['date'])
    kpiDate = f"{month} {date}:"

    kpiTime = data['startTime'][:-3]

    kpiDateRows = data['ridesDateSelected']

    kpiTimeRows = data['ridesHourSelected']

    return [kpiDate, kpiTime, kpiDateRows, kpiTimeRows]

@app.callback(
    [
        Output(component_id="map", component_property="children")
    ],
    [
        Input(component_id="store", component_property="data"),
    ]
)
def update_map(data):
    mapData = json.loads(data['table'])
    locationData = json.loads(data['locationTable'])
    mapChildren = [
        dl.TileLayer(
            url='https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
            attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
        ),
        dl.GeoJSON(
            data = mapData,
        ),
        dl.GeoJSON(
            data=locationData,
            zoomToBounds=True,
            options=dict(pointToLayer=ns("pointToLayer"))
        )
    ]

    return [mapChildren]

@app.callback(
    [
        Output(component_id="chart", component_property="figure")
    ],
    [
        Input(component_id="store", component_property="data")
    ]
)
def update_chart(data):
    day = data['date']
    month = data['monthName']

    dailyRides = pickups.query(
        f'Day == {day} and Month == \"{month}\"'
    )

    dailyRides = dailyRides['Hour'].value_counts().sort_index()

    labels = {
        "index": "Hour",
        "value": "Number of Rides"
    }

    byHourFigure = px.bar(dailyRides, labels=labels)
    byHourFigure.layout.margin.l = 0
    byHourFigure.layout.margin.r = 0
    byHourFigure.layout.margin.b = 0
    byHourFigure.layout.margin.t = 0

    return [byHourFigure]


if __name__ == "__main__":
    app.run_server(debug=True)