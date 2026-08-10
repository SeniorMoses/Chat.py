from dotenv import load_dotenv
from pathlib import Path
import os

env_path=Path(".env")
load_dotenv(env_path)

DBURL=os.getenv("db_url")
if not DBURL:
    raise ValueError("DBURL NOT LOADED")
    
SECRET=os.getenv("secret_key")
if not SECRET:
    raise ValueError("SECRET KEY NOT LOADED")
    
TOKEN_EXPIRE_MINUTES=20

TOKEN_EXPIRE_DAYS=16
