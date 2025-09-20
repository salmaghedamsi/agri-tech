from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.product import Product, ProductCategory
from app.models.course import Course
from app.models.land import Land
from app.models.forum import ForumPost, ForumCategory
from app.models.weather import WeatherAlert
from app.models.iot import IoTDevice, IoTAlert
from app.models.investment import Investment
from app.models.mentoring import Mentor
from sqlalchemy import desc, func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get statistics
    stats = {
        'total_users': User.query.count(),
        'farmers': User.query.filter_by(user_type='farmer').count(),
        'investors': User.query.filter_by(user_type='investor').count(),
        'experts': User.query.filter_by(user_type='expert').count(),
        'total_products': Product.query.count(),
        'active_products': Product.query.filter_by(is_available=True).count(),
        'total_courses': Course.query.count(),
        'published_courses': Course.query.filter_by(is_published=True).count(),
        'total_land_listings': Land.query.count(),
        'available_land': Land.query.filter_by(is_available=True).count(),
        'total_forum_posts': ForumPost.query.count(),
        'active_weather_alerts': WeatherAlert.query.filter_by(is_active=True).count(),
        'total_iot_devices': IoTDevice.query.count(),
        'online_iot_devices': IoTDevice.query.filter_by(is_online=True).count(),
        'total_investments': Investment.query.count(),
        'active_investments': Investment.query.filter_by(status='active').count(),
        'total_mentors': Mentor.query.count(),
        'available_mentors': Mentor.query.filter_by(is_available=True).count()
    }
    
    # Get recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    recent_products = Product.query.order_by(desc(Product.created_at)).limit(10).all()
    recent_courses = Course.query.order_by(desc(Course.created_at)).limit(10).all()
    recent_posts = ForumPost.query.order_by(desc(ForumPost.created_at)).limit(10).all()
    
    return render_template('admin/index.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_products=recent_products,
                         recent_courses=recent_courses,
                         recent_posts=recent_posts)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    page = request.args.get('page', 1, type=int)
    user_type = request.args.get('type', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    if user_type:
        query = query.filter_by(user_type=user_type)
    
    if search:
        query = query.filter(or_(
            User.username.contains(search),
            User.email.contains(search),
            User.first_name.contains(search),
            User.last_name.contains(search)
        ))
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html',
                         users=users,
                         user_type=user_type,
                         search=search)

@admin_bp.route('/user/<int:user_id>/toggle-status')
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    """Product management"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(or_(
            Product.name.contains(search),
            Product.description.contains(search)
        ))
    
    products = query.order_by(desc(Product.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = ProductCategory.query.all()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories,
                         category_id=category_id,
                         search=search)

@admin_bp.route('/product/<int:product_id>/toggle-status')
@login_required
@admin_required
def toggle_product_status(product_id):
    """Toggle product availability"""
    product = Product.query.get_or_404(product_id)
    
    product.is_available = not product.is_available
    db.session.commit()
    
    status = 'available' if product.is_available else 'unavailable'
    flash(f'Product {product.name} is now {status}.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Category management"""
    categories = ProductCategory.query.all()
    
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/add-category', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add new product category"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if name:
            category = ProductCategory(
                name=name,
                description=description
            )
            db.session.add(category)
            db.session.commit()
            
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin.categories'))
    
    return render_template('admin/add_category.html')

@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    """Course management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Course.query
    
    if search:
        query = query.filter(or_(
            Course.title.contains(search),
            Course.description.contains(search)
        ))
    
    courses = query.order_by(desc(Course.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/courses.html',
                         courses=courses,
                         search=search)

@admin_bp.route('/course/<int:course_id>/toggle-status')
@login_required
@admin_required
def toggle_course_status(course_id):
    """Toggle course published status"""
    course = Course.query.get_or_404(course_id)
    
    course.is_published = not course.is_published
    db.session.commit()
    
    status = 'published' if course.is_published else 'unpublished'
    flash(f'Course {course.title} is now {status}.', 'success')
    return redirect(url_for('admin.courses'))

@admin_bp.route('/land')
@login_required
@admin_required
def land():
    """Land listing management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Land.query
    
    if search:
        query = query.filter(or_(
            Land.title.contains(search),
            Land.description.contains(search),
            Land.location.contains(search)
        ))
    
    land_listings = query.order_by(desc(Land.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/land.html',
                         land_listings=land_listings,
                         search=search)

@admin_bp.route('/land/<int:land_id>/toggle-status')
@login_required
@admin_required
def toggle_land_status(land_id):
    """Toggle land availability"""
    land = Land.query.get_or_404(land_id)
    
    land.is_available = not land.is_available
    db.session.commit()
    
    status = 'available' if land.is_available else 'unavailable'
    flash(f'Land listing {land.title} is now {status}.', 'success')
    return redirect(url_for('admin.land'))

@admin_bp.route('/forum')
@login_required
@admin_required
def forum():
    """Forum management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = ForumPost.query
    
    if search:
        query = query.filter(or_(
            ForumPost.title.contains(search),
            ForumPost.content.contains(search)
        ))
    
    posts = query.order_by(desc(ForumPost.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/forum.html',
                         posts=posts,
                         search=search)

@admin_bp.route('/post/<int:post_id>/toggle-pin')
@login_required
@admin_required
def toggle_post_pin(post_id):
    """Toggle post pinned status"""
    post = ForumPost.query.get_or_404(post_id)
    
    post.is_pinned = not post.is_pinned
    db.session.commit()
    
    status = 'pinned' if post.is_pinned else 'unpinned'
    flash(f'Post {post.title} has been {status}.', 'success')
    return redirect(url_for('admin.forum'))

@admin_bp.route('/post/<int:post_id>/toggle-lock')
@login_required
@admin_required
def toggle_post_lock(post_id):
    """Toggle post locked status"""
    post = ForumPost.query.get_or_404(post_id)
    
    post.is_locked = not post.is_locked
    db.session.commit()
    
    status = 'locked' if post.is_locked else 'unlocked'
    flash(f'Post {post.title} has been {status}.', 'success')
    return redirect(url_for('admin.forum'))

@admin_bp.route('/weather-alerts')
@login_required
@admin_required
def weather_alerts():
    """Weather alert management"""
    page = request.args.get('page', 1, type=int)
    severity = request.args.get('severity', '')
    
    query = WeatherAlert.query
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(desc(WeatherAlert.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/weather_alerts.html',
                         alerts=alerts,
                         severity=severity)

@admin_bp.route('/iot-devices')
@login_required
@admin_required
def iot_devices():
    """IoT device management"""
    page = request.args.get('page', 1, type=int)
    device_type = request.args.get('type', '')
    
    query = IoTDevice.query
    
    if device_type:
        query = query.filter_by(device_type=device_type)
    
    devices = query.order_by(desc(IoTDevice.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/iot_devices.html',
                         devices=devices,
                         device_type=device_type)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard"""
    # User growth over time
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).group_by(func.date(User.created_at)).order_by('date').all()
    
    # Product categories distribution
    category_stats = db.session.query(
        ProductCategory.name,
        func.count(Product.id).label('count')
    ).join(Product).group_by(ProductCategory.name).all()
    
    # User type distribution
    user_type_stats = db.session.query(
        User.user_type,
        func.count(User.id).label('count')
    ).group_by(User.user_type).all()
    
    return render_template('admin/analytics.html',
                         user_growth=user_growth,
                         category_stats=category_stats,
                         user_type_stats=user_type_stats)
