from typing import overload
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from signalwire_swaig.swaig import SWAIG, SWAIGArgument
import os
import requests
from dotenv import load_dotenv

# Try to load from .env but don't fail if it doesn't exist
try:
    load_dotenv(override=True)
except:
    pass

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "weather-sarcasm-secret-key")
swaig = SWAIG(app)

# Get API key from environment or session
def get_api_key():
    # First try getting from session
    api_key = session.get('WEATHER_API_KEY')
    # If not in session, try environment
    if not api_key:
        api_key = os.getenv("WEATHER_API_KEY")
    return api_key

# Update to use WeatherAPI.com 
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    api_key = get_api_key()
    error_message = None
    test_result = None
    
    # If it's a POST request, handle the form submission
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        
        # Test the API key with a simple request
        test_params = {
            "key": api_key,
            "q": "London"  # Test with London as a safe default
        }
        
        try:
            test_response = requests.get(BASE_URL, params=test_params)
            if test_response.status_code == 200:
                # Save API key in session
                session['WEATHER_API_KEY'] = api_key
                test_result = "API key tested successfully!"
            else:
                error_message = f"Invalid API key or API error: {test_response.status_code}"
        except Exception as e:
            error_message = f"Error testing API key: {str(e)}"
    
    # If we already have an API key, let the user know
    has_api_key = api_key is not None
    
    # Determine the full URL for the SWAIG endpoint
    # This handles cases where the app might be behind a proxy
    host = request.host
    scheme = request.scheme
    full_url = f"{scheme}://{host}/swaig"
    
    return render_template('index.html', 
                          has_api_key=has_api_key,
                          error_message=error_message,
                          test_result=test_result,
                          full_url=full_url)

@app.route('/clear-key', methods=['POST'])
def clear_key():
    if 'WEATHER_API_KEY' in session:
        session.pop('WEATHER_API_KEY')
    return redirect(url_for('home'))

@swaig.endpoint("Get weather with sarcasm",
    city=SWAIGArgument("string", "Name of the city"),
    state=SWAIGArgument("string", "Name of the state", required=False),
    country=SWAIGArgument("string", "Name of the country", required=False))
def get_weather(city, state=None, country=None, meta_data_token=None, meta_data=None):
    API_KEY = get_api_key()
    
    if not API_KEY:
        return "No API key set. Please visit the homepage to configure your Weather API key.", {}
    
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
            f"Oh wow, it's {temp_f}°F in {city_name}. Bet you didn't see that coming!",
            f"Humidity at {humidity}%. Your hair is going to love this!",
            f"Wind speed is {wind_mph} mph. Hold onto your hats, or don't, I'm not your mother!",
            f"Looks like {condition}. Guess you'll survive another day." 
        ]
        return " ".join(weather_info), {}
    
    return f"Oh great, {city} doesn't exist... or maybe you just can't spell? Try again!", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))