from dash import Dash, html, dcc, Input, Output
from individual.individual_page import get_individual_page
from overview.overview import get_overview
from app import app
import dash_bootstrap_components as dbc
from common_elements.header import get_header
import re

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    get_header(),
    html.Div([
        get_individual_page(),
    ],
    id="page-content",
    style={'marginTop': '9vh'}) # Add margin to the top of the page),
],
)

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return get_overview()
    elif re.match(r'/individual.*', pathname):
        return get_individual_page()
    else:
        return dbc.Container(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )

if __name__ == '__main__':
    app.run(debug=True)