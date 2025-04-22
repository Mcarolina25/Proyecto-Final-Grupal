from typing import Union
from funciones import get_table_curated_by_columns
from funciones import get_coordinates
from funciones import get_polygon
import pandas as pd
from fastapi import FastAPI

app = FastAPI()


@app.get("/API")
def read_root():
    map_coor=get_coordinates()
    print(map_coor)
    return f"""{map_coor}"""

@app.get("/API/{ciudad}")
def read_item(ciudad: str, q: Union[str, None] = None):
    print("la Ciudad es: ",ciudad)
    map_coor=get_coordinates(ciudad)
    polygon_coor = get_polygon(map_coor,30)
    
    return polygon_coor
