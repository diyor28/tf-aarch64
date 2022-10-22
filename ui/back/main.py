import os

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
WHEELS_DIR = os.getenv("WHEELS_DIR")
templates = Jinja2Templates(directory="templates")


def wheels_list() -> list[dict[str, str]]:
    wheel_files = [f for f in os.listdir(WHEELS_DIR) if os.path.isfile(os.path.join(WHEELS_DIR, f))]
    res = []
    for file in wheel_files:
        res.append({"name": file, "url": f"/builds/{file}"})
    return res


@app.get("/wheels")
def read_wheels(request: Request):
    wheels = wheels_list()
    return templates.TemplateResponse("wheels.html", {"request": request, "wheels": wheels})


@app.get("/api/builds")
def build_wheel(request: Request):
    return {""}


@app.post("/api/builds")
def build_wheel(request: Request):
    return {""}
