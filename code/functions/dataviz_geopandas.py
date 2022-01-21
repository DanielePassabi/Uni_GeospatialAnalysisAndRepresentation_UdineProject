# Import Libraries
import geopandas as gpd
import pygeos
import pyrosm
import matplotlib.pyplot as plt
import warnings
import time
import geopy
import osmnx as ox
from shapely.geometry import LineString
import pandas as pd

# Ignore warnings
warnings.filterwarnings("ignore")


def extract_info_from_dict(output_dict):
    """
    Input:
        > dictionary outputted from the function `plot_udine_map()`

    Output:
        > tuple with two dataframes
            - pos 0: df about universities
            - pos 1: df about other locations
    """
    list_of_places = []
    list_of_closest_name = []
    list_of_closest_dist = []
    list_of_tot_in_area = []

    for key,value in output_dict.items():

        if key == "university":
            uni_names = []
            uni_distances = []
            for k,v in value.items():
                uni_names.append(k.replace("Università degli Studi di Udine - ",""))
                uni_distances.append(v)

        else:
            list_of_places.append(key)
            list_of_closest_name.append(value["closest_name"])
            list_of_closest_dist.append(value["closest_distance"])
            list_of_tot_in_area.append(value["in_1km_area"])

    # create information dataframes

    # universities
    uni_df = pd.DataFrame(
        list(zip(uni_names, uni_distances)),
        columns = ['University', 'Distance (m)']
        )

    # other locations
    location_df = pd.DataFrame(
        list(zip(list_of_places, list_of_closest_name, list_of_closest_dist, list_of_tot_in_area)),
        columns = ['Location', 'Closest (name)', 'Closest (distance)', 'Total in 1km Area']
        )

    # return tuple with 2 res df
    return (uni_df, location_df)


def extract_data_from_OSM(osm, primary_filter, secondary_filter="all"):
    """
    Input:
        > pyrosm.OSM object
        > primary_filter        string in 'aerialway' | 'aeroway' | 'amenity' | 'boundary' | ...
        > secondary_filter      list of strings in the sub-categories of the primary filter
    Output:
        > geodataframe with requested data
    """
    # setup primary filter
    custom_filter = {primary_filter:True}

    # obtain the required data
    if secondary_filter == "all":
        pois = osm.get_pois(custom_filter = {primary_filter:True})
    else:
        pois = osm.get_pois(custom_filter = {primary_filter:secondary_filter})
    
    # and return it
    return pois


def count_points_in_area(points_geodf, area_geodf):
    """
    Input:
        > points_geodf      geodataframe with locations
        > area_geodf        geodataframe with one polygon (area)

    Output:
        > number of points in given area 
    """
    count = 0
    for location in points_geodf.geometry.values:
        if location.within(area_geodf.geometry[0]):
            count += 1
    return count


def update_dict_with_closest_loc(dict_to_update, loc_geodf, graph, start_location):
    """
    Input:
        > dict_to_update
        > loc_geodf
        > graph
        > start_location
    
    Output:
        > updated dictionary
    """

    # Setup placeholders
    dict_to_update["closest_name"] = ""
    dict_to_update["closest_distance"] = 100000

    # iterate over each location
    for idx,row in loc_geodf.iterrows():

        # obtain name and coords
        location_name = row["name"]                       
        geom = row["geometry"]
        lat = geom.y
        lon = geom.x
        coords = (lat, lon)
        closest_point = ox.get_nearest_node(graph, coords)

        # find shortest path length
        route = ox.shortest_path(
            graph, 
            start_location, 
            closest_point, 
            weight='length'
            )
        edge_lengths = ox.utils_graph.get_route_edge_attributes(graph, route, 'length')
                    
        # update dict if required
        if sum(edge_lengths) < dict_to_update["closest_distance"]:
            dict_to_update["closest_name"] = location_name
            dict_to_update["closest_distance"] = round(sum(edge_lengths),2)  

    return dict_to_update


def plot_udine_map(udine_geodf, udine_osm, list_of_places, custom_address="", show_km_range = False, plot_uni_routes=False, list_of_uni="all", save=False, save_path=""):
    """
    Input:
        > udine_geodf       geodataframe of Udine
        > udine_osm         pyrosm.OSM object based on Udine
        > list_of_places    list of places to plot on the map
                            possible values:  
                                - "university"
                                - "supermarket"
                                - "hospital"
                                - "eating place"
                                - "bicycle rental"
                                - "car rental"
                                - "bus station"
        > custom_address    Udine address
        > show_km_range     boolean value, if set to True shows on the map the 1km area around the given address
        > plot_uni_routes   boolean value, if set to True shows the closest universities routes (by length)
        > list_of_uni       list of universities on which to obtain information about the nearest route
                            possible values:
                                - "Dipartimento di Scienze Giuridiche"
                                - "Università degli Studi di Udine - Facoltà di Medicina e Chirurgia - Corsi di Laurea Area Sanitaria"
                                - "Università degli Studi di Udine - Facoltà di Scienze della Formazione"
                                - "Università degli Studi di Udine - Dipartimento di Area medica"
                                - "Università degli Studi di Udine - Polo Scientifico dei Rizzi"
        > save              boolean value, if set to True saves the plot as .jpg
        > save_path         path and name of plot to save
    """

    # keep track of time
    start = time.time()

    # obtain the buildings
    print("> Obtaining Buildings from OSM")
    udine_buildings = udine_osm.get_buildings()

    # obtain the streets
    print("> Obtaining Streets from OSM")
    udine_streets_driving = udine_osm.get_network(network_type="driving")
    udine_streets_walking = udine_osm.get_network(network_type="walking")
    
    # clip the buildings and streets obtained based on the map of Udine
    print("> Clipping Buildings and Streets")
    udine_buildings_clipped = gpd.clip(udine_buildings, udine_geodf.to_crs(epsg=4326))
    udine_streets_driving_clipped = gpd.clip(udine_streets_driving, udine_geodf.to_crs(epsg=4326))
    udine_streets_walking_clipped = gpd.clip(udine_streets_walking, udine_geodf.to_crs(epsg=4326))

    # create the base map of Udine
    print("> Generating Base Map")
    base = udine_geodf.to_crs(epsg=4326).plot(
        figsize=(100, 100),
        color="#B5CEA8",
        edgecolor="#7AA762",
        linewidth=10
        )

    # add buildings
    print("> Adding Buildings")
    udine_buildings_clipped.plot(
        ax=base,
        color="#DC9596"
        )

    # add streets
    print("> Adding Streets")
    udine_streets_driving_clipped.plot(ax=base, color="#1F1F1F", lw=0.8, alpha=0.8)
    udine_streets_walking_clipped.plot(ax=base, color="#3D3D3D", lw=0.6, alpha=0.8)

    # dictionary that will contain all the information required
    info_dict = {}

    # add additional elements, if requested

    if "university" in list_of_places:

        print("> Adding Universities")

        # obtain the data
        universities = extract_data_from_OSM(udine_osm, "amenity", ["university"])

        # by inspecting the results, we find the list of geometries to be kept 
        # (those corresponding to real university locations)
        uni_names = [
            "Dipartimento di Scienze Giuridiche",
            "Università degli Studi di Udine - Facoltà di Medicina e Chirurgia - Corsi di Laurea Area Sanitaria",
            "Università degli Studi di Udine - Facoltà di Scienze della Formazione",
            "Università degli Studi di Udine - Dipartimento di Area medica",
            "Università degli Studi di Udine - Polo Scientifico dei Rizzi"
        ]

        # keep the found values
        universities = universities.loc[universities["name"].isin(uni_names)]

        # we store the buildings separately
        universities_buildings = universities.loc[universities["osm_type"] != "node"]

        # and we find the representative points of the original dataset 
        universities["geometry"] = universities.representative_point().geometry

        # add universities to the plot
        universities_buildings.plot(
            ax=base,
            color="#D68586",
            markersize=1000,
            edgecolor="black",
            linewidth=2
        )

        # and their representative points
        universities.plot(
            ax=base,
            color="#FF9F1C",
            edgecolor="black",
            marker='*',
            markersize=5000,
            linewidth=4
        )

    if "supermarket" in list_of_places:

        print("> Adding Supermarket")

        # obtain the data
        supermarkets = extract_data_from_OSM(udine_osm, "shop", ["supermarket"])

        # extract the representative points from the polygons (if present)
        supermarkets["geometry"] = supermarkets.representative_point().geometry
        
        # add supermarkets to the plot
        supermarkets.plot(
            ax=base,
            color="#7776BC",
            edgecolor="black",
            markersize=250,
            linewidth=2
        )

    if "hospital" in list_of_places:

        print("> Adding Hospitals")

        # obtain the data
        hospitals = extract_data_from_OSM(udine_osm, "amenity", ["hospital"])
        hospitals["geometry"] = hospitals.representative_point().geometry

        # keep only selected rows
        hospitals_names = [
            'Pronto Soccorso Udine',
            'Policlinico Città di Udine Polo 1',
            'Policlinico Città di Udine Polo 2',
            'Ospedale Civile "Santa Maria della Misericordia"'
        ]
        hospitals = hospitals.loc[hospitals["name"].isin(hospitals_names)]

        # add hospitals to the plot
        hospitals.plot(
            ax=base,
            color="#8A2E2F",
            edgecolor="black",
            marker='P',
            markersize=1000,
            linewidth=3
        )

    if "eating place" in list_of_places:
        
        print("> Adding Eating Places")
        
        # obtain the data of both restaurants and fast_foods
        eating_places = extract_data_from_OSM(udine_osm, "amenity", ["restaurant","fast_food"])
        eating_places["geometry"] = eating_places.representative_point().geometry

        # add eating places to the plot
        eating_places.plot(
            ax=base,
            color="#03B591",
            edgecolor="black",
            marker='h',
            markersize=200,
            linewidth=2,
            alpha=0.75
        )

    if "bicycle rental" in list_of_places:
        
        print("> Adding Bicycle Rental Locations")
        
        # obtain the data
        bicycle_rental = extract_data_from_OSM(udine_osm, "amenity", ["bicycle_rental"])

        # add bicycle rental to the plot
        bicycle_rental.plot(
            ax=base,
            color="#FFFFFF",
            edgecolor="black",
            marker='>',
            markersize=450,
            linewidth=2
        )

    if "car rental" in list_of_places:
        
        print("> Adding Car Rental Locations")
        
        # obtain the data
        car_rental = extract_data_from_OSM(udine_osm, "amenity", ["car_rental"])

        # add car rental to the plot
        car_rental.plot(
            ax=base,
            color="#B8B8B8",
            edgecolor="black",
            marker='<',
            markersize=450,
            linewidth=2
        )

    if "bus station" in list_of_places:
        
        print("> Adding Bus Stations")
        
        # obtain the data
        bus_station = extract_data_from_OSM(udine_osm, "amenity", ["bus_station"])

        # keep only selected rows
        bus_station_names = [
            'Autostazione di Udine',
            'Terminal Studenti'
        ]
        bus_station = bus_station.loc[bus_station["name"].isin(bus_station_names)]
        bus_station["geometry"] = bus_station.representative_point().geometry

        # add bus station to the plot
        bus_station.plot(
            ax=base,
            color="#F8F272",
            edgecolor="black",
            marker='v',
            markersize=450,
            linewidth=2
        )

    # add custom address location to the map
    if custom_address != "":

        print("> Adding info about provided Address to the Map")

        # find coordinates
        print(" - Geocoding Address")
        location = gpd.tools.geocode(custom_address, provider="arcgis")

        # check that the coordinates are within the map of Udine
        print(" - Checking that the position found is within the boundaries of Udine")
        location_to_test = location.geometry.values[0]
        udine_for_test = udine_geodf.reset_index().to_crs(epsg=4326).geometry[0]

        if (location_to_test.within(udine_for_test)):

            # plot the point
            print(" - The location is within boundaries, adding Location to the Map")
            location.plot(
                ax=base,
                color="#30B4C5",
                edgecolor="black",
                marker='D',
                markersize=2500,
                linewidth=4
            )

            # logic to show routes from custom address to universities, if requested
            print(" - Obtaining Information about Required Locations")

            # create osmnx network
            nodes, edges = udine_osm.get_network(nodes=True)
            G = udine_osm.to_graph(nodes, edges, graph_type="networkx")
            nodes_for_route, edges_for_route = ox.graph_to_gdfs(G)

            # find closest point to custom address
            address_coords = (location["geometry"].y.values[0], location["geometry"].x.values[0])
            closest_point_to_address = ox.get_nearest_node(G, address_coords)

            # UNIVERSITY
            # find closest points to required universities
            list_of_uni_closest_points = []

            if list_of_uni == "all":
                list_of_uni = uni_names

            for idx,row in universities.iterrows():
                uni_name = row["name"]                       
                if uni_name in list_of_uni:
                    geom = row["geometry"]
                    lat = geom.y
                    lon = geom.x
                    coords = (lat, lon)
                    list_of_uni_closest_points.append([uni_name, ox.get_nearest_node(G, coords)])

            # find closest routes and distances
            uni_dict = {}
            for uni_point in list_of_uni_closest_points:
                
                # obtain closest route (by length)
                closest_route = ox.shortest_path(
                    G, 
                    closest_point_to_address, 
                    uni_point[1], 
                    weight='length'
                    )

                # obtain distance info
                edge_lengths = ox.utils_graph.get_route_edge_attributes(G, closest_route, 'length')
                uni_dict[uni_point[0]] = round(sum(edge_lengths),2)

                # note: ox gives us the nodes id --> we want a LineString
                route_nodes = nodes_for_route.loc[closest_route]
                route_line = LineString(route_nodes['geometry'].tolist())
                route_geodf = gpd.GeoDataFrame(geometry=[route_line], crs=ox.settings.default_crs)

                # plot the routes, if requested
                if plot_uni_routes:
                    route_geodf.plot(
                        ax=base,
                        color="#B33951",
                        edgecolor="black",
                        markersize=1000,
                        linewidth=10
                    )

            # update info_dict
            info_dict["university"] = uni_dict

            # OTHER LOCATIONS
            # add info about every requested location, considering a range of 1km

            # obtain area
            location_crs = location.to_crs(32632).geometry.values[0]                            # get values in 32632
            location_crs_1km = location_crs.buffer(1000)                                        # obtain the area of 1km
            location_crs_1km_geodf = gpd.GeoDataFrame(geometry=[location_crs_1km], crs=32632)   # create geodf for plot
            location_crs_1km_geodf = location_crs_1km_geodf.to_crs(epsg=4326)                   # go back to 4326

            # plot the area, if requested
            if show_km_range:
                location_crs_1km_geodf.plot(
                    ax=base,
                    color="#8CD9E3",
                    edgecolor="black",
                    linewidth=2,
                    alpha = 0.30
                )

            # SUPERMARKET
            if "supermarket" in list_of_places:

                print("    * Supermarkets")
                supermarket_dict = {}

                # points in 1km area
                count = count_points_in_area(supermarkets, location_crs_1km_geodf)
                supermarket_dict["in_1km_area"] = count

                # find closest to address
                supermarket_dict = update_dict_with_closest_loc(supermarket_dict, supermarkets, G, closest_point_to_address)                

                info_dict["supermarket"] = supermarket_dict

            # HOSPITAL
            if "hospital" in list_of_places:

                print("    * Hospitals")
                hospital_dict = {}

                # points in 1km area
                count = count_points_in_area(hospitals, location_crs_1km_geodf)
                hospital_dict["in_1km_area"] = count

                # find closest to address
                hospital_dict = update_dict_with_closest_loc(hospital_dict, hospitals, G, closest_point_to_address)

                info_dict["hospital"] = hospital_dict

            # EATING PLACE
            if "eating place" in list_of_places:

                print("    * Eating Places")
                eating_place_dict = {}

                # points in 1km area
                count = count_points_in_area(eating_places, location_crs_1km_geodf)
                eating_place_dict["in_1km_area"] = count

                # find closest to address
                eating_place_dict = update_dict_with_closest_loc(eating_place_dict, eating_places, G, closest_point_to_address)

                info_dict["eating_place"] = eating_place_dict

            # BICYCLE RENTAL
            if "bicycle rental" in list_of_places:

                print("    * Bicycle Rentals")
                bicycle_rental_dict = {}

                # points in 1km area
                count = count_points_in_area(bicycle_rental, location_crs_1km_geodf)
                bicycle_rental_dict["in_1km_area"] = count

                # find closest to address
                bicycle_rental_dict = update_dict_with_closest_loc(bicycle_rental_dict, bicycle_rental, G, closest_point_to_address)

                info_dict["bicycle_rental"] = bicycle_rental_dict

            # CAR RENTAL
            if "car rental" in list_of_places:

                print("    * Car Rentals")
                car_rental_dict = {}

                # points in 1km area
                count = count_points_in_area(car_rental, location_crs_1km_geodf)
                car_rental_dict["in_1km_area"] = count

                # find closest to address
                car_rental_dict = update_dict_with_closest_loc(car_rental_dict, car_rental, G, closest_point_to_address)

                info_dict["car_rental"] = car_rental_dict

            # BUS STATION
            if "bus station" in list_of_places:

                print("    * Bus Stations")
                bus_station_dict = {}

                # points in 1km area
                count = count_points_in_area(bus_station, location_crs_1km_geodf)
                bus_station_dict["in_1km_area"] = count

                # find closest to address
                bus_station_dict = update_dict_with_closest_loc(bus_station_dict, bus_station, G, closest_point_to_address)

                info_dict["bus_station"] = bus_station_dict

        else:
            print(" - ATTENTION: the provided address was not within the boundaries of Udine. \n   No information was added to the map. Please check that the address you wrote is correct.")

    # save the plot, if requested
    if save:
        print("> Saving the image")
        plt.savefig(save_path)

    # show total time of computation
    end = time.time()
    print("\n> Elapsed Time:", round(end - start,2), "seconds")

    # returning information
    return info_dict