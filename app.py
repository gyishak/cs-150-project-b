from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import wb


app= Dash(__name__, external_stylesheets=[dbc.themes.MORPH])

#df = pd.read_csv("API_ER.H2O.FWTL.ZS_DS2_en_csv_v2_13232.csv")
indicators = {
    "ER.H2O.FWTL.ZS":"Annual Freshwater Withdrawals",
    "AG.LND.AGRI.ZS":"Agricultural Land (% of land Area)"
}

countries = wb.get_countries()
countries["capitalCity"].replace({"": None}, inplace=True)
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries.rename(columns={"name": "country"})


the_asia = [
    "AF", "AM", "AZ", "BH", "BD", "BT", "MM", "BN", "KH", "CN",
    "CY", "GE", "IN", "ID", "IR", "IQ", "IL", "JP", "JO", "KZ",
    "KP", "KR", "KW", "KG", "LA", "LB", "MO", "MY", "MV", "MN",
    "NP", "OM", "PK", "PH", "QA", "SA", "SG", "LK", "SY", "TJ",
    "TH", "TL", "TR", "TM", "AE", "UZ", "VN", "YE"
]
def update_wb_data():
    # Retrieve specific world bank data from API
    df = wb.download(
        indicator=(list(indicators)), country=the_asia, start=2001, end=2021
    )
    # print(df)
    df = df.reset_index()
    # print(df)
    df.year = df.year.astype(int)

    # Add country ISO3 id to main df
    df = pd.merge(df, countries, on="country")
    df = df.rename(columns=indicators)

    return df
df=update_wb_data()
df=df[df['iso3c'].isin(the_asia)]

app.layout=dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Water Scarcity vs Agricultural Expansion",
                        style={"textAlign":"center"},
                    ),
                   dcc.Graph(id="my-choropleth",figure={}),
                ],
                width=15,
            )
        ),
        dbc.Row([
            dbc.Col(
                [
                    dbc.Label(
                        "Select Data Set:",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20},
                    ),

                    dcc.Dropdown(
                        id="my-dropdown",
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        value=list(indicators.values())[0],
                        # inputClassName="me-2",
                    ),
                ],
                width=4,

            ),
            dbc.Col(
                [
                    dbc.Label(
                        "Select A Year",
                        className="fw-bold",
                        style={"textDecoration":"underline", "fontsize":20},
                    ),
                    dcc.RangeSlider(
                        id="years-range",
                        min=2001,
                        max=2021,
                        step=2,
                        value=[2001,2021],
                        marks={year: str(year) for year in range(2001, 2021, 2)
                        },
                    ),
                ],
                width=4,
            )
            ]
        ),
        dbc.Row(
            [dbc.Col([
                dbc.Button(
                    id="my-button",
                    children="Submit",
                    color="primary",
                    className="fw-bold d-flex justify-content-end"
                ),
            ],
                width=12,
            )],
        ),
        dbc.Row(
            dbc.Col(
                [
                   html.Div(dcc.Graph(id="line-chart", figure={}), className="row"),
                    html.Div(
            [
                    #     html.Div(
                    #         dcc.Dropdown(
                    #         id="my-dropdown",
                    #         multi=True,
                    #         options=[
                    #             {"label": x, "value": x}
                    #             for x in sorted(countries["iso3c"])
                    #         ],
                    #     ),
                    #     className="three columns",
                    # ),
                ],
                className="row",
        ),
                ],
                width=15,
            )
        ),
        dbc.Row(
            [dbc.Col([
                html.Div(dcc.Graph(id="example-graph", figure={}), className="row"),
            ],
                width=12,
            )],
        ),

        dcc.Store(id="storage", storage_type="session", data={}),
        dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)


@app.callback(Output("storage", "data"), Input("timer", "n_intervals"), )
def store_data(n_time):
    dataframe = update_wb_data()
    return dataframe.to_dict("records")

@app.callback(
    Output("my-choropleth", "figure"),
    Input("my-button", "n_clicks"),
    Input("storage", "data"),
    State("years-range", "value"),
    State("my-dropdown", "value"),
)
def update_graph(n_clicks, stored_dataframe,years_chosen, indct_chosen):

    dff = update_wb_data()
    dff = pd.DataFrame.from_records(stored_dataframe)
    #dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]


    if years_chosen[0] != years_chosen[1]:
        dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
        dff = dff.groupby(["iso3c", "country"])[indct_chosen].mean()
        dff = dff.reset_index()

        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="asia",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["ER.H2O.FWTL.ZS"]:"Annual Freshwater Withdrawals",
                indicators["AG.LND.AGRI.ZS"]: "Agricultural Land (% of land Area)"
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig

    if years_chosen[0] == years_chosen[1]:
        dff = dff[dff["year"].isin(years_chosen)]
        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="asia",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["ER.H2O.FWTL.ZS"]:"Annual Freshwater Withdrawals",
                indicators["AG.LND.AGRI.ZS"]: "Agricultural Land (% of land Area)"
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),

        )
        return fig

##line graph
@app.callback(
    Output(component_id="line-chart", component_property="figure"),
    #[Input(component_id="my-dropdown", component_property="value")],
    [Input(component_id="years-range", component_property="value")],
)
def update_graphs(years_chosen):
    indct_chosen = "Annual Freshwater Withdrawals"
    dff = update_wb_data()
    dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]

    fig = px.line(
        data_frame=dff,
        #locations="iso3c",
        x="year",
        y=indct_chosen,
        color="country",
    )
    return fig

##bar graph
@app.callback(
    Output(component_id="example-graph", component_property="figure"),

    [Input("years-range", component_property="value")],)
def bar_graph(years_chosen):
    indct_chosen = "Annual Freshwater Withdrawals"
    dff = update_wb_data()
    dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
    fig =px.bar(
        data_frame=dff,
        x="year",
        y= indct_chosen,
        color="country",
        barmode="group")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)


