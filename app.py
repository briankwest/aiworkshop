from typing import overload
from flask import Flask, request, jsonify
from signalwire_swaig.core import SWAIG, SWAIGArgument
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
swaig = SWAIG(app)

# Update to use WeatherAPI.com 
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"

@swaig.endpoint("Get weather with sarcasm",
    city=SWAIGArgument("string", "Name of the city"),
    state=SWAIGArgument("string", "Name of the state", required=False),
    country=SWAIGArgument("string", "Name of the country", required=False))
def get_weather(city, state=None, country=None, meta_data_token=None, meta_data=None):
    # Build location query string
    location = city
    if state and country:
        location = f"{city},{state},{country}"
    elif state:
        location = f"{city},{state}"
    elif country:
        location = f"{city},{country}"
    
    # Set up parameters for WeatherAPI
    params = {
        "key": API_KEY,
        "q": location,
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        weather_data = response.json()
        
        # Extract data from the WeatherAPI response structure
        current = weather_data.get("current", {})
        location_data = weather_data.get("location", {})
        
        temp_c = current.get("temp_c", "unknown")
        temp_f = current.get("temp_f", "unknown")
        humidity = current.get("humidity", "unknown")
        wind_mph = current.get("wind_mph", "unknown")
        condition = current.get("condition", {}).get("text", "clear skies")
        city_name = location_data.get("name", city)
        
        weather_info = [
            f"Oh wow, it's {temp_f}°F in {city_name}. ",
            f"Humidity at {humidity}%. ",
            f"Wind speed is {wind_mph} mph.",
            f"Looks like {condition}." 
        ]
        return " ".join(weather_info), {}
    
    return f"Oh great, {city} doesn't exist... or maybe you just can't spell? Try again!", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))