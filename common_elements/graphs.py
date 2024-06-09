import plotly.graph_objects as go
from geopy.geocoders import ArcGIS
from geopy.distance import geodesic

def calculate_center_and_farthest(countries):
    geolocator = ArcGIS()

    lat = []
    lon = []
    locations = []

    for country in countries:
        location = geolocator.geocode(country)
        if location:
            lat.append(location.latitude)
            lon.append(location.longitude)
            locations.append(location)

    center_lat = sum(lat) / len(lat)
    center_lon = sum(lon) / len(lon)
    center = (center_lat, center_lon)

    farthest_distance = max(geodesic(center, (loc.latitude, loc.longitude)).miles for loc in locations)

    return center_lat, center_lon, farthest_distance



def create_map(countries):
    # calculate center of the map and distance to the farthest country
    if len(countries) <6:
        center_lat, center_lon, distance = calculate_center_and_farthest(countries)
    else:
        center_lat = 0
        center_lon = 0
        distance = 2500

    fig = go.Figure(data=go.Choropleth(
        locations = countries,
        z = [1]*len(countries),  # Assign the same value to all countries
        locationmode = 'country names',
        colorscale = 'Viridis',
        showscale = False,  # Hide the color scale
        marker_line_color = 'darkgray',  # line markers between countries
        marker_line_width = 0.5,  # line markers between countries
    ))
    if distance == 0:
        distance = 1
    fig.update_geos(
        projection_type = 'kavrayskiy7',  # type of projection
        landcolor = 'lightgray',  # color of the land
        lakecolor = 'white',  # color of lakes
        showcountries = True,  # show country borders
        countrycolor = 'darkgray',  # color of country borders
        center=dict(lat=center_lat, lon=center_lon),  # center of the map
        projection_scale=2500/distance,  # adjust the zoom level
    )

    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # transparent background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # transparent background
        margin=go.layout.Margin(l=0, r=0, b=0, t=0),
    )

    return fig

