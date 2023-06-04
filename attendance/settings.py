# setup environmental variables
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# database config
DATABASE = BASE_DIR / 'attendance.sqlite'

# REDIS config
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
