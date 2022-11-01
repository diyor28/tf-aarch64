import os
import asyncio

from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic.main import BaseModel
from sqlalchemy.exc import IntegrityError

from store import Session, Build
from utils import wheels_list, get_log_updates, get_filename, create_builders, readers


class BuildBody(BaseModel):
    python: str
    package: str
    type: str


if not os.path.exists('./logs'):
    os.mkdir('./logs')

app = FastAPI()
templates = Jinja2Templates(directory="templates")

builders = create_builders()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("shutdown")
def on_shutdown():
    for b in builders:
        b.stop()
        b.join()

    for r in readers:
        r.stop()
        r.join()


@app.get("/wheels")
def read_wheels(request: Request):
    wheels = wheels_list()
    return templates.TemplateResponse("wheels.html", {"request": request, "wheels": wheels})


async def send_log_updates(websocket: WebSocket):
    async for record in get_log_updates():
        print("sending log updates")
        await websocket.send_json({"event": "log_updates", "data": record})


async def get_logs():
    pass


@app.websocket("/ws")
async def handle_socket_messages(websocket: WebSocket):
    await websocket.accept()
    asyncio.create_task(send_log_updates(websocket))
    while True:
        data = await websocket.receive_json()
        print(data)
        # await websocket.send_text(f"Message text was: {data}")


@app.get("/api/builds")
def get_builds(t: str = ''):
    session = Session()
    query_list = session.query(Build)
    if t:
        query_list = query_list.filter(Build.type == t)
    return [{"id": b.id, "python": b.python, "package": b.package, "filename": b.filename, "type": b.type} for b in query_list.all()]


@app.post("/api/builds")
async def start_build(conf: BuildBody):
    session = Session()
    build = Build(python=conf.python, package=conf.package, type=conf.type, filename=get_filename(conf.python, conf.package, conf.type))
    try:
        session.add(build)
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="This python and tensorflow combination already exists")

    return {
        "id": build.id,
        "python": build.python,
        "package": build.package,
        "filename": build.filename,
        "type": conf.type
    }
