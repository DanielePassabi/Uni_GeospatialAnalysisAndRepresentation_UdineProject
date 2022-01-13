# **Exploring Udine and its Municipalities**

## **Course**

Geospatial Analysis and Representation for Data Science (2021-2022)

<br>

## **Aim of the Project**

The project focuses on Udine and its municipalities. It is mainly aimed at students interested in studying and moving to the city.

<br>

## **Structure**

The project is divided into three main parts:

1. *Static map of Udine, with universities and points of interest*

    It provides the main information about the city.

2. *Interactive map of Udine with real walking and cycling routes*

    The map is designed for those who want to train and test themselves.

3. *Geospatial analysis of average house prices and rents in the province of Udine*

    Interesting for those planning to move to Udine or its vicinity. It provides useful hints and considerations about the influence of each municipality on prices in neighbouring municipalities.

![Preview](images/preview_of_sections.png)

<br>

## **How to execute the code (Python)**

The following is a list of methods by which you can install the necessary tools to run the Python code on your system.

<br>

### **Solution 1: Anaconda environment**

- If you want to run the code on your own machine, it is strongly recommended to create an environment through [Anaconda](https://www.anaconda.com/) with `Python 3.9.9`.

- In the `environment` folder you will find the file `environment.yaml`, download it.

- You can recreate the environment using the command:

    ```
    conda env create --file environment.yaml
    ```

    Note that you don't need to specify the name, which is `GEO_PROJ` and is already contained within the `.yaml` file.

- You can now activate the environment with the command:

    ```
    conda activate GEO_PROJ
    ```

    This is usually recognised by the terminal, which will look like this:

    ```
    (GEO_PROJ) ...
    ```

- It is now possible to execute the code.

<br>

### **Solution 2: install packages using pip**

*Note*: this solution is **not** recommended, as it is highly likely that `pip` will not be able to install all packages correctly.

Some packages, for example, must be installed before others on a Windows environment.

If you still want to try, in the `environment` folder you will find the file `requirements.txt`. You can install the packages with the command:

```
pip install -r requirements.txt
```

<br>

### **Solution 3: install the packages manually**

If everything else has failed, you can try installing the packages individually, following the documentation:

- [pandas==1.3.5](https://pandas.pydata.org/getting_started.html)
- [geopandas==0.10.2](https://geopandas.org/en/stable/getting_started/install.html)
- [pygeos==0.12.0](https://pygeos.readthedocs.io/en/stable/installation.html)
- [pyrosm==0.6.1](https://pyrosm.readthedocs.io/en/latest/installation.html) $\rightarrow$ it **must** be installed after `geopandas` in Windows
- [matplotlib==3.5.1](https://matplotlib.org/stable/users/installing/index.html)
- [geopy==2.2.0](https://geopy.readthedocs.io/en/stable/#installation)
- [osmnx==1.1.2](https://osmnx.readthedocs.io/en/stable/)
- [gpxpy==1.5.0](https://pypi.org/project/gpxpy/)
- [movingpandas==0.8rc1](https://anaconda.org/conda-forge/movingpandas)
- [contextily==1.2.0](https://contextily.readthedocs.io/en/latest/)
- [folium==0.12.1.post1](https://python-visualization.github.io/folium/installing.html)
- [leafmap==0.7.0](https://leafmap.org/installation/)

<br>

### **Online Notebooks**

All the notebooks are freely explorable on this [webpage](https://danielepassabi.github.io/uni/geo/geo_project.html). The code is already executed and you do not need to download anything.

<br>

## **How to execute the code (R)**

The list of libraries needed to execute the R code follows:

- `dplyr`
- `rgdal`
- `spdep`
- `ggplot2`
- `stringr`

All packages can be installed with the following command:

```
install.packages("package name", dependencies = TRUE)
```

<br>

### **Online Notebook**

The notebook is freely explorable [here](https://danielepassabi.github.io/uni/geo/nb/3_Analysis_of_House_Sale_and_Rent_Cost_in_Province_of_Udine_R.html). The code is already executed and you do not need to download anything.
