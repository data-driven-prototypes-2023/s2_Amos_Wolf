import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
from dash_bootstrap_components._components.Container import Container
from app import app

#PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto",
    align="center",
)



nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Overview", href="/")),
        dbc.NavItem(dbc.NavLink("Individual", href="/individual")),
    ],
    justified=True,
    navbar=True
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Food Data Analysis"),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                [nav, 
                #search_bar,
                ],
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    fixed="top",
    style={
        "backgroundColor": 'rgb(245, 244, 242)',
        'border': '1px solid rgb(215, 207, 193)',
    }
    #color="dark",
    #dark=True,
)


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def get_header():
    return navbar


