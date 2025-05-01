from typing import overload
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from signalwire_swaig.swaig import SWAIG, SWAIGArgument
import os
import requests
import json
from dotenv import load_dotenv
from signalwire_swml.swml import SignalWireSWML  # Import SWML module
from signalwire_pom.pom import PromptObjectModel  # Import POM for structured prompts
import secrets

# Try to load from .env but don't fail if it doesn't exist
try:
    load_dotenv(override=True)
except:
    pass

app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    secret_key = secrets.token_hex(32)
app.secret_key = secret_key
swaig = SWAIG(app)

# Add a global variable for the weather API key
weather_api_key = None

def get_api_key():
    global weather_api_key
    return weather_api_key

# Update to use WeatherAPI.com 
BASE_URL = "http://api.weatherapi.com/v1/current.json"

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    global weather_api_key
    # Retrieve from session if available (for other values)
    space_name = session.get('SPACE_NAME')
    project_id = session.get('PROJECT_ID')
    token = session.get('TOKEN')
    call_address = session.get('CALL_ADDRESS')
    call_token = session.get('CALL_TOKEN')
    error_message = None
    test_result = None

    if request.method == 'POST':
        api_key = request.form.get('api_key')
        space_name = request.form.get('space_name')
        project_id = request.form.get('project_id')
        token = request.form.get('token')

        # Test the Weather API key with a simple request
        test_params = {
            "key": api_key,
            "q": "London"
        }
        try:
            test_response = requests.get(BASE_URL, params=test_params)
            if test_response.status_code == 200:
                # Now test SignalWire credentials using the correct endpoint
                sw_url = f"https://{space_name}/api/laml/2010-04-01/Accounts"
                from requests.auth import HTTPBasicAuth
                sw_auth = HTTPBasicAuth(project_id, token)
                sw_response = requests.get(sw_url, headers={"Accept": "application/json"}, auth=sw_auth)
                if sw_response.status_code == 200:
                    # Now create the external SWML handler
                    swml_url = f"https://{space_name}/api/fabric/resources/external_swml_handlers"
                    from random import choices
                    import string
                    random_name = 'AI Weather Workshop ' + ''.join(choices(string.ascii_letters, k=5))
                    primary_request_url = f"https://{request.host}/swml"
                    swml_payload = {
                        "name": random_name,
                        "used_for": "calling",
                        "primary_request_url": primary_request_url,
                        "primary_request_method": "POST"
                    }
                    swml_create = requests.post(swml_url, headers={"Content-Type": "application/json", "Accept": "application/json"}, auth=sw_auth, json=swml_payload)
                    if swml_create.status_code in (200, 201):
                        handler_id = swml_create.json().get('id')
                        # Get the address
                        addr_url = f"https://{space_name}/api/fabric/resources/external_swml_handlers/{handler_id}/addresses"
                        addr_resp = requests.get(addr_url, headers={"Accept": "application/json"}, auth=sw_auth)
                        if addr_resp.status_code == 200 and addr_resp.json().get('data'):
                            address = addr_resp.json()['data'][0]['channels']['audio']
                            address_id = addr_resp.json()['data'][0]['id']
                            # Create a guest token
                            import time
                            expire_at = int(time.time()) + 3600 * 24  # 24 hours from now
                            guest_token_url = f"https://{space_name}/api/fabric/guests/tokens"
                            guest_payload = {
                                "allowed_addresses": [address_id],
                                "expire_at": expire_at
                            }
                            guest_token_resp = requests.post(guest_token_url, headers={"Content-Type": "application/json", "Accept": "application/json"}, auth=sw_auth, json=guest_payload)
                            if guest_token_resp.status_code in (200, 201):
                                call_token = guest_token_resp.json().get('token')
                                # Save all values in session (except weather_api_key)
                                weather_api_key = api_key
                                session['WEATHER_API_KEY'] = weather_api_key
                                session['SPACE_NAME'] = space_name
                                session['PROJECT_ID'] = project_id
                                session['TOKEN'] = token
                                session['CALL_ADDRESS'] = address
                                session['CALL_TOKEN'] = call_token
                                test_result = "Configuration saved, all credentials tested, and call widget is ready!"
                                call_address = address
                            else:
                                error_message = f"Failed to create guest token: {guest_token_resp.status_code} {guest_token_resp.text}"
                        else:
                            error_message = f"Failed to get call address: {addr_resp.status_code} {addr_resp.text}"
                    else:
                        error_message = f"Failed to create external SWML handler: {swml_create.status_code} {swml_create.text}"
                else:
                    error_message = f"SignalWire credentials test failed: {sw_response.status_code} {sw_response.text}"
            else:
                error_message = f"Invalid Weather API key or API error: {test_response.status_code}"
        except Exception as e:
            error_message = f"Error testing credentials: {str(e)}"

    # If we already have all values, let the user know
    has_api_key = all([get_api_key(), space_name, project_id, token, call_address, call_token])

    host = request.host
    full_url = f"https://{host}/swaig"
    swml_url = f"https://{host}/swml"

    return render_template(
        'index.html',
        has_api_key=has_api_key,
        error_message=error_message,
        test_result=test_result,
        full_url=full_url,
        swml_url=swml_url,
        api_key=get_api_key(),
        space_name=space_name,
        project_id=project_id,
        token=token,
        call_address=call_address,
        call_token=call_token
    )

@app.route('/clear-key', methods=['POST'])
def clear_key():
    global weather_api_key
    weather_api_key = None
    for key in ['WEATHER_API_KEY', 'SPACE_NAME', 'PROJECT_ID', 'TOKEN', 'CALL_ADDRESS', 'CALL_TOKEN']:
        if key in session:
            session.pop(key)
    return redirect(url_for('home'))

@swaig.endpoint("Get weather with sarcasm",
    city=SWAIGArgument("string", "Name of the city"),
    state=SWAIGArgument("string", "Name of the state", required=False),
    country=SWAIGArgument("string", "Name of the country", required=False))
def get_weather(city, state=None, country=None, meta_data_token=None, meta_data=None):
    api_key = get_api_key()
    if not api_key:
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
        "key": api_key,
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

# Helper function to build the POM for our weather agent
def build_weather_agent_prompt():
    pom = PromptObjectModel()
    
    # Overview section
    overview = pom.add_section("Overview", body="You are a highly opinionated AI weather assistant with a sharp wit and a knack for sarcasm.")
    
    # Personality section
    personality = pom.add_section("Personality", body="Your job is to provide accurate weather forecasts while keeping users entertained with snarky, humorous, and sometimes downright sassy responses.")
    
    # Response Style section
    style = pom.add_section("Response Style", body="You must respond with factual weather data, but always lace your replies with clever remarks, dry humor, and a pinch of good-natured mockery. Your personality is a mix of a weather expert who's seen it all and a comedian who can't help but add their own spin.")
    
    # Instructions section
    instructions = pom.add_section("Instructions", body="Be witty, be funny, but always ensure the weather details remain precise. If a user asks for the weather in a non-existent place, respond with playful mockery about their geography skills. Keep it engaging, keep it snarky, and never be boring.")
    
    # Add bullets to the instructions section
    instructions.add_bullets([
        "Always greet the user and ask for the city they want weather for.",
        "Use the get_weather function to fetch real-time weather data.",
        "Deliver factual weather information with sarcastic commentary.",
        "If the user asks about a non-existent location, mock them gently about their geography knowledge."
    ])
    
    return pom.to_dict()

# SWML Handler - Generates the SWML for voice applications
@app.route('/swml', methods=['GET', 'POST'])
def swml_handler():
    # Determine the base URL for SWAIG endpoints
    host = request.host
    swaig_url = f"https://{host}/swaig"
    
    # Create a new SWML instance
    swml = SignalWireSWML(version="1.0.0")
    
    # Add standard applications
    swml.add_application("main", "answer")
    swml.add_application("main", "record_call", {
        "format": "wav",
        "stereo": True
    })
    
    # Include our get_weather function
    swml.add_aiinclude({
        "url": swaig_url,
        "functions": [
            "get_weather"
        ]
    })
    
    # Set AI language
    swml.add_ailanguage({
        "code": "en-US",
        "name": "English",
        "voice": "openai.alloy"  # Using OpenAI Alloy voice
    })
    
    # Add AI parameters
    swml.add_aiparams({
        "post_prompt_silence_ms": "1000",  # Wait 1 second after prompts
        "end_of_speech_timeout": "2000"
    })
    
    # Set AI post prompt
    swml.set_aipost_prompt({
        "temperature": 0.5,
        "text": "Summarize this conversation about weather in a sarcastic tone.",
        "top_p": 0.5
    })
    
    # Set AI prompt using POM
    swml.set_aiprompt({
        "temperature": 0.9,  # Higher temperature for more creativity
        "pom": build_weather_agent_prompt(),
        "top_p": 0.9
    })
    
    # Add the AI application to the main section
    swml.add_aiapplication("main")
    
    # Output as JSON
    swml_json = swml.render_json(ordered=True)
    
    # Return the SWML as JSON
    if request.method == 'GET':
        # If GET request, pretty-print the JSON for viewing in browser
        return '<pre>' + json.dumps(json.loads(swml_json), indent=2) + '</pre>'
    else:
        # For POST requests, return the JSON directly for API consumers
        return swml_json, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))