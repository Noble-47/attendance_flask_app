# setup environmental variables
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / 'attendance.sqlite' 
