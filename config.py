import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_HOST = os.getenv('DEFAULT_HOST')
DEFAULT_PORT = os.getenv('DEFAULT_PORT')
DEFAULT_DB_NAME = os.getenv('DEFAULT_DB')
DEFAULT_DB_USER = os.getenv('DEFAULT_USER')
DEFAULT_DB_PASSWORD = os.getenv('DEFAULT_PASSWORD')
