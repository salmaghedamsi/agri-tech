from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, CourseModule, CourseEnrollment, CourseProgress
from app.forms.course import CourseForm, CourseModuleForm
from sqlalchemy import desc, or_
from werkzeug.exceptions import NotFound, Forbidden
import os
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, CourseModule, CourseEnrollment, CourseProgress
from app.forms.course import CourseForm, CourseModuleForm
from sqlalchemy import desc, or_
import os
from werkzeug.utils import secure_filename

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

@learning_bp.route('/course/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course"""
    # Prevent experts from enrolling
    if current_user.is_expert():
        flash('Experts cannot enroll in courses.', 'error')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
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

@learning_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    """Course detail page"""
    course = Course.query.get_or_404(course_id)
    
    # Get course modules
    modules = CourseModule.query.filter_by(course_id=course_id, is_published=True).order_by(CourseModule.order_index).all()
    
    # For experts, don't show enrollment info
    enrollment = None
    if current_user.is_authenticated and not current_user.is_expert():
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


@learning_bp.route('/course/<int:course_id>/learn')
@login_required
def learn_course(course_id):
    """Course learning interface"""
    course = Course.query.get_or_404(course_id)
    
    # If user is an expert, they can view without enrollment
    if not current_user.is_expert():
        # For non-experts, check enrollment
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=current_user.id
        ).first()
        
        if not enrollment:
            flash('You must enroll in this course first.', 'error')
            return redirect(url_for('learning.course_detail', course_id=course_id))
    else:
        # For experts, don't track enrollment
        enrollment = None
    
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
    
    # Experts don't need enrollment to view content
    if not current_user.is_expert():
        # Check if user is enrolled
        enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=current_user.id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'Not enrolled in course'}), 400
    else:
        # For experts, we don't track progress
        return jsonify({'success': True})
    
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
    # Redirect experts to course management
    if current_user.is_expert():
        flash('Experts should use the course management interface.', 'info')
        return redirect(url_for('learning.manage_courses'))
        
    page = request.args.get('page', 1, type=int)
    enrollments = CourseEnrollment.query.filter_by(user_id=current_user.id).order_by(desc(CourseEnrollment.enrolled_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('learning/my_courses.html', enrollments=enrollments)



import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'modules')

@learning_bp.route('/course/<int:course_id>/add-module', methods=['GET', 'POST'])
@login_required
def add_module(course_id):
    """Add module to course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is course instructor
    if course.instructor_id != current_user.id:
        flash('You can only add modules to your own courses.', 'error')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    form = CourseModuleForm()
    if form.validate_on_submit():
        # Get highest order_index
        highest_order = db.session.query(db.func.max(CourseModule.order_index)).filter_by(course_id=course_id).scalar()
        next_order = (highest_order or -1) + 1
        
        # Create module instance
        module = CourseModule(
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            content_type=form.content_type.data,
            video_url=form.video_url.data if form.content_type.data in ['video', 'video_plus_doc'] else None,
            duration_minutes=form.duration_minutes.data,
            order_index=next_order,
            course_id=course_id,
            is_required=form.is_required.data,
            is_published=form.is_published.data
        )
        
        # Handle document upload
        if form.document.data:
            # Ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Secure the filename and save the file
            filename = secure_filename(f"{course_id}_{next_order}_{form.document.data.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.document.data.save(filepath)
            
            # Store the relative path in the database
            module.document_path = os.path.join('uploads', 'modules', filename)
        
        db.session.add(module)
        db.session.commit()
        
        flash('Module added successfully!', 'success')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    return render_template('learning/add_module.html', form=form, course=course)

@learning_bp.route('/course/<int:course_id>/module/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_module(course_id, module_id):
    """Edit course module"""
    course = Course.query.get_or_404(course_id)
    module = CourseModule.query.get_or_404(module_id)
    
    # Check if user is course instructor
    if course.instructor_id != current_user.id:
        flash('You can only edit modules in your own courses.', 'error')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    form = CourseModuleForm(obj=module)
    if form.validate_on_submit():
        module.title = form.title.data
        module.description = form.description.data
        module.content = form.content.data
        module.content_type = form.content_type.data
        module.video_url = form.video_url.data if form.content_type.data in ['video', 'video_plus_doc'] else None
        module.duration_minutes = form.duration_minutes.data
        module.is_required = form.is_required.data
        module.is_published = form.is_published.data
        
        # Handle document upload
        if form.document.data:
            # Delete old document if it exists
            if module.document_path:
                old_filepath = os.path.join('app', 'static', module.document_path)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
            
            # Ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Secure the filename and save the file
            filename = secure_filename(f"{course_id}_{module.order_index}_{form.document.data.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.document.data.save(filepath)
            
            # Store the relative path in the database
            module.document_path = os.path.join('uploads', 'modules', filename)
        
        db.session.commit()
        
        flash('Module updated successfully!', 'success')
        return redirect(url_for('learning.course_detail', course_id=course_id))
    
    return render_template('learning/edit_module.html', form=form, course=course, module=module)

@learning_bp.route('/course/<int:course_id>/module/<int:module_id>', methods=['DELETE'])
@login_required
def delete_module(course_id, module_id):
    """Delete course module"""
    course = Course.query.get_or_404(course_id)
    module = CourseModule.query.get_or_404(module_id)
    
    # Check if user is course instructor
    if course.instructor_id != current_user.id:
        return jsonify({'error': 'You can only delete modules from your own courses.'}), 403
    
    try:
        # Delete associated document if it exists
        if module.document_path:
            filepath = os.path.join('app', 'static', module.document_path)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Delete module from database
        db.session.delete(module)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/course/<int:course_id>/reorder-modules', methods=['POST'])
@login_required
def reorder_modules(course_id):
    """Reorder course modules"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is course instructor
    if course.instructor_id != current_user.id:
        return jsonify({'error': 'You can only reorder modules in your own courses.'}), 403
    
    try:
        modules_data = request.json.get('modules', [])
        for module_data in modules_data:
            module = CourseModule.query.get(module_data['id'])
            if module and module.course_id == course_id:
                module.order_index = module_data['order']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@learning_bp.route('/manage-courses')
@login_required
def manage_courses():
    """Course management interface for instructors"""
    if not current_user.is_expert():
        flash('Only experts can access course management.', 'error')
        return redirect(url_for('learning.index'))
    
    page = request.args.get('page', 1, type=int)
    
    courses = Course.query.filter_by(instructor_id=current_user.id)\
        .order_by(Course.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('learning/manage_courses.html', courses=courses)

@learning_bp.route('/course/<int:course_id>/manage-modules')
@login_required
def manage_modules(course_id):
    """Module management interface"""
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != current_user.id:
        flash('You can only manage modules in your own courses.', 'error')
        return redirect(url_for('learning.index'))
    
    modules = CourseModule.query.filter_by(course_id=course_id)\
        .order_by(CourseModule.order_index).all()
    
    return render_template('learning/manage_modules.html', 
                         course=course, 
                         modules=modules)

@learning_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course_management():
    """Create new course with document upload"""
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
            is_published=form.is_published.data,
            tutorial_video_url=form.tutorial_video_url.data
        )
        
        # Handle document upload
        if form.document.data:
            file = form.document.data
            if file and file.filename:
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'courses', 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Secure filename and save
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Store relative path
                course.document_path = f'uploads/courses/documents/{filename}'
        
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('learning.manage_courses'))
    
    return render_template('learning/create_course.html', form=form)

@learning_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit existing course"""
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != current_user.id:
        flash('You can only edit your own courses.', 'error')
        return redirect(url_for('learning.manage_courses'))
    
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        course.duration_hours = form.duration_hours.data
        course.difficulty_level = form.difficulty_level.data
        course.language = form.language.data
        course.is_published = form.is_published.data
        course.tutorial_video_url = form.tutorial_video_url.data
        
        # Handle document upload
        if form.document.data:
            file = form.document.data
            if file and file.filename:
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'courses', 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Secure filename and save
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Store relative path
                course.document_path = f'uploads/courses/documents/{filename}'
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('learning.manage_courses'))
    
    return render_template('learning/edit_course.html', form=form, course=course)

@learning_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete course"""
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != current_user.id:
        flash('You can only delete your own courses.', 'error')
        return redirect(url_for('learning.manage_courses'))
    
    # Delete associated file if exists
    if course.document_path:
        file_path = os.path.join(current_app.root_path, 'static', course.document_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('learning.manage_courses'))

@learning_bp.route('/courses/<int:course_id>/publish', methods=['POST'])
@login_required
def publish_course(course_id):
    """Toggle course publication status"""
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != current_user.id:
        flash('You can only manage your own courses.', 'error')
        return redirect(url_for('learning.manage_courses'))
    
    course.is_published = not course.is_published
    db.session.commit()
    
    status = 'published' if course.is_published else 'unpublished'
    flash(f'Course {status} successfully!', 'success')
    return redirect(url_for('learning.manage_courses'))
