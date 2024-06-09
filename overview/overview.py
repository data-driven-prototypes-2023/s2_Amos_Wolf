import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc, Dash, dash_table
from dash_bootstrap_components._components.Container import Container
import pandas as pd
from app import app
import pandas as pd
from clean_dataset.calc import new_column_lang, agent_clean_list
import numpy as np
import dash
import flask
from overview.graphs import bar_chart_brands, nutriscore_brand_chart, ecoscore_brand_chart, calculatedscore_brand_chart
from common_elements.graphs import create_map
from clean_dataset.calc import transl_allergens




df = pd.read_csv('static/openfoodfacts_export.csv', sep='\t', low_memory=False)
df = df[df['nutrition_data_per']=='100g']
order_of_importance = ['en', 'es', 'fr', 'pt', 'it', 'de', 'ar', 'bg', 'ca', 'cs', 'da', 'el', 'fi', 'hr', 'hu', 'is', 'ja', 'nl', 'no', 'pl', 'ro', 'sl', 'sv', 'th', 'xx']
df['product_name']=new_column_lang(df, 'product_name', order_of_importance)
df['ingredients_text'] = new_column_lang(df, 'ingredients_text', order_of_importance)

brands= df['brands'].str.lower().str.split(',').explode().str.strip().str.capitalize().unique()
brands = [brand for brand in brands if brand is not None and brand != '']
brands = np.sort(brands)

countries = df['countries'].str.split(',').explode().str.strip().str.capitalize().unique()
countries = [country for country in countries if country is not None and country != ''] 
countries = agent_clean_list(countries)

list_allergens=list(set([transl_allergens(allergen) for allergen in df['allergens'].str.split(',').explode().str.strip().unique() if allergen is not None]))
list_allergens.sort()

input_groups = html.Div(
    [
        dbc.InputGroup(
            [
                dcc.Dropdown(
                    id='select_allergens',
                    options=[{'label': brand, 'value': brand} for brand in list_allergens],
                    multi=True,
                    style={'width': '100%'},
                    placeholder='Filter products without following allergens',
                ),
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                dcc.Dropdown(
                    id='select_country',
                    options=[{'label': brand, 'value': brand} for brand in countries],
                    multi=True,
                    style={'width': '100%'},
                    placeholder='Select a country',
                ),
            ],
            className="mb-3",
        ),
        dbc.InputGroup(
            [
                
                dcc.Dropdown(
                    id='select_brand',
                    options=[{'label': brand, 'value': brand} for brand in brands],
                    multi=True,
                    style={'width': '100%'},
                    placeholder='Select a brand',
                ),
            ]
        ),
    ]
)


#table = dbc.Table.from_dataframe(df[['code', 'product_name', 'brands']].head(10), striped=True, bordered=True, hover=True, className='rounded')



def create_dash_table(df):
    table=dash_table.DataTable(
        id='table_overview',
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_table={'height': '400px', 'overflowY': 'auto'},
        fixed_rows={'headers': True},
        #row_selectable='multi',
        page_size=100,
        style_cell={
            # all three widths are needed
            'minWidth': '30px', 
            'width': 'auto', 
            'maxWidth': '180px',
            #'whiteSpace': 'normal',
            'overflow': 'hidden',
            'textOverflow': 'clip',
        },
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('records')
        ],
        tooltip_duration=None
        
    )
    return table

@app.callback(
    Output('url', 'pathname'),
    Output('url', 'search'),
    Input('table_overview', 'active_cell'),
    State('table_overview', 'data'),
    State('table_overview', 'page_current'),
    State('table_overview', 'page_size')
)
def update_individual_view(active_cell, data, page_current, page_size):
    if active_cell is None:
        return dash.no_update  # No update if no cell is selected
    print(active_cell)
    print('Here')
    # Calculate the actual row index in the dataframe
    if page_current is None:
        page_current = 0
    row_index = active_cell['row'] + page_current * page_size
    cell_value = data[row_index]['code'] if 'code' in data[row_index] else 'N/A'
    
    # Redirect to the new URL with the code
    return '/individual', f'?code={cell_value}'


@app.callback(
    Output('table_placeholder', 'children'),
    Output('bar_chart_brands', 'figure'),
    Output('map_chart', 'figure'),
    Input('select_brand', 'value'),
    Input('select_country', 'value'),
    Input('select_allergens', 'value'),
)
def display_table(value, value_country, allergens):
    display_columns=['code', 'product_name', 'brands', 'ingredients_text']

    # Start by filtering
    if value is not None and value!=[]:
        brands_selection = df['brands'].str.lower()
        values = [v.lower() for v in value]
        indexes = [brands_selection.str.contains(v, na=False) for v in values]
        df_filtered = df.loc[indexes[0]]
        
    else:
        df_filtered = df

    if value_country is not None and value_country!=[]: # filter not correct but to showcase LLM functionalities
        countries_selection = df['countries'].str.lower()
        values = [v.lower() for v in value_country]
        indexes = [countries_selection.str.contains(v, na=False) for v in values]
        df_filtered = df_filtered.loc[indexes[0]]
    
    if allergens is not None and allergens != []:
        print(allergens)
        allergens_selection = df['allergens'].apply(lambda allergens: [transl_allergens(allergen.strip()) for allergen in str(allergens).split(',')] if pd.notnull(allergens) else allergens)
        indexes = [allergens_selection.apply(lambda x: v not in (list(x) if isinstance(x, list) else [x]) if x is not None else True) for v in allergens]
        df_filtered = df.loc[np.all(indexes, axis=0)]
    

    # Create table
    table = create_dash_table(df_filtered[display_columns])

    # Create brand chart
    brand_chart = bar_chart_brands(df_filtered)

    # Create list of countries
    list_countries = df_filtered['countries'].str.split(',').explode().str.strip().str.capitalize().unique()
    list_countries = [country for country in list_countries if country is not None and country != '']
    list_countries = agent_clean_list(list_countries)

    # Create map chart
    map_chart = create_map(list_countries)

    return table, brand_chart, map_chart

collapse = html.Div(
    [
        dbc.Button(
            "Filter products",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            input_groups,
            id="collapse",
            is_open=False,
        ),
    ]
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('calculatedscore_brand_chart', 'figure'),
    Input('calculated_score_slider', 'value'),
)
def update_calculatedscore_brand_chart(value):
    value=value/100
    fig = calculatedscore_brand_chart(df, value)
    return fig


def get_overview():
    return dbc.Container(
        [
            #dcc.Location(id='url', refresh=True),
            dbc.Row(
                [
                    
                    collapse,

                ],
            ),
            html.H3('Product overview'),
            dbc.Row(
                [
                    
                ],
                id='table_placeholder',
                className='mt-3',
            ),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='bar_chart_brands',),
                ]),
                dbc.Col([
                    dcc.Graph(id='map_chart'),
                ]),
            ]),
            html.Div(
                [
                    html.H3('Brand Analysis'),
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(figure=nutriscore_brand_chart(df), id='nutriscore_brand_chart'),
                            dcc.Graph(figure=ecoscore_brand_chart(df), id='ecoscore_brand_chart'),
                        ]),
                        dbc.Col([
                            dcc.Graph(figure=calculatedscore_brand_chart(df), id='calculatedscore_brand_chart'),
                            dcc.Slider(
                                id='calculated_score_slider',
                                min=0,
                                max=100,
                                step=1,
                                value=50,
                                marks={i: 'Nutri' if i == 0 else 'Eco' if i == 100 else str(i) for i in range(0, 101, 20)},
                            ),
                        ],
                        class_name='text-center',
                        style={'position': 'relative', 'transform': 'translateY(25%)'},)  # center the slider vertically),
                    ])
                ],
                style={
                    
                    'border': '1px solid #000',
                    'border-radius': '.25rem',
                    'margin-top': '.75rem',
                    'padding': '.75rem'
                }
            )
            
            
            
        ],
    )

