import requests
import os
from datetime import datetime, timedelta
from app import db
from app.models.weather import WeatherData, WeatherAlert

def get_weather_data(location):
    """Get current weather data from API and save to database"""
    api_key = os.environ.get('WEATHER_API_KEY')
    if not api_key:
        # Return mock data if no API key
        return create_mock_weather_data(location)
    
    try:
        # Using OpenWeatherMap API
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather_data = WeatherData(
                location=location,
                latitude=data['coord']['lat'],
                longitude=data['coord']['lon'],
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                wind_speed=data['wind']['speed'],
                wind_direction=data['wind'].get('deg', 0),
                precipitation=data['rain'].get('1h', 0) if 'rain' in data else 0,
                uv_index=0,  # Not available in basic API
                visibility=data.get('visibility', 0) / 1000,  # Convert to km
                cloud_cover=data['clouds']['all'],
                weather_condition=data['weather'][0]['main'].lower(),
                weather_description=data['weather'][0]['description']
            )
            
            db.session.add(weather_data)
            db.session.commit()
            
            check_weather_alerts(location)
            
            return weather_data
        else:
            return create_mock_weather_data(location)
            
    except Exception as e:
        print(f"Weather API error: {e}")
        return create_mock_weather_data(location)

def get_weather_forecast(location, days=7):
    """Get weather forecast for the next few days"""
    api_key = os.environ.get('WEATHER_API_KEY')
    if not api_key:
        return create_mock_forecast(location, days)
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric',
            'cnt': days * 8  # 8 forecasts per day (every 3 hours)
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            forecast = []
            daily_data = {}
            
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_data:
                    daily_data[date] = {
                        'date': date.isoformat(),
                        'temperatures': [],
                        'humidity': [],
                        'precipitation': 0,
                        'weather_condition': item['weather'][0]['main'].lower(),
                        'weather_description': item['weather'][0]['description']
                    }
                
                daily_data[date]['temperatures'].append(item['main']['temp'])
                daily_data[date]['humidity'].append(item['main']['humidity'])
                daily_data[date]['precipitation'] += item.get('rain', {}).get('3h', 0)
            
            # Calculate daily averages
            for date, data in daily_data.items():
                forecast.append({
                    'date': data['date'],
                    'temperature': {
                        'min': min(data['temperatures']),
                        'max': max(data['temperatures']),
                        'avg': sum(data['temperatures']) / len(data['temperatures'])
                    },
                    'humidity': sum(data['humidity']) / len(data['humidity']),
                    'precipitation': data['precipitation'],
                    'weather_condition': data['weather_condition'],
                    'weather_description': data['weather_description']
                })
            
            return forecast
        else:
            return create_mock_forecast(location, days)
            
    except Exception as e:
        print(f"Weather forecast API error: {e}")
        return create_mock_forecast(location, days)

def create_mock_weather_data(location):
    """Create mock weather data for testing"""
    import random
    
    weather_data = WeatherData(
        location=location,
        latitude=36.8065 + random.uniform(-0.1, 0.1),  # Tunisia coordinates
        longitude=10.1815 + random.uniform(-0.1, 0.1),
        temperature=random.uniform(15, 35),
        humidity=random.uniform(30, 80),
        pressure=random.uniform(1000, 1020),
        wind_speed=random.uniform(0, 15),
        wind_direction=random.uniform(0, 360),
        precipitation=random.uniform(0, 5),
        uv_index=random.uniform(0, 10),
        visibility=random.uniform(5, 15),
        cloud_cover=random.uniform(0, 100),
        weather_condition=random.choice(['clear', 'cloudy', 'rain', 'sunny']),
        weather_description=random.choice(['Clear sky', 'Partly cloudy', 'Light rain', 'Sunny'])
    )
    
    db.session.add(weather_data)
    db.session.commit()
    
    check_weather_alerts(location)
    
    return weather_data

def create_mock_forecast(location, days):
    """Create mock weather forecast for testing"""
    import random
    from datetime import date, timedelta
    
    forecast = []
    base_date = date.today()
    
    for i in range(days):
        forecast_date = base_date + timedelta(days=i)
        temp_min = random.uniform(10, 20)
        temp_max = random.uniform(20, 35)
        
        forecast.append({
            'date': forecast_date.isoformat(),
            'temperature': {
                'min': round(temp_min, 1),
                'max': round(temp_max, 1),
                'avg': round((temp_min + temp_max) / 2, 1)
            },
            'humidity': round(random.uniform(30, 80), 1),
            'precipitation': round(random.uniform(0, 10), 1),
            'weather_condition': random.choice(['clear', 'cloudy', 'rain', 'sunny']),
            'weather_description': random.choice(['Clear sky', 'Partly cloudy', 'Light rain', 'Sunny'])
        })
    
    return forecast

def check_weather_alerts(location):
    """Check for weather alerts and create them if needed"""
    weather_data = WeatherData.query.filter_by(location=location).order_by(WeatherData.recorded_at.desc()).first()
    
    if not weather_data:
        return
    
    alerts = []
    
    # Temperature alerts
    if weather_data.temperature < 0:
        alerts.append({
            'title': 'Frost Warning',
            'message': f'Frost risk detected. Temperature is {weather_data.temperature}°C. Protect sensitive crops.',
            'alert_type': 'warning',
            'severity': 'high'
        })
    elif weather_data.temperature > 40:
        alerts.append({
            'title': 'Heat Warning',
            'message': f'Extreme heat warning. Temperature is {weather_data.temperature}°C. Take precautions.',
            'alert_type': 'warning',
            'severity': 'high'
        })
    
    # Precipitation alerts
    if weather_data.precipitation > 20:
        alerts.append({
            'title': 'Heavy Rain Warning',
            'message': f'Heavy rainfall detected: {weather_data.precipitation}mm. Check drainage systems.',
            'alert_type': 'warning',
            'severity': 'medium'
        })
    
    # Wind alerts
    if weather_data.wind_speed > 25:
        alerts.append({
            'title': 'Strong Wind Warning',
            'message': f'Strong winds detected: {weather_data.wind_speed} m/s. Secure equipment and structures.',
            'alert_type': 'warning',
            'severity': 'medium'
        })
    
    # Create alerts in database
    for alert_data in alerts:
        # Check if alert already exists
        existing_alert = WeatherAlert.query.filter_by(
            title=alert_data['title'],
            location=location,
            is_active=True
        ).first()
        
        if not existing_alert:
            alert = WeatherAlert(
                title=alert_data['title'],
                message=alert_data['message'],
                alert_type=alert_data['alert_type'],
                severity=alert_data['severity'],
                location=location,
                latitude=weather_data.latitude,
                longitude=weather_data.longitude,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=24)
            )
            db.session.add(alert)
    
    db.session.commit()
