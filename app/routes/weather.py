from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.weather import WeatherData, WeatherAlert
from app.utils.weather import get_weather_data, get_weather_forecast
from sqlalchemy import desc, func
from datetime import datetime, timedelta

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/')
def index():
    """Weather dashboard"""
    location = request.args.get('location', current_user.location if current_user.is_authenticated else 'Tunisia')
    
    # Get current weather data
    weather_data = WeatherData.query.filter_by(location=location).order_by(desc(WeatherData.recorded_at)).first()
    
    # Get weather forecast (next 7 days)
    forecast_data = get_weather_forecast(location)
    
    # Get active weather alerts
    alerts = WeatherAlert.query.filter_by(is_active=True).all()
    
    # Get historical weather data for charts
    historical_data = WeatherData.query.filter_by(location=location).filter(
        WeatherData.recorded_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(WeatherData.recorded_at).all()
    
    return render_template('weather/index.html',
                         weather_data=weather_data,
                         forecast_data=forecast_data,
                         alerts=alerts,
                         historical_data=historical_data,
                         location=location)

@weather_bp.route('/api/current')
def api_current_weather():
    """API endpoint for current weather"""
    location = request.args.get('location', 'Tunisia')
    
    # Try to get from database first
    weather_data = WeatherData.query.filter_by(location=location).order_by(desc(WeatherData.recorded_at)).first()
    
    # If no recent data or data is older than 1 hour, fetch from API
    if not weather_data or (datetime.utcnow() - weather_data.recorded_at).seconds > 3600:
        weather_data = get_weather_data(location)
        if weather_data:
            from app.models.weather import save_weather_and_alerts
            save_weather_and_alerts(weather_data)

    
    if weather_data:
        return jsonify({
            'location': weather_data.location,
            'temperature': weather_data.temperature,
            'humidity': weather_data.humidity,
            'pressure': weather_data.pressure,
            'wind_speed': weather_data.wind_speed,
            'wind_direction': weather_data.wind_direction,
            'precipitation': weather_data.precipitation,
            'uv_index': weather_data.uv_index,
            'visibility': weather_data.visibility,
            'cloud_cover': weather_data.cloud_cover,
            'weather_condition': weather_data.weather_condition,
            'weather_description': weather_data.weather_description,
            'recorded_at': weather_data.recorded_at.isoformat()
        })
    
    return jsonify({'error': 'Weather data not available'}), 404

@weather_bp.route('/api/forecast')
def api_forecast():
    """API endpoint for weather forecast"""
    location = request.args.get('location', 'Tunisia')
    days = request.args.get('days', 7, type=int)
    
    forecast_data = get_weather_forecast(location, days)
    
    return jsonify(forecast_data)

@weather_bp.route('/api/alerts')
def api_alerts():
    """API endpoint for weather alerts"""
    location = request.args.get('location', '')
    
    query = WeatherAlert.query.filter_by(is_active=True)
    if location:
        query = query.filter(WeatherAlert.location.contains(location))
    
    alerts = query.order_by(desc(WeatherAlert.created_at)).all()
    
    alerts_data = []
    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'title': alert.title,
            'message': alert.message,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'location': alert.location,
            'start_time': alert.start_time.isoformat(),
            'end_time': alert.end_time.isoformat(),
            'created_at': alert.created_at.isoformat()
        })
    
    return jsonify(alerts_data)

@weather_bp.route('/alerts')
def alerts():
    """Weather alerts page"""
    page = request.args.get('page', 1, type=int)
    location = request.args.get('location', '')
    severity = request.args.get('severity', '')
    
    query = WeatherAlert.query.filter_by(is_active=True)
    
    if location:
        query = query.filter(WeatherAlert.location.contains(location))
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(desc(WeatherAlert.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('weather/alerts.html',
                         alerts=alerts,
                         location=location,
                         severity=severity)

@weather_bp.route('/historical')
def historical():
    """Historical weather data page"""
    location = request.args.get('location', current_user.location if current_user.is_authenticated else 'Tunisia')
    days = request.args.get('days', 30, type=int)
    
    # Get historical data
    start_date = datetime.utcnow() - timedelta(days=days)
    historical_data = WeatherData.query.filter(
        WeatherData.location == location,
        WeatherData.recorded_at >= start_date
    ).order_by(WeatherData.recorded_at).all()
    
    # Calculate statistics
    if historical_data:
        temperatures = [data.temperature for data in historical_data]
        humidities = [data.humidity for data in historical_data]
        precipitations = [data.precipitation for data in historical_data]
        
        stats = {
            'avg_temperature': sum(temperatures) / len(temperatures),
            'max_temperature': max(temperatures),
            'min_temperature': min(temperatures),
            'avg_humidity': sum(humidities) / len(humidities),
            'total_precipitation': sum(precipitations),
            'data_points': len(historical_data)
        }
    else:
        stats = None
    
    return render_template('weather/historical.html',
                         historical_data=historical_data,
                         stats=stats,
                         location=location,
                         days=days)

@weather_bp.route('/agricultural-advice')
def agricultural_advice():
    """Agricultural advice based on weather conditions"""
    location = request.args.get('location', current_user.location if current_user.is_authenticated else 'Tunisia')
    
    # Get current weather
    weather_data = WeatherData.query.filter_by(location=location).order_by(desc(WeatherData.recorded_at)).first()
    
    advice = []
    
    if weather_data:
        # Temperature-based advice
        if weather_data.temperature < 5:
            advice.append("⚠️ Frost risk: Protect sensitive crops with covers or move them indoors.")
        elif weather_data.temperature > 35:
            advice.append("🌡️ High temperature: Increase irrigation frequency and provide shade for crops.")
        elif 15 <= weather_data.temperature <= 25:
            advice.append("✅ Optimal temperature range for most crops.")
        
        # Humidity-based advice
        if weather_data.humidity < 30:
            advice.append("💧 Low humidity: Increase irrigation and consider mulching to retain moisture.")
        elif weather_data.humidity > 80:
            advice.append("🌧️ High humidity: Watch for fungal diseases, ensure good air circulation.")
        
        # Precipitation advice
        if weather_data.precipitation > 10:
            advice.append("🌧️ Heavy rain expected: Check drainage systems and protect crops from waterlogging.")
        elif weather_data.precipitation == 0 and weather_data.humidity < 40:
            advice.append("🌵 Dry conditions: Schedule irrigation and consider drought-resistant crops.")
        
        # Wind advice
        if weather_data.wind_speed > 20:
            advice.append("💨 Strong winds: Secure greenhouses and protect young plants.")
        
        # UV index advice
        if weather_data.uv_index > 8:
            advice.append("☀️ High UV index: Provide shade for sensitive plants and protect yourself from sun exposure.")
    
    return render_template('weather/agricultural_advice.html',
                         weather_data=weather_data,
                         advice=advice,
                         location=location)
