import pandas as pd

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

    return (uni_df, location_df)
