from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.course import Course, CourseEnrollment
from app.models.land import Land
from app.models.forum import ForumPost
from app.models.weather import WeatherData, WeatherAlert
from app.models.iot import IoTDevice, IoTAlert
from app.models.investment import Investment
from app.models.mentoring import MentoringSession
from sqlalchemy import func, desc

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard with overview statistics and recent activity"""
    
    # Get user statistics based on user type
    stats = {}
    
    if current_user.is_farmer():
        stats.update({
            'total_products': Product.query.filter_by(seller_id=current_user.id).count(),
            'active_listings': Product.query.filter_by(seller_id=current_user.id, is_available=True).count(),
            'total_sales': 0,  # TODO: Calculate from orders
            'enrolled_courses': CourseEnrollment.query.filter_by(user_id=current_user.id).count()
        })
    elif current_user.is_investor():
        stats.update({
            'total_investments': Investment.query.filter_by(farmer_id=current_user.id).count(),
            'active_proposals': 0,  # TODO: Calculate from investment proposals
            'total_invested': 0,  # TODO: Calculate from completed investments
            'land_listings': Land.query.filter_by(owner_id=current_user.id).count()
        })
    elif current_user.is_expert():
        stats.update({
            'total_courses': Course.query.filter_by(instructor_id=current_user.id).count(),
            'total_students': 0,  # TODO: Calculate from course enrollments
            'mentoring_sessions': MentoringSession.query.filter_by(mentor_id=current_user.id).count(),
            'forum_posts': ForumPost.query.filter_by(author_id=current_user.id).count()
        })
    
    # Get recent activity
    recent_products = Product.query.order_by(desc(Product.created_at)).limit(5).all()
    recent_courses = Course.query.filter_by(is_published=True).order_by(desc(Course.created_at)).limit(5).all()
    recent_land = Land.query.filter_by(is_available=True).order_by(desc(Land.created_at)).limit(5).all()
    recent_forum_posts = ForumPost.query.order_by(desc(ForumPost.created_at)).limit(5).all()
    
    # Get weather data for user's location
    weather_data = WeatherData.query.filter_by(location=current_user.location).order_by(desc(WeatherData.recorded_at)).first()
    
    # Get active weather alerts
    weather_alerts = WeatherAlert.query.filter_by(is_active=True).all()
    
    # Get IoT devices for farmers
    iot_devices = []
    iot_alerts = []
    if current_user.is_farmer():
        iot_devices = IoTDevice.query.filter_by(owner_id=current_user.id).all()
        iot_alerts = IoTAlert.query.filter_by(is_resolved=False).join(IoTDevice).filter(IoTDevice.owner_id == current_user.id).all()
    
    return render_template('dashboard/index.html',
                         stats=stats,
                         recent_products=recent_products,
                         recent_courses=recent_courses,
                         recent_land=recent_land,
                         recent_forum_posts=recent_forum_posts,
                         weather_data=weather_data,
                         weather_alerts=weather_alerts,
                         iot_devices=iot_devices,
                         iot_alerts=iot_alerts)

@dashboard_bp.route('/stats')
@login_required
def stats():
    """API endpoint for dashboard statistics"""
    
    stats = {}
    
    if current_user.is_farmer():
        stats = {
            'products': {
                'total': Product.query.filter_by(seller_id=current_user.id).count(),
                'active': Product.query.filter_by(seller_id=current_user.id, is_available=True).count(),
                'sold': 0  # TODO: Calculate from orders
            },
            'courses': {
                'enrolled': CourseEnrollment.query.filter_by(user_id=current_user.id).count(),
                'completed': CourseEnrollment.query.filter_by(user_id=current_user.id, is_completed=True).count()
            },
            'land': {
                'owned': Land.query.filter_by(owner_id=current_user.id).count(),
                'available': Land.query.filter_by(owner_id=current_user.id, is_available=True).count()
            }
        }
    elif current_user.is_investor():
        stats = {
            'investments': {
                'total': Investment.query.filter_by(farmer_id=current_user.id).count(),
                'active': Investment.query.filter_by(farmer_id=current_user.id, status='active').count(),
                'funded': Investment.query.filter_by(farmer_id=current_user.id, status='funded').count()
            },
            'land': {
                'invested': 0,  # TODO: Calculate from land investments
                'leased': 0  # TODO: Calculate from land leases
            }
        }
    elif current_user.is_expert():
        stats = {
            'courses': {
                'created': Course.query.filter_by(instructor_id=current_user.id).count(),
                'students': 0  # TODO: Calculate from course enrollments
            },
            'mentoring': {
                'sessions': MentoringSession.query.filter_by(mentor_id=current_user.id).count(),
                'requests': 0  # TODO: Calculate from mentoring requests
            },
            'community': {
                'posts': ForumPost.query.filter_by(author_id=current_user.id).count(),
                'comments': 0  # TODO: Calculate from forum comments
            }
        }
    
    return jsonify(stats)


@dashboard.route('/alerte')
def alerte():
    return render_template('alerte.html')  # vérifier le chemin exact dans templates/

