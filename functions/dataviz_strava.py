import gpxpy
import pandas as pd
from datetime import datetime,timezone,timedelta
import geopandas as gpd
from geopy.geocoders import Nominatim
import movingpandas as mpd
import contextily as ctx
import folium
import leafmap


def read_gpx(path):
    """
    returns a gpx object, given its local path
    """
    gpx_file = open(path, 'r', encoding='UTF-8')
    return gpxpy.parse(gpx_file)


def print_gpx_info(gpx_file):
    """
    prints info about creator and structure of gpx file
    """
    for count_t, track in enumerate(gpx_file.tracks):
        print("Creator:", gpx_file.creator)
        #print("\nTracks, Segments and Points")
        print("> Track", count_t)
        for count_s, segment in enumerate(track.segments):
            print("  > Segment", count_s, "has", len(segment.points), "points")


def create_geodf_from_segment(gpx_file, track_idx, segment_idx):
    """
    Input
        > gpx_file
        > track_idx     index of track (first layer)
        > segment_idx   index of segment (second layer)

    Output
        > pandas dataframe with information of required segment
    """
    data = []
    for point_idx, point in enumerate(gpx_file.tracks[track_idx].segments[segment_idx].points):
        data.append([
            point.longitude, 
            point.latitude,
            point.elevation,
            point.time]
            ) 

    columns_name = ['longitude', 'latitude', 'altitude', 'time'] 
    gpx_dataframe = pd.DataFrame(data, columns=columns_name)

    gpx_dataframe['time'] = gpx_dataframe['time'].apply(lambda x: x.replace(tzinfo=None))

    geo_df = gpd.GeoDataFrame(
        gpx_dataframe, 
        crs = 4326,
        geometry = gpd.points_from_xy(gpx_dataframe.longitude, gpx_dataframe.latitude, gpx_dataframe.altitude)
        )

    return geo_df


def get_total_distance(df):
    """
    Given a geodf with a 'time' column based on a gpx segment, it returns the total distance in meters (as html)
    """
    trajectory = mpd.Trajectory(df, traj_id="temp", t="time")
    dis = trajectory.get_length()
    return "<b>Distance</b>: %s m (%s km)" % (round(dis), round(dis/1000,2))


def get_travel_time(df):
    """
    Given a geodf with a 'time' column, it returns the total time required (as html)
    Note: the 'time' column MUST be sorted in ascending order
    """
    # obtain start and end times
    start = df["time"][0]
    end = df["time"][len(df["time"])-1]

    # get travel time
    travel_time = end - start
    travel_time_hours = str(timedelta(seconds=travel_time.seconds))

    # show res
    print_travel_time = travel_time_hours.split(':')
    return "<b>Time</b>: %sh %sm" % (print_travel_time[0], print_travel_time[1])


def get_altitude(df):
    """
    Given a geodf with an 'altitude' column, it returns the min and max value present (as html)
    """
    min_alt = min(df["altitude"])
    max_alt = max(df["altitude"])
    return "<b>Min Altitude</b>: %s meters<br><b>Max Altitude</b>: %s meters" % (min_alt, max_alt)


def get_start_end_locations(df):
    """
    Given a geodf with a 'geometry' column, it returns the first and last location (as html) 
    """

    # setup Nominatin
    geolocator = Nominatim(user_agent="udine_project")

    # obtain lat and lon for start point point
    lat_start = df["geometry"][0].y
    lon_start = df["geometry"][0].x
    latlon_start = str(lat_start) + "," + str(lon_start)

    # obtain lat and lon for end point
    last_idx = len(df["geometry"]) - 1
    lat_end = df["geometry"][last_idx].y
    lon_end = df["geometry"][last_idx].x
    latlon_end = str(lat_end) + "," + str(lon_end)

    # obtain info and print them
    start_location = geolocator.reverse(latlon_start)
    end_location = geolocator.reverse(latlon_end)

    return "<b>Start Location</b>: %s <br><b>End Location</b>: %s" % (start_location[0], end_location[0])


def extract_lat_lon_for_folium(geodf):
    """
    Given a geodf with a 'geometry' columns, 
    it returns a list of tuples with all the values of lat/lon
    """
    coords = []
    for idx,row in geodf.iterrows():
        lat = row["geometry"].y
        lon = row["geometry"].x
        coords.append( (lat,lon) )
    return coords


def create_folium_map(lat,lon,list_of_layers,list_of_routes):
    """
    Input:
        > lat               latitude of the location we want to display
        > lon               longitude of the location we want to display
        > list_of_layers    list of compatible layers that the map will have
        > list_of_routes    list of routes related information. Note that:
                                list_of_routes[i][0] -> geodf of the route
                                list_of_routes[i][1] -> title of the route (used in the popup)
                                list_of_routes[i][2] -> type of the route, can be [run|bike]

    Given latitude, longitude and a list of layers, it creates and returns a folium interactive map
    """

    # initialize folium map centered on coords (Udine)
    print("> Creating Base Map")
    base_map = folium.Map(location=[lat,lon])
    run_group = folium.FeatureGroup(name="Run")
    bike_group = folium.FeatureGroup(name="Bike")

    # add multiple layers
    print("> Adding multiple layers")
    for layer in list_of_layers:
        folium.TileLayer(layer).add_to(base_map)

    # add routes
    print("> Adding routes")
    for route in list_of_routes:

        # extract info of route
        geodf = route[0]
        title = route[1]
        route_type = route[2]

        # setup icon, style and color for popup
        if route_type == "run":
            icon = folium.features.CustomIcon('../images/icon_run.png', icon_size=(35,35))
            style='<style>body {background-color: #ecebe4;font-family: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";}</style>'
            color = "#DB504A"
        elif route_type == "bike":
            icon = folium.features.CustomIcon('../images/icon_bike.png', icon_size=(35,35))
            style='<style>body {background-color: #D8B3AB;font-family: system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";}</style>'
            color = "#19297C"
        else:
            print("ERROR: incorrect type provided")
            return 0

        # extract coords from geodf
        coords = extract_lat_lon_for_folium(geodf)

        # plot route
        route = folium.PolyLine(
            coords,
            color=color,
            weight=3,
            opacity=0.75)

        # obtain info about route
        distance = get_total_distance(geodf)
        travel_time = get_travel_time(geodf)
        altitude = get_altitude(geodf)
        start_end = get_start_end_locations(geodf)

        # prepare popup
        html = style + "<h3>" + title + "</h3>" + "<p>" + distance + "</p><p>" + travel_time + "</p><p>" + altitude + "</p><p>" + start_end + "</p>"
        iframe = folium.IFrame(html=html, width=320, height=200)

        # add marker
        marker = folium.Marker(
            location=[coords[0][0],coords[0][1]],
            popup=folium.Popup(iframe, max_width=800),
            tooltip=title,
            icon=icon
        )

        if route_type == "run":
            route.add_to(run_group)
            marker.add_to(run_group)
        elif route_type == "bike":
            route.add_to(bike_group)
            marker.add_to(bike_group)

        print("  - Added", route_type, "route:", title)

    # add groups to base_map
    run_group.add_to(base_map)
    bike_group.add_to(base_map)

    # create layer control
    folium.LayerControl().add_to(base_map)

    # return map
    print("> Interactive Map Created")
    return base_map
    