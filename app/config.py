import os 
from dotenv import load_dotenv
load_dotenv()


class Settings:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "mistralai/devstral-2512:free")

settings = Settings()