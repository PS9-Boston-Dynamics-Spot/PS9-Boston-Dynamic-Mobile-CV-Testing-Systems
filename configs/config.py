from dotenv import load_dotenv
import os

# Pfad zur .env-Datei
from pathlib import Path
env_path = Path('env/.env')

load_dotenv(dotenv_path=env_path)

# Zugriff auf Variablen
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
api_key = os.getenv("API_KEY")

print (db_user)
print(api_key) 