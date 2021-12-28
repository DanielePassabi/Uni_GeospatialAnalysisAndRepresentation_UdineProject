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

# Ignore warnings
warnings.filterwarnings("ignore")


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



def plot_udine_map(udine_geodf, udine_osm, list_of_places, custom_address="", plot_uni_routes=False, list_of_uni="all", save=False, save_path=""):
    """
    TODO: write function description
    """

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
            print(" - The location is within boundaries, adding Location to the Map")
            # plot the point
            location.plot(
                ax=base,
                color="#30B4C5",
                edgecolor="black",
                marker='D',
                markersize=2500,
                linewidth=4
            )

            # logic to show routes from custom address to universities, if requested
            if plot_uni_routes:

                print(" - Obtaining Closest Routes to required Universities")

                # create osmnx network
                nodes, edges = udine_osm.get_network(nodes=True)
                G = udine_osm.to_graph(nodes, edges, graph_type="networkx")
                nodes_for_route, edges_for_route = ox.graph_to_gdfs(G)

                # find closest point to custom address
                address_coords = (location["geometry"].y.values[0], location["geometry"].x.values[0])
                closest_point_to_address = ox.get_nearest_node(G, address_coords)

                # find closest points to required universities
                list_of_uni_closest_points = []

                if list_of_uni == "all":
                    list_of_uni == [
                        "Dipartimento di Scienze Giuridiche",
                        "Università degli Studi di Udine - Facoltà di Medicina e Chirurgia - Corsi di Laurea Area Sanitaria",
                        "Università degli Studi di Udine - Facoltà di Scienze della Formazione",
                        "Università degli Studi di Udine - Dipartimento di Area medica",
                        "Università degli Studi di Udine - Polo Scientifico dei Rizzi"
                    ]

                for idx,row in universities.iterrows():
                    uni_name = row["name"]                       
                    if uni_name in list_of_uni:
                        geom = row["geometry"]
                        lat = geom.y
                        lon = geom.x
                        coords = (lat, lon)
                        list_of_uni_closest_points.append(ox.get_nearest_node(G, coords))

                # find closest routes and plot them
                for uni_point in list_of_uni_closest_points:
                    
                    # obtain closest route
                    closest_route = ox.shortest_path(
                        G, 
                        closest_point_to_address, 
                        uni_point, 
                        weight='length'
                        )

                    # note: ox gives us the nodes id --> we want a LineString
                    route_nodes = nodes_for_route.loc[closest_route]
                    route_line = LineString(route_nodes['geometry'].tolist())
                    route_geodf = gpd.GeoDataFrame(geometry=[route_line], crs=ox.settings.default_crs)

                    # plot the route
                    route_geodf.plot(
                        ax=base,
                        color="#B33951",
                        edgecolor="black",
                        markersize=1000,
                        linewidth=10
                    )



        else:
            print(" - ATTENTION: the provided address was not within the boundaries of Udine. \n   No information was added to the map. Please check that the address you wrote is correct.")

    # save the plot, if requested
    if save:
        print("> Saving the image")
        plt.savefig(save_path)

    # print time of computation
    end = time.time()
    print("\n> Elapsed Time:", round(end - start,2), "seconds")