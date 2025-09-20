from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.course import Course
from app.models.land import Land
from app.models.forum import ForumPost
from app.models.weather import WeatherData, WeatherAlert
from app.models.iot import IoTDevice, IoTData
from app.models.investment import Investment
from app.models.mentoring import Mentor
from app.models.chatbot import ChatSession, ChatMessage
from app.utils.chatbot import get_ai_response
from app.models.course import CourseEnrollment
from app.models.land import LandInvestment, LandLease
from sqlalchemy import desc, or_
import json
import time

api_bp = Blueprint('api', __name__)

@api_bp.route('/search')
def search():
    """Global search API"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify([])
    
    results = {
        'products': [],
        'courses': [],
        'land': [],
        'posts': [],
        'users': []
    }
    
    # Search products
    products = Product.query.filter(
        Product.is_available == True,
        or_(
            Product.name.contains(query),
            Product.description.contains(query)
        )
    ).limit(limit).all()
    
    for product in products:
        results['products'].append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'seller': product.seller.get_full_name(),
            'type': 'product'
        })
    
    # Search courses
    courses = Course.query.filter(
        Course.is_published == True,
        or_(
            Course.title.contains(query),
            Course.description.contains(query)
        )
    ).limit(limit).all()
    
    for course in courses:
        results['courses'].append({
            'id': course.id,
            'title': course.title,
            'price': course.price,
            'instructor': course.instructor.get_full_name(),
            'type': 'course'
        })
    
    # Search land
    land_listings = Land.query.filter(
        Land.is_available == True,
        or_(
            Land.title.contains(query),
            Land.description.contains(query),
            Land.location.contains(query)
        )
    ).limit(limit).all()
    
    for land in land_listings:
        results['land'].append({
            'id': land.id,
            'title': land.title,
            'location': land.location,
            'price_per_acre': land.price_per_acre,
            'area_acres': land.area_acres,
            'type': 'land'
        })
    
    # Search forum posts
    posts = ForumPost.query.filter(
        or_(
            ForumPost.title.contains(query),
            ForumPost.content.contains(query)
        )
    ).limit(limit).all()
    
    for post in posts:
        results['posts'].append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': post.author.get_full_name(),
            'type': 'post'
        })
    
    # Search users (experts and mentors only)
    users = User.query.filter(
        User.user_type.in_(['expert', 'mentor']),
        or_(
            User.username.contains(query),
            User.first_name.contains(query),
            User.last_name.contains(query)
        )
    ).limit(limit).all()
    
    for user in users:
        results['users'].append({
            'id': user.id,
            'name': user.get_full_name(),
            'username': user.username,
            'user_type': user.user_type,
            'type': 'user'
        })
    
    return jsonify(results)

@api_bp.route('/chat', methods=['POST'])
def chat():
    """AI Chatbot API"""
    data = request.get_json()
    message = data.get('message', '')
    session_id = data.get('session_id', '')
    language = data.get('language', 'en')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get or create chat session
    if session_id:
        session = ChatSession.query.filter_by(session_id=session_id).first()
    else:
        session = None
    
    if not session:
        session = ChatSession(
            session_id=session_id or f"session_{current_user.id if current_user.is_authenticated else 'anonymous'}_{int(time.time())}",
            language=language,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(session)
        db.session.commit()
    
    # Save user message
    user_message = ChatMessage(
        content=message,
        message_type='user',
        session_id=session.id
    )
    db.session.add(user_message)
    
    # Get AI response
    start_time = time.time()
    ai_response = get_ai_response(message, language, session.id)
    response_time = int((time.time() - start_time) * 1000)
    
    # Save AI response
    bot_message = ChatMessage(
        content=ai_response,
        message_type='bot',
        session_id=session.id,
        response_time_ms=response_time
    )
    db.session.add(bot_message)
    db.session.commit()
    
    return jsonify({
        'response': ai_response,
        'session_id': session.session_id,
        'response_time': response_time
    })

@api_bp.route('/weather/current')
def weather_current():
    """Current weather API"""
    location = request.args.get('location', 'Tunisia')
    
    weather_data = WeatherData.query.filter_by(location=location).order_by(desc(WeatherData.recorded_at)).first()
    
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

@api_bp.route('/weather/alerts')
def weather_alerts():
    """Weather alerts API"""
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

@api_bp.route('/iot/devices')
@login_required
def iot_devices():
    """User's IoT devices API"""
    devices = IoTDevice.query.filter_by(owner_id=current_user.id).all()
    
    devices_data = []
    for device in devices:
        latest_data = device.get_latest_data()
        devices_data.append({
            'id': device.id,
            'name': device.name,
            'device_type': device.device_type,
            'sensor_type': device.sensor_type,
            'location': device.location,
            'is_online': device.is_online,
            'battery_level': device.battery_level,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
            'latest_data': {
                'value': latest_data.value if latest_data else None,
                'unit': latest_data.unit if latest_data else None,
                'timestamp': latest_data.timestamp.isoformat() if latest_data else None
            }
        })
    
    return jsonify(devices_data)

@api_bp.route('/iot/device/<int:device_id>/data')
@login_required
def iot_device_data(device_id):
    """IoT device data API"""
    device = IoTDevice.query.filter_by(id=device_id, owner_id=current_user.id).first_or_404()
    
    # Get data points
    limit = request.args.get('limit', 100, type=int)
    hours = request.args.get('hours', 24, type=int)
    
    from datetime import datetime, timedelta
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    data_points = IoTData.query.filter(
        IoTData.device_id == device_id,
        IoTData.timestamp >= start_time
    ).order_by(desc(IoTData.timestamp)).limit(limit).all()
    
    data = []
    for point in data_points:
        data.append({
            'value': point.value,
            'unit': point.unit,
            'timestamp': point.timestamp.isoformat(),
            'quality_score': point.quality_score
        })
    
    return jsonify({
        'device': {
            'id': device.id,
            'name': device.name,
            'device_type': device.device_type,
            'sensor_type': device.sensor_type
        },
        'data': data
    })

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Dashboard statistics API"""
    stats = {}
    
    if current_user.is_farmer():
        stats = {
            'products': {
                'total': Product.query.filter_by(seller_id=current_user.id).count(),
                'active': Product.query.filter_by(seller_id=current_user.id, is_available=True).count()
            },
            'courses': {
                'enrolled': Course.query.join(CourseEnrollment).filter(CourseEnrollment.user_id == current_user.id).count()
            },
            'land': {
                'owned': Land.query.filter_by(owner_id=current_user.id).count(),
                'available': Land.query.filter_by(owner_id=current_user.id, is_available=True).count()
            },
            'iot_devices': {
                'total': IoTDevice.query.filter_by(owner_id=current_user.id).count(),
                'online': IoTDevice.query.filter_by(owner_id=current_user.id, is_online=True).count()
            }
        }
    elif current_user.is_investor():
        stats = {
            'investments': {
                'total': Investment.query.filter_by(farmer_id=current_user.id).count(),
                'active': Investment.query.filter_by(farmer_id=current_user.id, status='active').count()
            },
            'land': {
                'invested': LandInvestment.query.filter_by(investor_id=current_user.id).count(),
                'leased': LandLease.query.filter_by(tenant_id=current_user.id).count()
            }
        }
    elif current_user.is_expert():
        stats = {
            'courses': {
                'created': Course.query.filter_by(instructor_id=current_user.id).count(),
                'published': Course.query.filter_by(instructor_id=current_user.id, is_published=True).count()
            },
            'mentoring': {
                'sessions': Mentor.query.filter_by(user_id=current_user.id).first().sessions.count() if Mentor.query.filter_by(user_id=current_user.id).first() else 0
            },
            'community': {
                'posts': ForumPost.query.filter_by(author_id=current_user.id).count()
            }
        }
    
    return jsonify(stats)

@api_bp.route('/notifications')
@login_required
def notifications():
    """User notifications API"""
    # TODO: Implement notification system
    notifications = []
    
    # Weather alerts
    weather_alerts = WeatherAlert.query.filter_by(is_active=True).all()
    for alert in weather_alerts:
        notifications.append({
            'id': f"weather_{alert.id}",
            'type': 'weather_alert',
            'title': alert.title,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat()
        })
    
    # IoT alerts
    iot_alerts = IoTAlert.query.filter_by(is_resolved=False).join(IoTDevice).filter(IoTDevice.owner_id == current_user.id).all()
    for alert in iot_alerts:
        notifications.append({
            'id': f"iot_{alert.id}",
            'type': 'iot_alert',
            'title': alert.title,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.isoformat()
        })
    
    return jsonify(notifications)
