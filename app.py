from typing import overload
from flask import Flask, request, jsonify
from signalwire_swaig.core import SWAIG, SWAIGArgument
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
swaig = SWAIG(app)

API_KEY = os.getenv("API_NINJAS_KEY")
BASE_URL = "https://api.api-ninjas.com/v1/weather?"

@swaig.endpoint("Get weather with sarcasm",
    city=SWAIGArgument("string", "Name of the city"),
    state=SWAIGArgument("string", "Name of the state", required=False),
    country=SWAIGArgument("string", "Name of the country", required=False))
def get_weather(city, state=None, country=None, meta_data_token=None, meta_data=None):
    headers = {"X-Api-Key": API_KEY}
    api_url = f"{BASE_URL}city={city}"
    if state:
        api_url += f"&state={state}"
    if country:
        api_url += f"&country={country}"

    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        weather = response.json()
        temp_c = weather.get("temp", "unknown")
        # Convert temperature to Fahrenheit if we have a valid number
        temp = round((temp_c * 9/5) + 32) if isinstance(temp_c, (int, float)) else "unknown"
        humidity = weather.get("humidity", "unknown")
        wind_kmh = weather.get("wind_speed", "unknown")
        # Convert wind speed to mph if we have a valid number
        wind_speed = round(wind_kmh * 0.621371) if isinstance(wind_kmh, (int, float)) else "unknown"
        condition = weather.get("conditions", "clear skies")
        
        sarcasm = [
            f"Oh wow, it's {temp}°F in {city}. Bet you didn't see that coming!",
            f"Humidity at {humidity}%. Your hair is going to love this!",
            f"Wind speed is {wind_speed} mph. Hold onto your hats, or don't, I'm not your mother!",
            f"Looks like {condition}. Guess you'll survive another day." 
        ]
        return " ".join(sarcasm), {}
    
    return f"Oh great, {city} doesn't exist... or maybe you just can't spell? Try again!", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))