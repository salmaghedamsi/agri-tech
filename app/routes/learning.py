from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, CourseModule, CourseEnrollment, CourseProgress
from app.forms.course import CourseForm, CourseModuleForm
from sqlalchemy import desc, or_

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/')
def index():
    """Learning hub home page with course listings"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    language = request.args.get('language', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Build query
    query = Course.query.filter_by(is_published=True)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            Course.title.contains(search),
            Course.description.contains(search)
        ))
    
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    if language:
        query = query.filter_by(language=language)
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Course.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Course.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(desc(Course.created_at))  # TODO: Implement rating-based sorting
    else:  # newest
        query = query.order_by(desc(Course.created_at))
    
    # Paginate results
    courses = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('learning/index.html',
                         courses=courses,
                         search=search,
                         difficulty=difficulty,
                         language=language,
                         sort_by=sort_by)

@learning_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    course = Course.query.get_or_404(course_id)
    
    # Get course modules
    modules = CourseModule.query.filter_by(course_id=course_id, is_published=True).order_by(CourseModule.order_index).all()
    
    # Check if user is enrolled
    enrollment = None
    if current_user.is_authenticated:
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=current_user.id
        ).first()
    
    # Get related courses
    related_courses = Course.query.filter(
        Course.id != course_id,
        Course.is_published == True
    ).limit(4).all()
    
    return render_template('learning/course_detail.html',
                         course=course,
                         modules=modules,
                         enrollment=enrollment,
                         related_courses=related_courses)

@learning_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = CourseEnrollment.query.filter_by(
        course_id=course_id,
        user_id=current_user.id
    ).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    # Create enrollment
    enrollment = CourseEnrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    
    db.session.add(enrollment)
    db.session.commit()
    
    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('learning.course_detail', course_id=course_id))

@learning_bp.route('/course/<int:course_id>/learn')
@login_required
def learn_course(course_id):
    """Course learning interface"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        course_id=course_id,
        user_id=current_user.id
    ).first()
    
    if not enrollment:
        flash('You must enroll in this course first.', 'error')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    # Get course modules
    modules = CourseModule.query.filter_by(course_id=course_id, is_published=True).order_by(CourseModule.order_index).all()
    
    # Get current module
    current_module_id = request.args.get('module', type=int)
    if current_module_id:
        current_module = CourseModule.query.get(current_module_id)
    else:
        current_module = modules[0] if modules else None
    
    # Get user's progress for current module
    progress = None
    if current_module:
        progress = CourseProgress.query.filter_by(
            enrollment_id=enrollment.id,
            module_id=current_module.id
        ).first()
    
    return render_template('learning/learn_course.html',
                         course=course,
                         modules=modules,
                         current_module=current_module,
                         enrollment=enrollment,
                         progress=progress)

@learning_bp.route('/course/<int:course_id>/module/<int:module_id>/complete', methods=['POST'])
@login_required
def complete_module(course_id, module_id):
    """Mark module as completed"""
    course = Course.query.get_or_404(course_id)
    module = CourseModule.query.get_or_404(module_id)
    
    # Check if user is enrolled
    enrollment = CourseEnrollment.query.filter_by(
        course_id=course_id,
        user_id=current_user.id
    ).first()
    
    if not enrollment:
        return jsonify({'error': 'Not enrolled in course'}), 400
    
    # Get or create progress record
    progress = CourseProgress.query.filter_by(
        enrollment_id=enrollment.id,
        module_id=module_id
    ).first()
    
    if not progress:
        progress = CourseProgress(
            enrollment_id=enrollment.id,
            module_id=module_id
        )
        db.session.add(progress)
    
    # Mark as completed
    progress.is_completed = True
    progress.completed_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({'success': True})

@learning_bp.route('/my-courses')
@login_required
def my_courses():
    """User's enrolled courses"""
    page = request.args.get('page', 1, type=int)
    enrollments = CourseEnrollment.query.filter_by(user_id=current_user.id).order_by(desc(CourseEnrollment.enrolled_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('learning/my_courses.html', enrollments=enrollments)

@learning_bp.route('/create-course', methods=['GET', 'POST'])
@login_required
def create_course():
    """Create new course (experts only)"""
    if not current_user.is_expert():
        flash('Only experts can create courses.', 'error')
        return redirect(url_for('learning.index'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration_hours=form.duration_hours.data,
            difficulty_level=form.difficulty_level.data,
            language=form.language.data,
            instructor_id=current_user.id,
            is_published=form.is_published.data
        )
        
        # Handle thumbnail upload
        if form.thumbnail.data:
            # TODO: Implement thumbnail upload logic
            pass
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('learning.course_detail', course_id=course.id))
    
    return render_template('learning/create_course.html', form=form)

@learning_bp.route('/course/<int:course_id>/add-module', methods=['GET', 'POST'])
@login_required
def add_module(course_id):
    """Add module to course"""
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != current_user.id:
        flash('You can only add modules to your own courses.', 'error')
        return redirect(url_for('learning.index'))
    
    form = CourseModuleForm()
    if form.validate_on_submit():
        module = CourseModule(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            content_type=form.content_type.data,
            duration_minutes=form.duration_minutes.data,
            order_index=form.order_index.data,
            course_id=course_id,
            is_published=form.is_published.data
        )
        
        db.session.add(module)
        db.session.commit()
        
        flash('Module added successfully!', 'success')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    return render_template('learning/add_module.html', form=form, course=course)
