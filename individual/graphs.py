import plotly.graph_objects as go
import numpy as np

def create_bar_chart(element, macro_not_prepared):
    # Filter out None or '' values
    filtered_macros = [macro for macro in macro_not_prepared if (not np.isnan(element[macro+'_value']) and element[macro+'_value'] != '' and element[macro+'_value'] != 0)]
    if len(filtered_macros) == 0:
        return None

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=filtered_macros,
        y=[element[macro+'_value'] for macro in filtered_macros],
    ))

    fig.update_layout(
        xaxis_title="Macros",
        yaxis_title="Value",
        showlegend=False
    )

    return fig