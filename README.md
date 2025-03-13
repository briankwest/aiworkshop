# AI Weather Agent - Witty & Sarcastic Edition

## Table of Contents

1. [Introduction](#introduction)
2. [Overview](#overview)
3. [API Information](#api-information)
4. [Features & Capabilities](#features--capabilities)
5. [Environment Setup](#environment-setup)
6. [Functions & Implementation](#functions--implementation)
7. [Sample Queries & Responses](#sample-queries--responses)
8. [AI System Prompt](#ai-system-prompt)
9. [Conclusion](#conclusion)
10. [SignalWire Dashboard](#SignalWire-Dashboard-Settings)

---

## Introduction

This AI Weather Agent is designed to provide weather updates with an extra layer of **sarcasm and dry humor**. Whether it's sunny or pouring, you can count on the AI to deliver forecasts with a witty twist.

## Overview

- Built using **SignalWire AI Gateway (SWAIG)** and **Python**.
- Uses the **Weather API** from [API Ninjas](https://api-ninjas.com/api/weather).
- Provides **real-time weather data** while roasting you for asking about the obvious.
- Supports querying by **city, state, and/or country**.
- Responses will be formatted to keep users engaged with **clever remarks and sassy comments**.

## API Information

- **Base API URL:** `https://api.api-ninjas.com/v1/weather`
- **Expected Usage:**
  - **Get current weather:** Retrieves temperature, humidity, wind speed, and general conditions.
  - **Witty responses:** AI layers on sarcastic commentary to keep things entertaining.
- **Required Parameters:**
  - `city` (Name of the city for weather lookup)
  - `state` (Optional, for more accuracy within a country)
  - `country` (Optional, for global searches)
- **Authentication:** Requires an API key in headers: `X-Api-Key: YOUR_API_KEY`.

## Features & Capabilities

- **Weather Forecasting**: Retrieves real-time weather conditions.
- **Sarcastic Commentary**: AI provides an opinionated take on the forecast.
- **Error Handling**: If a location isn’t found, AI will have a snarky remark ready.
- **Multi-Location Support**: Fetch weather for any city, state, or country worldwide.

## Environment Setup

Ensure you have the following installed:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask signalwire-swaig requests python-dotenv
```

Create a `.env` file with your API keys:

```ini
# .env file
API_NINJAS_KEY=your_weather_api_key
PORT=5000
DEBUG=True
```

## Functions & Implementation

### Fetching Weather Data with Sarcasm

```python
from flask import Flask, request, jsonify
from signalwire_swaig.core import SWAIG, SWAIGArgument
import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
    location_query = f"city={city}"
    if state:
        location_query += f"&state={state}"
    if country:
        location_query += f"&country={country}"
    
    response = requests.get(BASE_URL + location_query, headers=headers)
    
    if response.status_code == 200:
        weather = response.json()
        temp = weather.get("temp", "unknown")
        humidity = weather.get("humidity", "unknown")
        wind_speed = weather.get("wind_speed", "unknown")
        condition = weather.get("conditions", "clear skies")
        
        sarcasm = [
            f"Oh wow, it's {temp}°C in {city}. Bet you didn't see that coming!",
            f"Humidity at {humidity}%. Your hair is going to love this!",
            f"Wind speed is {wind_speed} km/h. Hold onto your hats, or don't, I'm not your mother!",
            f"Looks like {condition}. Guess you’ll survive another day." 
        ]
        return " ".join(sarcasm), {}
    
    return f"Oh great, {city} doesn't exist... or maybe you just can't spell? Try again!", {}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=os.getenv('DEBUG', False))
```

## Sample Queries & Responses

### Example Query:

```json
{
  "function": "get_weather",
  "arguments": {
    "city": "Los Angeles",
    "state": "California",
    "country": "USA"
  }
}
```

### Example Response:

```json
{
  "response": "Oh wow, it's 27°C in Los Angeles. Bet you didn't see that coming! Humidity at 40%. Your hair is going to love this! Wind speed is 15 km/h. Hold onto your hats, or don't, I'm not your mother! Looks like clear skies. Guess you’ll survive another day."
}
```

## AI System Prompt

**System Prompt:**

*"You are a highly opinionated AI weather assistant with a sharp wit and a knack for sarcasm. Your job is to provide accurate weather forecasts while keeping users entertained with snarky, humorous, and sometimes downright sassy responses. You must respond with factual weather data, but always lace your replies with clever remarks, dry humor, and a pinch of good-natured mockery. Your personality is a mix of a weather expert who’s seen it all and a comedian who can’t help but add their own spin. Be witty, be funny, but always ensure the weather details remain precise. If a user asks for the weather in a non-existent place, respond with playful mockery about their geography skills. Keep it engaging, keep it snarky, and never be boring.
Greet the user with a and ask for the city they want the weather for.git "*

## Conclusion

The AI Weather Agent not only keeps you informed but also entertained. Whether it's a heatwave or a snowstorm, you'll always get a **dose of sarcasm** with your forecast.

Ready to launch? Fire up the bot and let the snark begin!


## SignalWire Dashboard Settings

1. Go to `Resources` left side tab.

<img src="https://github.com/user-attachments/assets/b5dd5804-207a-42b0-a22c-f4575bd3a225" alt="image" style="width:15%;">


2. Click the button `Add New`

<img src="https://github.com/user-attachments/assets/07eea87d-b2fc-4a92-8c7a-dfb97c462eaa" alt="image" style="width:15%;">


3. Choose `AI Agent`

<img src="https://github.com/user-attachments/assets/a0dc60a6-a871-402c-8ec7-07da15e8113e" alt="image" style="width:50%;">


4. Choose `Custom AI Agent`

<img src="https://github.com/user-attachments/assets/a5ee97ff-3d06-4c10-86a7-ba6c6422d99b" alt="image" style="width:50%;">


5. Click the `functions` tab

<img src="https://github.com/user-attachments/assets/041c2e7c-3187-4c6d-adf4-4e87c1f1f3af" alt="image" style="width:50%;">



6. Enter the URL in the search box. In this example we are using NGROK. https://admin:password@test.ngrok-free.app/swaig

<img src="https://github.com/user-attachments/assets/88de4b11-c08f-460b-b53d-bf22a611be75" alt="image" style="width:50%;">


7. Click the checkbox for `get_weather` then click the `create` button.


<img src="https://github.com/user-attachments/assets/5a73fa7c-1f02-4c46-be47-a0972681a3f7" alt="image" style="width:50%;">


8. Then click the `save` button.

<img src="https://github.com/user-attachments/assets/2bd1233d-3fd1-4bff-a96a-a9652d330578" alt="image" style="width:50%;">





