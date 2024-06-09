import plotly.graph_objects as go

def bar_chart_brands(df):
    list_brands = df['brands'].str.lower().str.split(',').explode().str.strip().str.capitalize()
    data= list_brands.value_counts().head(20)
    #print(data.values)
    
    fig = go.Figure(data=[go.Bar(
        x=data.index,
        y=data.values,
        text=data.values,
        textposition='auto',
    )])
    fig.update_layout(
        title='Number of products per brand',
        xaxis_title='Brand',
        yaxis_title='Number of products',
    )
    return fig

def nutriscore_brand_chart(df):
    data = df.groupby('brands')['off:nutriscore_grade'].value_counts().unstack().fillna(0)
    data = data[['a', 'b', 'c', 'd', 'e']]
    data.sort_values(['a', 'b', 'c', 'd', 'e'], ascending=False, inplace=True)
    data = data.head(8)
    
    fig = go.Figure()
    
    colors = {'a': 'darkgreen', 'b': 'green', 'c': 'yellow', 'd': 'orange', 'e': 'red'}
    
    for grade in ['a', 'b', 'c', 'd', 'e']:
        fig.add_trace(go.Bar(
            x=data.index,
            y=data[grade],
            name=grade,
            text=data[grade],
            textposition='auto',
            marker_color=colors[grade],  # set color for each grade
        ))
    
    fig.update_layout(
        title='Number of products per Nutri-Score per Brand',
        xaxis_title='Brand',
        yaxis_title='Number of products per score',
        barmode='group'
    )
    
    fig.update_yaxes(type='log')  # set y-axis to logarithmic scale

    return fig

def ecoscore_brand_chart(df):
    data = df.groupby('brands')['off:ecoscore_grade'].value_counts().unstack().fillna(0)
    data = data[['a', 'b', 'c', 'd', 'e']]
    data.sort_values(['a', 'b', 'c', 'd', 'e'], ascending=False, inplace=True)
    data = data.head(8)
    
    fig = go.Figure()
    
    colors = {'a': 'darkgreen', 'b': 'green', 'c': 'yellow', 'd': 'orange', 'e': 'red'}
    
    for grade in ['a', 'b', 'c', 'd', 'e']:
        fig.add_trace(go.Bar(
            x=data.index,
            y=data[grade],
            name=grade,
            text=data[grade],
            textposition='auto',
            marker_color=colors[grade],  # set color for each grade
        ))
    
    fig.update_layout(
        title='Number of products per Eco-Score per Brand',
        xaxis_title='Brand',
        yaxis_title='Number of products per score',
        barmode='group'
    )
    
    fig.update_yaxes(type='log')  # set y-axis to logarithmic scale

    return fig


def calculatedscore_brand_chart(df, weight_eco=0.5):
    data_eco = df.groupby('brands')['off:ecoscore_grade'].value_counts().unstack().fillna(0)
    # normalize it
    data_eco = data_eco.div(data_eco.sum(axis=1), axis=0)
    data_eco = data_eco['a']

    data_nutri = df.groupby('brands')['off:nutriscore_grade'].value_counts().unstack().fillna(0)
    # normalize it
    data_nutri = data_nutri.div(data_nutri.sum(axis=1), axis=0)
    data_nutri = data_nutri['a']

    data_calc = (data_eco*weight_eco + data_nutri*(1-weight_eco))

    data_calc.sort_values(ascending=False, inplace=True)
    data = data_calc.head(20)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data.index,
        y=data,
        name='Average of normalized counts',
        text=data,
        textposition='auto',
        marker_color='blue',  # set color for the bar
    ))

    fig.update_layout(
        title='Average of normalized counts of \'a\' grade per Brand',
        xaxis_title='Brand',
        yaxis_title='Average of normalized counts',
        barmode='group'
    )

    return fig