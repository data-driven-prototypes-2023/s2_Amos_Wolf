import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc, Dash
from dash_bootstrap_components._components.Container import Container
import pandas as pd
from app import app
from clean_dataset.calc import new_column_lang
from common_elements.graphs import create_map
import dash
import re
from individual.graphs import create_bar_chart
from clean_dataset.calc import get_nutrition_columns

macronutrients, vitamins_minerals, vitamins, sugars, energy, fats, alcohols_polyols, fatty_acids, others = get_nutrition_columns()


macro_prepared = [macro for macro in macronutrients if 'prepared' in macro]
macro_not_prepared = [macro for macro in macronutrients if 'prepared' not in macro]


df = pd.read_csv('static/openfoodfacts_export.csv', sep='\t', low_memory=False)
order_of_importance = ['en', 'es', 'fr', 'pt', 'it', 'de', 'ar', 'bg', 'ca', 'cs', 'da', 'el', 'fi', 'hr', 'hu', 'is', 'ja', 'nl', 'no', 'pl', 'ro', 'sl', 'sv', 'th', 'xx']


def get_element_by_id(id):
    return df.loc[int(id)]

def scroll_down_input(df):
    options =[]
    product_names = new_column_lang(df, 'product_name', order_of_importance)
    # drop rows in df where product_names is None
    product_names = product_names.dropna()

    for index, value in product_names.items():
        options.append({'label': value, 'value': index})
    select = dbc.Select(
        id="select_individual",
        options=options,
        value=None,
    )
    return select

@app.callback(
    Output('select_individual', 'value'),
    Input('url', 'search')
)
def update_select_input(href):
    if (href is None) or ('code' not in href):
        return dash.no_update  # No update if no URL is provided
    # Extract the code from the URL
    code = href.split('code=')[-1]
    
    
    return df[df['code'] == code].index[0]

def get_analysis(id):
    element = get_element_by_id(id)
    product_name = new_column_lang(df, 'product_name', order_of_importance).loc[int(id)]
    print(element['countries'].split(', '))
    macro_chart = create_bar_chart(element, macro_not_prepared)
    macro_prepared_chart = create_bar_chart(element, macro_prepared)
    vitamins_minerals_chart = create_bar_chart(element, vitamins_minerals)
    vitamins_chart = create_bar_chart(element, vitamins)
    sugars_chart = create_bar_chart(element, sugars)
    fats_chart = create_bar_chart(element, fats)
    alcohols_polyols_chart = create_bar_chart(element, alcohols_polyols)
    fatty_acids_chart = create_bar_chart(element, fatty_acids)
    others_chart = create_bar_chart(element, others)


    row_elements = [
        dbc.Col([
            dbc.Row([
                html.P('Product name:'),
                html.H3(product_name),
                html.P('Brands:'),
                html.H4(element['brands']),
                html.P('Categories:'),
                html.H4(element['categories']),
                html.P('Labels:'),
                html.H4(element['labels']),
                html.P('Allergens:'),
                html.H4(element['allergens']),
            ])
        ], 
        width=4),
        dbc.Col([
            dcc.Graph(figure=create_map(element['countries'].split(', ')),
                      className='m-3',
                      )
        ], 
        width=8),
    ]

    # Conditionally add macro_chart
    macro_elements = []
    if macro_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=macro_chart), width=3))

    if macro_prepared_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=macro_prepared_chart), width=3))

    if vitamins_minerals_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=vitamins_minerals_chart), width=3))

    if vitamins_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=vitamins_chart), width=3))

    if sugars_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=sugars_chart), width=3))

    if fats_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=fats_chart), width=3))

    if alcohols_polyols_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=alcohols_polyols_chart), width=3))

    if fatty_acids_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=fatty_acids_chart), width=3))

    if others_chart is not None:
        macro_elements.append(dbc.Col(dcc.Graph(figure=others_chart), width=3))
    
    print('Here')

    row_elements.append(dbc.Row(macro_elements, justify='center'))

    row_name_loc = dbc.Row(row_elements)
    print('After')

    return row_name_loc



def get_individual_page():
    return dbc.Container(
        [
            dbc.Row(
                [
                    scroll_down_input(df),
                    dbc.Row(
                        [
                            
                        ],
                        id='analysis'
                    ),
                ],
                
            ),
        ],
        
    )

@app.callback(
    Output('analysis', 'children'),
    [Input('select_individual', 'value')]
)
def display_analysis(value):
    if value is None:
        return html.P('Please select a product')
    else:
        return get_analysis(value)




