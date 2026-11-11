
... import pandas as np
... import dash
... from dash import html, dcc
... from dash.dependencies import Input, Output
... from dash import dash_table
... 
... import plotly.graph_objects as go
...
...
... import numpy as np
... 
... 
... # -------------------------------------------------------------
... # LOAD DATA
... # -------------------------------------------------------------
... df = pd.read_csv("electric-car-stocks.csv")
... df.columns = df.columns.str.strip()
... df["Year"] = df["Year"].astype(int)
... entities = sorted(df["Entity"].unique())
... 
... # -------------------------------------------------------------
... # CREATE DASH APP
... # -------------------------------------------------------------
... app = dash.Dash(__name__, suppress_callback_exceptions=True)
... server = app.server
... 
... # -------------------------------------------------------------
... # LAYOUT
... # -------------------------------------------------------------
... app.layout = html.Div([
...     html.H1("Electric Car Stocks Dashboard", style={"textAlign": "center"}),
... 
...     dcc.Tabs(id="mainTabs", value="overviewTab", children=[
...         dcc.Tab(label="Overview", value="overviewTab"),
...         dcc.Tab(label="Graphics (Nested Tabs)", value="graphicsTab"),
...         dcc.Tab(label="Data Table", value="tableTab"),
...         dcc.Tab(label="Summary Statistics", value="summaryTab"),
    ]),

    html.Hr(),

    # ------------------- FILTERS -------------------
    html.Div([
        html.Div([
            html.Label("Select Entity:"),
            dcc.Dropdown(
                id="entityFilter",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": e, "value": e} for e in entities],
                value=["All"],
                multi=True,
                style={"width": "95%"}
            )
        ], style={'width': '28%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Year Range:"),
            dcc.RangeSlider(
                id="yearFilter",
                min=df["Year"].min(),
                max=df["Year"].max(),
                value=[df["Year"].min(), df["Year"].max()],
                marks={y: str(y) for y in range(df["Year"].min(), df["Year"].max()+1, 2)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'width': '68%', 'display': 'inline-block', 'paddingLeft': '2%'})
    ], style={"padding": "15px"}),

    html.Hr(),

    html.Div(id="tabContent"),
    dcc.Store(id="filteredData")
])

# -------------------------------------------------------------
# CALLBACK → FILTER DATA
# -------------------------------------------------------------
@app.callback(
    Output("filteredData", "data"),
    [Input("entityFilter", "value"),
     Input("yearFilter", "value")]
)
def filter_data(entitysel, yearrange):
    low, high = yearrange
    dff = df.copy()

    if "All" not in entitysel:
        dff = dff[dff["Entity"].isin(entitysel)]

    dff = dff[(dff["Year"] >= low) & (dff["Year"] <= high)]
    return dff.to_dict("records")

# -------------------------------------------------------------
# CALLBACK → MAIN TABS
# -------------------------------------------------------------
@app.callback(
    Output("tabContent", "children"),
    [Input("mainTabs", "value"),
     Input("filteredData", "data")]
)
def render_tabs(tab, data):

    # SAFETY CHECK: Data not ready yet
    if not data:
        return html.Div("Loading data...")

    dff = pd.DataFrame(data)

    if tab == "overviewTab":
        fig = go.Figure()

        for entity in dff["Entity"].unique():
            df_e = dff[dff["Entity"] == entity]
            fig.add_trace(go.Scatter(
                x=df_e["Year"],
                y=df_e["Electric car stocks"],
                mode="lines+markers",
                name=entity
            ))

        return html.Div([
            html.H3("Overview"),
            dcc.Graph(figure=fig)
        ])

    if tab == "graphicsTab":
        return html.Div([
            dcc.Tabs(id="nestedTabs", value="line", children=[
                dcc.Tab(label="Line Chart", value="line"),
                dcc.Tab(label="Bar Chart", value="bar"),
                dcc.Tab(label="Scatter Plot", value="scatter"),
                dcc.Tab(label="Trendline Plot", value="trend")
            ]),
            html.Div(id="nestedContent", style={"paddingTop": "20px"})
        ])

    if tab == "tableTab":
        return html.Div([
            html.H3("Filtered Data Table"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in dff.columns],
                data=dff.to_dict("records"),
                page_size=12,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "center"}
            )
        ])

    if tab == "summaryTab":
        return html.Div([
            html.H3("Summary Statistics"),
            html.Pre(dff.describe().to_string())
        ])

# -------------------------------------------------------------
# CALLBACK → NESTED GRAPH TABS
# -------------------------------------------------------------
@app.callback(
    Output("nestedContent", "children"),
    [Input("nestedTabs", "value"),
     Input("filteredData", "data")]
)
def nested_graphs(nestedTab, data):

    # SAFETY CHECK
    if not data:
        return html.Div("Waiting for data...")

    dff = pd.DataFrame(data)

    if nestedTab == "line":
        fig = go.Figure()
        for entity in dff["Entity"].unique():
            df_e = dff[dff["Entity"] == entity]
            fig.add_trace(go.Scatter(
                x=df_e["Year"],
                y=df_e["Electric car stocks"],
                mode="lines+markers",
                name=entity
            ))
        return dcc.Graph(figure=fig)

    if nestedTab == "bar":
        sums = dff.groupby("Entity")["Electric car stocks"].sum().reset_index()
        fig = go.Figure(go.Bar(x=sums["Entity"], y=sums["Electric car stocks"]))
        return dcc.Graph(figure=fig)

    if nestedTab == "scatter":
        fig = go.Figure()
        for entity in dff["Entity"].unique():
            df_e = dff[dff["Entity"] == entity]
            fig.add_trace(go.Scatter(
                x=df_e["Year"],
                y=df_e["Electric car stocks"],
                mode="markers",
                name=entity
            ))
        return dcc.Graph(figure=fig)

    if nestedTab == "trend":
        fig = go.Figure()
        for entity in dff["Entity"].unique():
            df_e = dff[dff["Entity"] == entity]
            fig.add_trace(go.Scatter(
                x=df_e["Year"],
                y=df_e["Electric car stocks"],
                mode="markers",
                name=entity
            ))
            if len(df_e) > 1:
                m, b = np.polyfit(df_e["Year"], df_e["Electric car stocks"], 1)
                fig.add_trace(go.Scatter(
                    x=df_e["Year"],
                    y=m * df_e["Year"] + b,
                    mode="lines",
                    name=f"{entity} trend"
                ))
        return dcc.Graph(figure=fig)

# -------------------------------------------------------------
# RUN APP
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
