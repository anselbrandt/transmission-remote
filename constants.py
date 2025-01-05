import os
from dotenv import load_dotenv

load_dotenv()

LOCAL_PATH = os.getenv("LOCAL_PATH")
REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_PATH = os.getenv("REMOTE_PATH")
ROOT_PATH = os.getenv("ROOT_PATH")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")
SSH_USER = os.getenv("SSH_USER")
TRANSMISSION_PASSWORD = os.getenv("TRANSMISSION_PASSWORD")
TRANSMISSION_USERNAME = os.getenv("TRANSMISSION_USERNAME")

commands = f"sshpass -p {SSH_PASSWORD} rsync -rP {SSH_USER}@{REMOTE_HOST}:{REMOTE_PATH} {LOCAL_PATH}".split(
    " "
)
