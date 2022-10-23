import os
import subprocess

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from store import Session, Build

app = FastAPI()
WHEELS_DIR = os.getenv("WHEELS_DIR")
templates = Jinja2Templates(directory="templates")


class BuildBody(BaseModel):
    python: str
    tensorflow: str


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
def get_builds():
    session = Session()
    return {"builds": [{"id": b.id, "python": b.python, "tensorflow": b.tensorflow} for b in session.query(Build).all()]}


@app.post("/api/builds")
def start_build(request: Request, conf: BuildBody):
    subprocess.run(["docker", "build", ""])
    session = Session()
    build = Build(python=conf.python, tensorflow=conf.tensorflow)
    session.add(build)
    session.commit()
    return {""}
