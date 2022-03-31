import os

class Config:
    WEATHER_API_BASE_URL: str
    WEATHER_API_KEY: str
    SLACK_BOT_TOKEN: str
    MESSAGES_TEMPLATES_PATH: str
    ENCRYPTED_EXPECTED_TOKEN: str
    
    def __init__(self):
        self.MESSAGES_TEMPLATES_PATH = "templates/messages"
        self.WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1"
        self.WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
        self.SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
        self.ENCRYPTED_EXPECTED_TOKEN = os.environ['KMS_ENCRYPTED_TOKEN']