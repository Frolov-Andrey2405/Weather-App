import datetime
import requests
from django.shortcuts import render
from django.conf import settings

def index(request):
    # API key moved to Django settings
    API_KEY = settings.OPENWEATHERMAP_API_KEY

    current_weather_url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'

    if request.method == 'POST':
        city1 = request.POST.get('city1')
        city2 = request.POST.get('city2')

        weather_data1, daily_forecast1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)

        if city2:
            weather_data2, daily_forecast2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_url)
        else:
            weather_data2, daily_forecast2 = None, None

        context = {
            'weather_data1': weather_data1,
            'daily_forecast1': daily_forecast1,
            'weather_data2': weather_data2,
            'daily_forecast2': daily_forecast2
        }

        return render(request, 'weather_app/index.html', context)

    else:
        return render(request, 'weather_app/index.html')


def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    
    # Use try-except to handle errors in case of missing coordinates
    try:
        lat, lon = response['coord']['lat'], response['coord']['lon']
    except KeyError:
        # If there are no coordinates, we return empty data
        return None, None

    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    # Add logging instead of print for debugging
    print(f"Forecast response: {forecast_response}")

    weather_data = {
        'city': city,
        'temperature': round(response['main']['temp'] - 273.15, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    daily_forecast = []

    for daily_data in forecast_response.get('daily', [])[:5]:
        daily_forecast.append({
            'day': datetime.datetime.fromtimestamp(daily_data['dt']).strftime('%A'),
            'min_temp': round(daily_data['temp']['min'] - 273.15, 2),
            'max_temp': round(daily_data['temp']['max'] - 273.15, 2),
            'description': daily_data['weather'][0]['description'],
            'icon': daily_data['weather'][0]['icon'],
        })
    return weather_data, daily_forecast
