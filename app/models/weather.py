from datetime import datetime
from app import db
from app.models.user import User

class WeatherData(db.Model):
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, default=0.0)
    uv_index = db.Column(db.Float, default=0.0)
    visibility = db.Column(db.Float, default=0.0)
    cloud_cover = db.Column(db.Float, default=0.0)
    weather_condition = db.Column(db.String(100), nullable=False)
    weather_description = db.Column(db.String(200))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_weather_icon(self):
        """Get appropriate weather icon based on condition"""
        condition_map = {
            'clear': 'sun',
            'sunny': 'sun',
            'cloudy': 'cloud',
            'overcast': 'cloud',
            'rain': 'cloud-rain',
            'drizzle': 'cloud-drizzle',
            'thunderstorm': 'cloud-lightning',
            'snow': 'snowflake',
            'fog': 'eye-slash',
            'mist': 'eye-slash'
        }
        condition = self.weather_condition.lower()
        for key, icon in condition_map.items():
            if key in condition:
                return icon
        return 'question-circle'
    
    def get_temperature_color(self):
        """Get color based on temperature"""
        if self.temperature < 0:
            return 'text-primary'  # Blue for cold
        elif self.temperature < 15:
            return 'text-info'     # Light blue for cool
        elif self.temperature < 25:
            return 'text-success'  # Green for mild
        elif self.temperature < 35:
            return 'text-warning'  # Orange for warm
        else:
            return 'text-danger'   # Red for hot
    
    def __repr__(self):
        return f'<WeatherData {self.location} - {self.temperature}°C>'

class WeatherAlert(db.Model):
    __tablename__ = 'weather_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.Enum('warning', 'watch', 'advisory', 'info'), default='info')
    severity = db.Column(db.Enum('low', 'moderate', 'high', 'extreme'), default='low')
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_severity_color(self):
        """Get color based on severity"""
        color_map = {
            'low': 'success',
            'moderate': 'warning',
            'high': 'danger',
            'extreme': 'dark'
        }
        return color_map.get(self.severity, 'info')
    
    def get_alert_icon(self):
        """Get appropriate icon based on alert type"""
        icon_map = {
            'warning': 'exclamation-triangle',
            'watch': 'eye',
            'advisory': 'info-circle',
            'info': 'info-circle'
        }
        return icon_map.get(self.alert_type, 'info-circle')
    
    def __repr__(self):
        return f'<WeatherAlert {self.title} - {self.severity}>'
    
def check_weather_alerts(weather):
    """Détecte les alertes météo à partir des données météo"""
    alerts = []

    frost_threshold = 3.0
    heat_threshold = 40.0
    wind_threshold = 50.0
    precipitation_threshold = 20.0

    if weather.temperature < frost_threshold:
        alerts.append("⚠️ Frost risk warning")
    if weather.temperature > heat_threshold:
        alerts.append("🔥 Heatwave warning")
    if weather.wind_speed > wind_threshold:
        alerts.append("💨 Strong wind warning")
    if weather.precipitation > precipitation_threshold:
        alerts.append("🌧️ Heavy rain warning")

    return alerts

