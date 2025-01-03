import os
from dotenv import load_dotenv

load_dotenv()

REMOTE_HOST = os.getenv("REMOTE_HOST")
ROOT_PATH = os.getenv("ROOT_PATH")
TRANSMISSION_PASSWORD = os.getenv("TRANSMISSION_PASSWORD")
TRANSMISSION_USERNAME = os.getenv("TRANSMISSION_USERNAME")
