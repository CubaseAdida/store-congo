import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, "instance")

# créer le dossier si nécessaire
os.makedirs(instance_path, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        "sqlite:///" + os.path.join(instance_path, "stores.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False