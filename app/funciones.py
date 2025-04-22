import gcsfs
import pandas as pd
import bigframes.pandas as bpd
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import bigquery
from google.api_core.exceptions import NotFound


import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans
from geopy.distance import geodesic
from math import radians, degrees, sin, cos, atan2

PROJECT_ID = 'acme-987654'
LOCATION = "southamerica-east1" 
service_account_path = 'acme-987654-c052039ac4cd.json'

bucket_name = "acme_storage"

dataset_curated = "Curated"

table_checkin_id = "CheckIn"
table_user_id = "User" 
table_business_id = "Business"
table_review_id ="Review"
table_sitios_id = "Sitios"

table_estados_california_id = "Sitios_California"
table_estados_carolina_id = "Sitios_Carolina_Sur"
table_estados_florida_id = "Sitios_Florida"
table_estados_Massachusetts_id = "Sitios_Massachusetts"
table_estados_Texas_id = "Sitios_Texas"
table_estados_Washington_id = "Sitios_Washington"
table_estados_Luisiana_id = "Sitios_Luisiana"

def get_table_curated_by_columns(table, columns,city):
    # Initialize BigQuery client
    client = bigquery.Client.from_service_account_json(service_account_path)

    # Define your query
    query = f"""
        SELECT {columns} FROM acme-987654.Curated.{table} where city = {city}
    """

    
    # Run the query
    print(query)
    query_job = client.query(query)
    df = query_job.to_dataframe()
    return df

def get_coordinates():
    # Create a map centered on Mexico City
    df = get_table_curated_by_columns("Estados")
    

    #map_mx = folium.Map(location=[29.954423,-90.0714173], zoom_start=12)

    # Define the polygon coordinates
    #polygon_coords = [df.to_numpy()]

    # Add a semi-transparent polygon to create a shadow effect
    #folium.Polygon(
    #    locations=polygon_coords,
    #    color="black",
    #    fill=True,
    #    fill_color="gray",
    #    fill_opacity=0.3  # Shadow transparency
    #).add_to(map_mx)

    # Display the map inside Jupyter Notebook
    #return map_mx
    #return ""
    print("Value: ",df.to_numpy())
    return df.to_numpy()

def get_coordinates(ciudad):
    # Create a map centered on Mexico City
    df_lat_long = get_table_curated_by_columns("Estados", "latitude, longitude",f"""'{ciudad}'""")
    
    # Combine latitude and longitude into a 2D array
    coordinates = np.vstack([df_lat_long.latitude, df_lat_long.longitude])

    # Perform Kernel Density Estimation (KDE)
    kde = gaussian_kde(coordinates)
    density = kde(coordinates)  # Calculate density for each point

    # Use KMeans to cluster the high-density points
    num_clusters = 1  # You can change this based on your needs
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(coordinates.T)  # .T transposes the array
    cluster_centers = kmeans.cluster_centers_

    # Recommended latitude and longitude (centroid of the cluster)
    recommended_latitude = cluster_centers[0, 0]
    recommended_longitude = cluster_centers[0, 1]
    print(f"Recommended Location: Latitude = {recommended_latitude}, Longitude = {recommended_longitude}")
    return [recommended_latitude, recommended_longitude]

# Function to calculate new coordinates
def add_distance(lat, lon, distance, bearing):
    
    
    # Earth radius (in meters)
    R = 6378137
    
    # Convert latitude and longitude from degrees to radians
    lat_rad = radians(lat)
    lon_rad = radians(lon)
    bearing_rad = radians(bearing)
    
    # Calculate new latitude and longitude
    new_lat = lat_rad + (distance / R) * cos(bearing_rad)
    new_lon = lon_rad + (distance / R) * sin(bearing_rad) / cos(lat_rad)
    
    # Convert back to degrees
    new_lat = degrees(new_lat)
    new_lon = degrees(new_lon)
    
    return new_lat, new_lon

def get_polygon(map_coor, distance_in_meters):

    # Define your starting latitude and longitude
    latitude = map_coor[0]
    longitude = map_coor[1]

    # Add 5 meters in different directions (e.g., bearings 0°, 90°, 180°, 270°)
    directions = ["North", "East", "South", "West"]
    bearings = [0, 90, 180, 270]

    polygon_coords = []
    for direction, bearing in zip(directions, bearings):
        new_lat, new_lon = add_distance(latitude, longitude, distance_in_meters, bearing)
        lat_long = [new_lat,new_lon]
        print(lat_long)
        polygon_coords.append(lat_long)
    print(polygon_coords)

    return polygon_coords



