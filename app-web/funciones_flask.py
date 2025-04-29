
#import numpy as np
#import matplotlib.pyplot as plt
#from scipy.stats import gaussian_kde
#from sklearn.cluster import KMeans
#from geopy.distance import geodesic
from math import radians, degrees, sin, cos, atan2

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



