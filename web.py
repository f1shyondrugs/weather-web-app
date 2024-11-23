from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

BASE_URL = "http://api.weatherapi.com/v1/current.json"
API_KEY = "2b1739b99f8e43e18b7200829242211"

def get_weather_condition(condition_code):
    if condition_code in [1000]:
        return "sunny"
    elif condition_code in range(1003, 1010):
        return "cloudy"
    elif condition_code in range(1150, 1202) or condition_code in range(1240, 1253):
        return "rainy"
    elif condition_code in range(1203, 1225) or condition_code in range(1255, 1269):
        return "snowy"
    elif condition_code in [1030, 1135, 1147]:
        return "cloudy"
    return "sunny"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    try:
        city = request.form.get('city', '')
        if not city:
            return jsonify({'error': 'City name is required'}), 400
        
        params = {
            'key': API_KEY,
            'q': city,
            'aqi': 'no'
        }
        
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        weather_data = response.json()
        
        condition = get_weather_condition(weather_data['current']['condition']['code'])
        
        processed_data = {
            'city': weather_data['location']['name'],
            'region': weather_data['location']['region'],
            'country': weather_data['location']['country'],
            'condition': condition,
            'temp': round(weather_data['current']['temp_c']),
            'humidity': weather_data['current']['humidity'],
            'wind': round(weather_data['current']['wind_kph']),
            'description': weather_data['current']['condition']['text'],
            'feels_like': round(weather_data['current']['feelslike_c'])
        }
        
        return jsonify(processed_data)
        
    except requests.exceptions.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch weather data. Please try again.'
        }), 500
    except KeyError as e:
        app.logger.error(f"Invalid response format: {str(e)}")
        return jsonify({
            'error': 'Invalid city name. Please check and try again.'
        }), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8989)