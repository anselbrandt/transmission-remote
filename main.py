import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Header, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import redis
from sse_starlette.sse import EventSourceResponse


from constants import ROOT_PATH
from utils import (
    formatSize,
    getFree,
    indicatorStyle,
    MagnetLink,
    torrentClient,
)

cache = redis.Redis(decode_responses=True)


app = FastAPI(root_path=ROOT_PATH)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, hx_request: Optional[str] = Header(None)):
    torrents = torrentClient.get_torrents()
    context = {
        "request": request,
        "rootPath": ROOT_PATH,
        "torrents": torrents,
        "indicatorStyle": indicatorStyle,
        "formatSize": formatSize,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/add")
async def add(magnetlink: MagnetLink):
    try:
        url = magnetlink.url
        res = torrentClient.add_torrent(url)
        return res.name
    except Exception as error:
        print(str(error))
        return str(error)


@app.delete("/delete/{id}")
async def delete(id, response: Response):
    try:
        torrentClient.remove_torrent(id, delete_data=True)
        response.status_code = status.HTTP_200_OK
        return response
    except Exception as error:
        print(str(error))
        return str(error)


@app.get("/free", response_class=HTMLResponse)
async def free(request: Request):
    freepace = getFree()
    context = {
        "request": request,
        "rootPath": ROOT_PATH,
        "freespace": round(freepace / (2**30), 1),
    }
    return templates.TemplateResponse("freespace.html", context)


@app.get("/messages")
async def console(request: Request):
    async def publisher():
        try:
            while True:
                time = datetime.now()
                if cache.exists("messages"):
                    current = cache.get("messages")
                    messages = f"{current}<div>{time}</div>"
                    cache.set("messages", messages, ex=60)
                    yield messages
                else:
                    cache.set("messages", f"<div>{str(time)}</div>", ex=60)
                    yield time
                await asyncio.sleep(1)
        except asyncio.CancelledError as error:
            print(error)

    return EventSourceResponse(publisher())
