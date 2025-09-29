from datetime import datetime
from app import db

class IoTDevice(db.Model):
    __tablename__ = 'iot_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.Enum('sensor', 'actuator', 'gateway', 'camera'), nullable=False)
    sensor_type = db.Column(db.Enum('temperature', 'humidity', 'soil_moisture', 'light', 'ph', 'nutrient', 'camera', 'other'), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    mac_address = db.Column(db.String(17), unique=True)
    ip_address = db.Column(db.String(15))
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    battery_level = db.Column(db.Integer)  # 0-100
    firmware_version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    data_points = db.relationship('IoTData', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('IoTAlert', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_latest_data(self):
        """Get the latest data point from this device"""
        return self.data_points.order_by(IoTData.timestamp.desc()).first()
    
    def get_data_count(self):
        """Get total number of data points"""
        return self.data_points.count()
    
    def get_status_color(self):
        """Get color based on device status"""
        if not self.is_online:
            return 'danger'
        elif self.battery_level and self.battery_level < 20:
            return 'warning'
        else:
            return 'success'
    
    def __repr__(self):
        return f'<IoTDevice {self.name} - {self.device_type}>'

class IoTData(db.Model):
    __tablename__ = 'iot_data'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    quality_score = db.Column(db.Float, default=1.0)  # 0-1, data quality indicator
    
    # Foreign keys
    device_id = db.Column(db.Integer, db.ForeignKey('iot_devices.id'), nullable=False)
    
    def get_value_with_unit(self):
        """Get formatted value with unit"""
        return f"{self.value} {self.unit}"
    
    def __repr__(self):
        return f'<IoTData {self.device.name} - {self.value} {self.unit}>'

class IoTAlert(db.Model):
    __tablename__ = 'iot_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    alert_type = db.Column(db.Enum('threshold_exceeded', 'device_offline', 'battery_low', 'data_anomaly', 'maintenance_required'), nullable=False)
    severity = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    threshold_value = db.Column(db.Float)
    actual_value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    device_id = db.Column(db.Integer, db.ForeignKey('iot_devices.id'), nullable=False)
    
    def get_severity_color(self):
        """Get color based on severity"""
        color_map = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return color_map.get(self.severity, 'info')
    
    def get_alert_icon(self):
        """Get appropriate icon based on alert type"""
        icon_map = {
            'threshold_exceeded': 'exclamation-triangle',
            'device_offline': 'wifi',
            'battery_low': 'battery-quarter',
            'data_anomaly': 'chart-line',
            'maintenance_required': 'wrench'
        }
        return icon_map.get(self.alert_type, 'info-circle')
    
    def __repr__(self):
        return f'<IoTAlert {self.title} - {self.severity}>'

class IoTCommand(db.Model):
    __tablename__ = 'iot_commands'
    
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String(100), nullable=False)  # e.g., 'pump_on', 'pump_off', 'set_irrigation_time'
    parameters = db.Column(db.JSON)  # Additional command parameters
    status = db.Column(db.Enum('pending', 'sent', 'executed', 'failed'), default='pending')
    sent_at = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    response = db.Column(db.JSON)  # Device response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    device_id = db.Column(db.Integer, db.ForeignKey('iot_devices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    device = db.relationship('IoTDevice', backref='commands')
    user = db.relationship('User', backref='iot_commands')
    
    def get_status_color(self):
        """Get color based on command status"""
        color_map = {
            'pending': 'warning',
            'sent': 'info',
            'executed': 'success',
            'failed': 'danger'
        }
        return color_map.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<IoTCommand {self.command} - {self.status}>'
