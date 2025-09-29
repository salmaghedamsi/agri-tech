from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import desc, and_
from app import db
from app.models.iot import IoTDevice, IoTData, IoTAlert, IoTCommand
from app.models.user import User

iot_bp = Blueprint('iot', __name__, url_prefix='/iot')

@iot_bp.route('/')
@login_required
def dashboard():
    """IoT Dashboard - Main monitoring interface"""
    devices = IoTDevice.query.filter_by(owner_id=current_user.id).all()
    
    # Get latest sensor readings for dashboard
    latest_data = {}
    for device in devices:
        latest = device.get_latest_data()
        if latest:
            latest_data[device.sensor_type] = {
                'value': latest.value,
                'unit': latest.unit,
                'timestamp': latest.timestamp,
                'device_name': device.name
            }
    
    # Get unresolved alerts
    alerts = IoTAlert.query.filter_by(is_resolved=False).join(IoTDevice).filter(
        IoTDevice.owner_id == current_user.id
    ).order_by(desc(IoTAlert.created_at)).limit(5).all()
    
    # Get recent commands
    recent_commands = IoTCommand.query.join(IoTDevice).filter(
        IoTDevice.owner_id == current_user.id
    ).order_by(desc(IoTCommand.created_at)).limit(10).all()
    
    return render_template('iot/dashboard.html', 
                         devices=devices,
                         latest_data=latest_data,
                         alerts=alerts,
                         recent_commands=recent_commands)

@iot_bp.route('/monitoring')
@login_required
def monitoring():
    """Advanced monitoring interface - Verdiva style"""
    # Get environmental sensors (temperature, humidity, soil moisture)
    temp_device = IoTDevice.query.filter_by(
        owner_id=current_user.id, 
        sensor_type='temperature'
    ).first()
    
    humidity_device = IoTDevice.query.filter_by(
        owner_id=current_user.id, 
        sensor_type='humidity'
    ).first()
    
    soil_device = IoTDevice.query.filter_by(
        owner_id=current_user.id, 
        sensor_type='soil_moisture'
    ).first()
    
    # Get latest readings
    latest_data = {
        'temp': 0,
        'humidity': 0,
        'soil': 0
    }
    
    if temp_device:
        temp_reading = temp_device.get_latest_data()
        if temp_reading:
            latest_data['temp'] = temp_reading.value
    
    if humidity_device:
        humidity_reading = humidity_device.get_latest_data()
        if humidity_reading:
            latest_data['humidity'] = humidity_reading.value
    
    if soil_device:
        soil_reading = soil_device.get_latest_data()
        if soil_reading:
            latest_data['soil'] = soil_reading.value
    
    # Get pump/actuator devices
    actuators = IoTDevice.query.filter_by(
        owner_id=current_user.id,
        device_type='actuator'
    ).all()
    
    return render_template('iot/monitoring.html', 
                         latest_data=latest_data,
                         actuators=actuators,
                         temp_device=temp_device,
                         humidity_device=humidity_device,
                         soil_device=soil_device)

# API Endpoints for IoT devices (similar to your original code)
@iot_bp.route('/api/data', methods=['POST'])
def receive_data():
    """Receive sensor data from IoT devices"""
    try:
        data = request.get_json()
        
        # Find device by MAC address or create if needed
        device_mac = data.get('mac_address', 'unknown')
        device = IoTDevice.query.filter_by(mac_address=device_mac).first()
        
        if not device:
            # Auto-register device (you may want to change this for security)
            device = IoTDevice(
                name=f"Auto Device {device_mac[-6:]}",
                device_type='sensor',
                location='Auto-detected',
                mac_address=device_mac,
                owner_id=current_user.id if current_user.is_authenticated else 1,  # Default to first user
                is_online=True,
                last_seen=datetime.utcnow()
            )
            db.session.add(device)
            db.session.flush()
        
        # Update device status
        device.is_online = True
        device.last_seen = datetime.utcnow()
        
        # Store sensor data
        for sensor_type, value in data.items():
            if sensor_type in ['temp', 'temperature']:
                # Create/update temperature device
                temp_device = IoTDevice.query.filter_by(
                    mac_address=device_mac,
                    sensor_type='temperature'
                ).first()
                
                if not temp_device:
                    temp_device = IoTDevice(
                        name=f"Temperature Sensor {device_mac[-6:]}",
                        device_type='sensor',
                        sensor_type='temperature',
                        location=device.location,
                        mac_address=device_mac,
                        owner_id=device.owner_id,
                        is_online=True,
                        last_seen=datetime.utcnow()
                    )
                    db.session.add(temp_device)
                    db.session.flush()
                
                # Store data
                data_point = IoTData(
                    device_id=temp_device.id,
                    value=float(value),
                    unit='°C'
                )
                db.session.add(data_point)
            
            elif sensor_type in ['humidity']:
                # Create/update humidity device
                humidity_device = IoTDevice.query.filter_by(
                    mac_address=device_mac,
                    sensor_type='humidity'
                ).first()
                
                if not humidity_device:
                    humidity_device = IoTDevice(
                        name=f"Humidity Sensor {device_mac[-6:]}",
                        device_type='sensor',
                        sensor_type='humidity',
                        location=device.location,
                        mac_address=device_mac,
                        owner_id=device.owner_id,
                        is_online=True,
                        last_seen=datetime.utcnow()
                    )
                    db.session.add(humidity_device)
                    db.session.flush()
                
                # Store data
                data_point = IoTData(
                    device_id=humidity_device.id,
                    value=float(value),
                    unit='%'
                )
                db.session.add(data_point)
            
            elif sensor_type in ['soil', 'soil_moisture']:
                # Create/update soil moisture device
                soil_device = IoTDevice.query.filter_by(
                    mac_address=device_mac,
                    sensor_type='soil_moisture'
                ).first()
                
                if not soil_device:
                    soil_device = IoTDevice(
                        name=f"Soil Sensor {device_mac[-6:]}",
                        device_type='sensor',
                        sensor_type='soil_moisture',
                        location=device.location,
                        mac_address=device_mac,
                        owner_id=device.owner_id,
                        is_online=True,
                        last_seen=datetime.utcnow()
                    )
                    db.session.add(soil_device)
                    db.session.flush()
                
                # Store data
                data_point = IoTData(
                    device_id=soil_device.id,
                    value=float(value),
                    unit='units'
                )
                db.session.add(data_point)
        
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@iot_bp.route('/api/data/latest')
def get_latest_data():
    """Get latest sensor readings"""
    try:
        # Default values
        latest_data = {
            'temp': 24.5,
            'humidity': 65.0,
            'soil': 1850
        }
        
        if current_user.is_authenticated:
            # Get real data from user's devices
            temp_device = IoTDevice.query.filter_by(
                owner_id=current_user.id,
                sensor_type='temperature'
            ).first()
            
            if temp_device:
                temp_reading = temp_device.get_latest_data()
                if temp_reading:
                    latest_data['temp'] = temp_reading.value
            
            humidity_device = IoTDevice.query.filter_by(
                owner_id=current_user.id,
                sensor_type='humidity'
            ).first()
            
            if humidity_device:
                humidity_reading = humidity_device.get_latest_data()
                if humidity_reading:
                    latest_data['humidity'] = humidity_reading.value
            
            soil_device = IoTDevice.query.filter_by(
                owner_id=current_user.id,
                sensor_type='soil_moisture'
            ).first()
            
            if soil_device:
                soil_reading = soil_device.get_latest_data()
                if soil_reading:
                    latest_data['soil'] = soil_reading.value
        
        return jsonify(latest_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@iot_bp.route('/api/command', methods=['GET', 'POST'])
@login_required
def handle_command():
    """Handle device commands"""
    if request.method == 'POST':
        try:
            command_data = request.get_json()
            action = command_data.get('action', 'none')
            device_id = command_data.get('device_id')
            
            # Find actuator device or create default
            if device_id:
                device = IoTDevice.query.filter_by(
                    id=device_id,
                    owner_id=current_user.id
                ).first()
            else:
                # Find first actuator device
                device = IoTDevice.query.filter_by(
                    owner_id=current_user.id,
                    device_type='actuator'
                ).first()
            
            if not device and action != 'none':
                # Create default pump actuator
                device = IoTDevice(
                    name="Water Pump",
                    device_type='actuator',
                    sensor_type='other',
                    location='Farm',
                    owner_id=current_user.id,
                    is_online=True,
                    last_seen=datetime.utcnow()
                )
                db.session.add(device)
                db.session.flush()
            
            if device:
                # Create command record
                command = IoTCommand(
                    device_id=device.id,
                    user_id=current_user.id,
                    command=action,
                    parameters=command_data,
                    status='sent',
                    sent_at=datetime.utcnow()
                )
                db.session.add(command)
                db.session.commit()
            
            return jsonify({'status': 'command set', 'action': action})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    else:
        # GET - Return latest command for device
        try:
            device_id = request.args.get('device_id')
            
            if device_id:
                device = IoTDevice.query.filter_by(
                    id=device_id,
                    owner_id=current_user.id
                ).first()
            else:
                device = IoTDevice.query.filter_by(
                    owner_id=current_user.id,
                    device_type='actuator'
                ).first()
            
            if device:
                latest_command = IoTCommand.query.filter_by(
                    device_id=device.id
                ).order_by(desc(IoTCommand.created_at)).first()
                
                if latest_command:
                    return jsonify({
                        'action': latest_command.command,
                        'parameters': latest_command.parameters,
                        'status': latest_command.status
                    })
            
            return jsonify({'action': 'none'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@iot_bp.route('/devices')
@login_required
def devices():
    """Manage IoT devices"""
    devices = IoTDevice.query.filter_by(owner_id=current_user.id).all()
    return render_template('iot/devices.html', devices=devices)

@iot_bp.route('/alerts')
@login_required
def alerts():
    """View and manage IoT alerts"""
    alerts = IoTAlert.query.join(IoTDevice).filter(
        IoTDevice.owner_id == current_user.id
    ).order_by(desc(IoTAlert.created_at)).all()
    
    return render_template('iot/alerts.html', alerts=alerts)

@iot_bp.route('/alert/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Resolve an IoT alert"""
    alert = IoTAlert.query.join(IoTDevice).filter(
        IoTAlert.id == alert_id,
        IoTDevice.owner_id == current_user.id
    ).first_or_404()
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    
    db.session.commit()
    flash('Alert resolved successfully!', 'success')
    
    return redirect(url_for('iot.alerts'))