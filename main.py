from subprocess import Popen, PIPE, run
from typing import Optional
import asyncio


from fastapi import BackgroundTasks, FastAPI, Request, Header, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
import redis


from constants import (
    cleanup_commands,
    local_commands,
    rsync_commands,
    ROOT_PATH,
)
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


def startRsync():
    with Popen(rsync_commands, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            if cache.exists("messages"):
                current = cache.get("messages")
                messages = f"{current}<div>{line}</div>"
                cache.set("messages", messages, ex=30)
            else:
                cache.set("messages", f"<div>{str(line)}</div>", ex=30)


def startLocalSync():
    with Popen(local_commands, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            cache.set("isSyncing", "true")
        cache.set("isSyncing", "false")


def startCleanup():
    run(cleanup_commands)


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


@app.get("/localcontrols", response_class=HTMLResponse)
async def controls(request: Request, response: Response):
    if cache.get("isSyncing") == "true":
        response.status_code = status.HTTP_200_OK
        return response
    else:
        context = {
            "request": request,
            "rootPath": ROOT_PATH,
        }
        return templates.TemplateResponse("localControls.html", context)


@app.post("/localsync")
async def localsync(background_tasks: BackgroundTasks, response: Response):
    background_tasks.add_task(startLocalSync)
    response.status_code = status.HTTP_200_OK
    return response


@app.post("/cleanup")
async def cleanup(background_tasks: BackgroundTasks, response: Response):
    background_tasks.add_task(startCleanup)
    response.status_code = status.HTTP_200_OK
    return response


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


@app.get("/controls", response_class=HTMLResponse)
async def controls(request: Request, response: Response):
    if cache.exists("messages"):
        response.status_code = status.HTTP_200_OK
        return response
    else:
        context = {
            "request": request,
            "rootPath": ROOT_PATH,
        }
        return templates.TemplateResponse("rsyncButton.html", context)


@app.get("/console", response_class=HTMLResponse)
async def console(request: Request, response: Response):
    if cache.exists("messages"):
        context = {
            "request": request,
            "rootPath": ROOT_PATH,
        }
        return templates.TemplateResponse("console.html", context)
    else:
        response.status_code = status.HTTP_200_OK
        return response


@app.post("/rsync", response_class=HTMLResponse)
async def rsync(background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(startRsync)
    context = {
        "request": request,
        "rootPath": ROOT_PATH,
    }
    return templates.TemplateResponse("console.html", context)


@app.get("/messages")
async def messages():
    async def publisher():
        try:
            while True:
                if cache.exists("messages"):
                    messages = cache.get("messages")
                    yield messages
                else:
                    yield ""
                await asyncio.sleep(0.5)
        except asyncio.CancelledError as error:
            print(error)

    return EventSourceResponse(publisher())
