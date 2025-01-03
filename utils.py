import shutil

from pydantic import BaseModel
from transmission_rpc import Client

from constants import (
    REMOTE_HOST,
    TRANSMISSION_USERNAME,
    TRANSMISSION_PASSWORD,
)

torrentClient = Client(
    host=REMOTE_HOST,
    port=9091,
    username=TRANSMISSION_USERNAME,
    password=TRANSMISSION_PASSWORD,
)


class MagnetLink(BaseModel):
    url: str


def indicatorStyle(status):
    if status == "seeding":
        return "flex w-3 h-3 me-3 bg-green-500 rounded-full"
    if status == "downloading":
        return "flex w-3 h-3 me-3 bg-blue-600 rounded-full"
    else:
        return "flex w-3 h-3 me-3 bg-gray-200 rounded-full"


def formatSize(num):
    if num < 1000000000:
        return f"{round(num / 1000000, 1)} MB"
    else:
        return f"{round(num / 1000000000, 2)} GB"


def getFree():
    total, used, free = shutil.disk_usage("/")
    return free
