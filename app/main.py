from typing import Union
from funciones import get_coordinates

import pandas as pd
from fastapi import FastAPI

app = FastAPI()


@app.get("/API")
def read_root():
    return f"""Bienvenido al API"""

@app.get("/API/{ciudad}")
def read_item(ciudad: str, q: Union[str, None] = None):
    print("la Ciudad es: ",ciudad)
    map_coor=get_coordinates(ciudad)
    return map_coor
