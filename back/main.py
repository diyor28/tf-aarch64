import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlalchemy.exc import IntegrityError

from src.build_model import Session, Build
from src.utils import wheels_list
from src.worker_threads import create_builders, get_logs


class BuildBody(BaseModel):
    python: str
    package: str
    type: str


if not os.path.exists('./logs'):
    os.mkdir('./logs')

if not os.path.exists('./build_files'):
    os.mkdir('./build_files')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

builders = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
def on_startup():
    builders.extend(create_builders())
    print("Started worker threads")


@app.on_event("shutdown")
def on_shutdown():
    for b in builders:
        b.stop()

    for b in builders:
        b.join()


@app.get("/wheels")
def read_wheels(request: Request):
    wheels = wheels_list()
    return templates.TemplateResponse("wheels.html", {"request": request, "wheels": wheels})


@app.get("/api/versions")
def get_versions():
    tf_versions = [
        "2.7.0",
        "2.7.1",
        "2.7.2",
        "2.7.3",
        "2.7.4",
        "2.7.x",
        "2.8.0",
        "2.8.1",
        "2.8.2",
        "2.8.3",
        "2.8.4",
        "2.8.x",
        "2.9.0",
        "2.9.1",
        "2.9.2",
        "2.9.3",
        "2.9.x",
        "2.10.0",
        "2.10.1",
        "2.10.x",
        "2.11.0",
        "2.11.1",
        "2.11.x",
        "2.12.0",
    ]
    tfx_versions = [
        "1.4.0",
        "1.4.x",
        "1.5.0",
        "1.5.x",
        "1.6.0",
        "1.6.x",
        "1.7.0",
        "1.7.x",
        "1.8.0",
        "1.8.x",
        "1.9.0",
        "1.9.x",
        "1.10.0",
        "1.10.x",
        "1.11.0",
        "1.11.x",
        "1.12.0",
        "1.12.x",
        "1.13.0",
        "1.13.x",
    ]

    return {"tensorflow": tf_versions, "tfx": tfx_versions}


@app.get("/api/builds")
def get_builds(t: str = ''):
    session = Session()
    query_list = session.query(Build).order_by(Build.update_at.desc())
    if t:
        query_list = query_list.filter(Build.type == t)
    result = []
    for b in query_list.all():
        result.append({
            "id": b.id,
            "python": b.python,
            "package": b.package,
            "status": b.status,
            "type": b.type,
            "logs": get_logs(b.id)
        })
    return result


@app.post("/api/builds")
async def start_build(conf: BuildBody):
    session = Session()
    build = Build(python=conf.python, package=conf.package, type=conf.type)

    try:
        session.add(build)
        session.commit()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="This python and tensorflow combination already exists")

    return {
        "id": build.id,
        "python": build.python,
        "package": build.package,
        "status": build.status,
        "type": conf.type,
        "logs": get_logs(build.id)
    }


@app.post("/api/builds/{filename}/cancel")
async def cancel_build(filename: str):
    session = Session()
    build = session.query(Build).get(filename)
    if not build:
        raise HTTPException(status_code=404, detail=f"No build for filename {filename} found")

    build.update_status(Build.Status.CANCELLED)
    session.add(build)
    session.commit()
    return {"ok": True}


@app.put("/api/builds/{filename}")
async def rebuild(conf: BuildBody, filename: str):
    session = Session()
    build = session.query(Build).get(filename)
    if not build:
        build = Build(python=conf.python, package=conf.package, type=conf.type)
    else:
        build.update_status(build.Status.PENDING)

    try:
        session.add(build)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="This python and tensorflow combination already exists")

    return {
        "id": build.id,
        "python": build.python,
        "package": build.package,
        "status": build.status,
        "type": build.type,
        "logs": get_logs(build.id)
    }


@app.delete("/api/builds/{filename}")
async def start_build(filename: str):
    session = Session()
    session.query(Build).filter_by(id=filename).delete()
    session.commit()
    logs_filename = f"./logs/{filename}.txt"
    if os.path.exists(logs_filename):
        os.remove(logs_filename)
    return {"ok": True}
