from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/API")
def read_root():
    return {"Bienvenido al API de Recomendación"}

