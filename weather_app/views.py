from django.shortcuts import render
import requests
import datetime

def index(request):
    api_key = ''
    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'

    if request.method == 'POST':
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1 = fetch_weather_and_forecast(city1, api_key, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecasts2 = fetch_weather_and_forecast(city2, api_key, current_weather_url, forecast_url)
        else:
            weather_data2, daily_forecasts2 = None, None

        context = {
            'weather_data1': weather_data1,
            'daily_forecasts1': daily_forecasts1,
            'weather_data2': weather_data2,
            'daily_forecasts2': daily_forecasts2,
        }

        return render(request, 'weather_app/index.html', context)
    else:
        return render(request, 'weather_app/index.html')

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    # Fetch current weather data
    response = requests.get(current_weather_url.format(city, api_key)).json()
    
    # Check if the current weather response has an error
    if response.get('cod') != 200:
        print(f"Error fetching weather data for city: {city}")
        print(response)
        return None, None

    lat, lon = response['coord']['lat'], response['coord']['lon']
    
    # Fetch forecast data
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()
    
    # Check if the forecast response has an error
    if forecast_response.get('cod') != 200:
        print(f"Error fetching forecast data for city: {city}")
        print(forecast_response)
        return None, None

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    daily_forecasts = []
    # Ensure the 'daily' key exists in the forecast response
    if 'daily' in forecast_response:
        for daily_data in forecast_response['daily'][:5]:
            daily_forecasts.append({
                'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
                'min_temp': round(daily_data['temp']['min'] - 273.15, 2),
                'max_temp': round(daily_data['temp']['max'] - 273.15, 2),
                'description': daily_data['weather'][0]['description'],
                'icon': daily_data['weather'][0]['icon'],
            })
    else:
        print(f"No daily data available in forecast for city: {city}")

    return weather_data, daily_forecasts
