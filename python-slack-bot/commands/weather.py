import json
import re
import urllib3
from config import Config
from typing import Optional


class Weather:
    def __init__(self, params):
        self.config = Config()
        self.params = params
        self.user = self.params["user_name"][0]
        self.command = self.params["command"][0]
        self.user = self.params["user_id"][0]
        self.http = urllib3.PoolManager()
        self.location = "68701"

    def process(self):
        self.command_text = re.findall(r"[a-z]+", self.params["text"][0])
        self.location = re.findall(
            r"\d+|[a-z]+, [a-z]+", self.params["text"][0].lower()
        )
        if len(self.command_text) > 0:
            text = self.command_text[0]
            if text == "forecast":
                return self.forecast()
            if text == "alerts":
                return self.alerts()
            if text == "air":
                return self.air()
            if text == "help":
                return self.help()
            if text == "current":
                return self.current()

    def air(self):
        epa_severity = {
            1: "Good",
            2: "Moderate",
            3: "Unhealthy for sensitive groups",
            4: "Unhealthy",
            5: "Very Unhealthy",
            6: "Hazardous",
        }
        url = f"{self.config.WEATHER_API_BASE_URL}/current.json?key={self.config.WEATHER_API_KEY}&q={self.location[0]}&aqi=yes"
        r = self.http.request("GET", url)
        weather_data = json.loads(r.data.decode("utf-8"))
        air = weather_data["current"]["air_quality"]
        city = weather_data["location"]["name"]
        state = weather_data["location"]["region"]
        location = f"{city}, {state}"
        blocks = json.load(
            open(f"{self.config.MESSAGES_TEMPLATES_PATH}/air_quality.json")
        )
        air_quality_data = f"""```
        EPA Index: {epa_severity[air["us-epa-index"]]}
        Carbon Monoxide (μg/m3): {air["co"]}
        Ozone (μg/m3): {air["o3"]}
        Nitrogen dioxide (μg/m3): {air["no2"]}
        ```"""
        blocks[0]["text"]["text"] = blocks[0]["text"]["text"] + location
        blocks[2]["text"]["text"] = air_quality_data
        text = "Retrieving air quality data!"
        return self._send_slack_ephemeral(blocks, text)

    def alerts(self):
        url = f"{self.config.WEATHER_API_BASE_URL}/forecast.json?key={self.config.WEATHER_API_KEY}&q={self.location[0]}&days=1&aqi=no&alerts=yes"
        r = self.http.request("GET", url)
        weather_data = json.loads(r.data.decode("utf-8"))
        blocks = json.load(open(f"{self.config.MESSAGES_TEMPLATES_PATH}/alerts.json"))
        city = weather_data["location"]["name"]
        state = weather_data["location"]["region"]
        location = f"{city}, {state}"
        if len(weather_data["alerts"]["alert"]) == 0:
            text_1 = "No active alerts for " + location
            text_2 = "No alerts"
        else:
            text_1 = "Found the following alerts for " + location
            message = []
            for alert in weather_data["alerts"]["alert"]:
                message.append(
                    "Event: "
                    + alert["event"]
                    + " Effective: "
                    + alert["effective"]
                    + " Expires: "
                    + alert["expires"]
                    + "\n\n"
                )
            text_2 = f"""```{''.join(message)}```"""
        blocks[0]["text"]["text"] = text_1
        blocks[2]["text"]["text"] = text_2
        text = "Retrieving alert data!"
        return self._send_slack_ephemeral(blocks, text)

    def current(self):
        url = f"{self.config.WEATHER_API_BASE_URL}/current.json?key={self.config.WEATHER_API_KEY}&q={self.location[0]}&aqi=no"
        weather_data = json.loads(self._send_request("GET", url))
        blocks = json.load(open(f"{self.config.MESSAGES_TEMPLATES_PATH}/current.json"))
        city = weather_data["location"]["name"]
        state = weather_data["location"]["region"]
        location = f"{city}, {state}"
        text_2 = f"""```
        Temperature: {weather_data["current"]["temp_f"]}F
        Feels Like: {weather_data["current"]["feelslike_f"]}F
        Description: {weather_data["current"]["condition"]["text"]}
        Wind: {weather_data["current"]["wind_mph"]}mph
        Humidity: {weather_data["current"]["humidity"]}%
        UV Index: {weather_data["current"]["uv"]}
        Visibility: {weather_data["current"]["vis_miles"]}mi
        ```"""
        blocks[0]["text"]["text"] = blocks[0]["text"]["text"] + location
        blocks[2]["text"]["text"] = text_2
        text = "Retrieving alert data!"
        return self._send_slack_ephemeral(blocks, text)

    def help(self):
        blocks = json.load(open(f"{self.config.MESSAGES_TEMPLATES_PATH}/help.json"))
        text = "Help Request Received!"
        return self._send_slack_ephemeral(blocks, text)

    def _send_slack_ephemeral(self, blocks: dict, text: str):
        auth_token = self.config.SLACK_BOT_TOKEN
        headers = {
            "Authorization": "Bearer " + auth_token,
            "Content-Type": "application/json",
        }
        body = {
            "blocks": blocks,
            "channel": f"{self.user}",
            "text": text,
            "user": f"{self.user}",
        }
        encoded_body = json.dumps(body)
        url = "https://slack.com/api/chat.postEphemeral"
        r = self.http.request("POST", url, headers=headers, body=encoded_body)
        return r.data.decode("utf-8")
