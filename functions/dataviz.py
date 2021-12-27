# Import Libraries
import geopandas as gpd
import pygeos
import pyrosm
import matplotlib.pyplot as plt
import warnings
import time

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



def plot_udine_map(udine_geodf, udine_osm, list_of_places, save, save_path=""):
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
            markersize=250,
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
            markersize=250,
            linewidth=2
        )

    # save the plot, if requested
    if save:
        print("> Saving the image")
        plt.savefig(save_path)

    # print time of computation
    end = time.time()
    print("\n> Elapsed Time:", round(end - start,2), "seconds")