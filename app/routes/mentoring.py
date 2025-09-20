from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.mentoring import Mentor, MentoringRequest, MentoringSession
from app.forms.mentoring import MentoringRequestForm, MentoringSessionForm
from sqlalchemy import desc, or_

mentoring_bp = Blueprint('mentoring', __name__)

@mentoring_bp.route('/')
def index():
    """Mentoring hub home page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    
    # Build query for mentors
    query = Mentor.query.filter_by(is_available=True)
    
    if search:
        query = query.join(Mentor.get_user()).filter(
            or_(
                Mentor.specialization.contains(search),
                Mentor.bio.contains(search)
            )
        )
    
    if specialization:
        query = query.filter(Mentor.specialization.contains(specialization))
    
    mentors = query.order_by(desc(Mentor.rating)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('mentoring/index.html',
                         mentors=mentors,
                         search=search,
                         specialization=specialization)

@mentoring_bp.route('/mentor/<int:mentor_id>')
def mentor_profile(mentor_id):
    """Mentor profile page"""
    mentor = Mentor.query.get_or_404(mentor_id)
    
    # Get mentor's recent sessions
    recent_sessions = MentoringSession.query.filter_by(
        mentor_id=mentor.user_id
    ).order_by(desc(MentoringSession.created_at)).limit(5).all()
    
    return render_template('mentoring/mentor_profile.html',
                         mentor=mentor,
                         recent_sessions=recent_sessions)

@mentoring_bp.route('/request-mentoring', methods=['GET', 'POST'])
@login_required
def request_mentoring():
    """Request mentoring session"""
    form = MentoringRequestForm()
    
    # Populate mentor choices
    mentors = Mentor.query.filter_by(is_available=True).all()
    form.mentor_id.choices = [(m.id, f"{m.get_user().get_full_name()} - {m.specialization}") for m in mentors]
    
    if form.validate_on_submit():
        request_obj = MentoringRequest(
            subject=form.subject.data,
            description=form.description.data,
            preferred_time=form.preferred_time.data,
            duration_minutes=form.duration_minutes.data,
            mentee_id=current_user.id,
            mentor_id=form.mentor_id.data
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        flash('Mentoring request sent successfully!', 'success')
        return redirect(url_for('mentoring.my_requests'))
    
    return render_template('mentoring/request_mentoring.html', form=form)

@mentoring_bp.route('/my-requests')
@login_required
def my_requests():
    """User's mentoring requests"""
    page = request.args.get('page', 1, type=int)
    requests = MentoringRequest.query.filter_by(mentee_id=current_user.id).order_by(desc(MentoringRequest.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('mentoring/my_requests.html', requests=requests)

@mentoring_bp.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    """Accept mentoring request (mentors only)"""
    request_obj = MentoringRequest.query.get_or_404(request_id)
    
    if request_obj.mentor_id != current_user.id:
        flash('You can only accept your own requests.', 'error')
        return redirect(url_for('mentoring.index'))
    
    request_obj.status = 'accepted'
    db.session.commit()
    
    flash('Request accepted successfully!', 'success')
    return redirect(url_for('mentoring.mentor_dashboard'))

@mentoring_bp.route('/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    """Reject mentoring request (mentors only)"""
    request_obj = MentoringRequest.query.get_or_404(request_id)
    
    if request_obj.mentor_id != current_user.id:
        flash('You can only reject your own requests.', 'error')
        return redirect(url_for('mentoring.index'))
    
    request_obj.status = 'rejected'
    db.session.commit()
    
    flash('Request rejected.', 'info')
    return redirect(url_for('mentoring.mentor_dashboard'))

@mentoring_bp.route('/mentor-dashboard')
@login_required
def mentor_dashboard():
    """Mentor dashboard"""
    if not current_user.is_expert():
        flash('Only experts can access mentor dashboard.', 'error')
        return redirect(url_for('mentoring.index'))
    
    # Get mentor profile
    mentor = Mentor.query.filter_by(user_id=current_user.id).first()
    
    if not mentor:
        flash('Please complete your mentor profile first.', 'info')
        return redirect(url_for('mentoring.create_profile'))
    
    # Get pending requests
    pending_requests = MentoringRequest.query.filter_by(
        mentor_id=mentor.id,
        status='pending'
    ).order_by(desc(MentoringRequest.created_at)).all()
    
    # Get upcoming sessions
    upcoming_sessions = MentoringSession.query.filter_by(
        mentor_id=current_user.id,
        status='scheduled'
    ).order_by(MentoringSession.scheduled_time).all()
    
    # Get recent sessions
    recent_sessions = MentoringSession.query.filter_by(
        mentor_id=current_user.id
    ).order_by(desc(MentoringSession.created_at)).limit(10).all()
    
    return render_template('mentoring/mentor_dashboard.html',
                         mentor=mentor,
                         pending_requests=pending_requests,
                         upcoming_sessions=upcoming_sessions,
                         recent_sessions=recent_sessions)

@mentoring_bp.route('/create-profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    """Create mentor profile (experts only)"""
    if not current_user.is_expert():
        flash('Only experts can create mentor profiles.', 'error')
        return redirect(url_for('mentoring.index'))
    
    # Check if profile already exists
    existing_profile = Mentor.query.filter_by(user_id=current_user.id).first()
    if existing_profile:
        flash('You already have a mentor profile.', 'info')
        return redirect(url_for('mentoring.mentor_dashboard'))
    
    if request.method == 'POST':
        mentor = Mentor(
            user_id=current_user.id,
            specialization=request.form.get('specialization'),
            experience_years=int(request.form.get('experience_years')),
            hourly_rate=float(request.form.get('hourly_rate', 0)),
            bio=request.form.get('bio'),
            languages=request.form.get('languages'),
            is_available=True
        )
        
        db.session.add(mentor)
        db.session.commit()
        
        flash('Mentor profile created successfully!', 'success')
        return redirect(url_for('mentoring.mentor_dashboard'))
    
    return render_template('mentoring/create_profile.html')

@mentoring_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    """Mentoring session detail"""
    session = MentoringSession.query.get_or_404(session_id)
    
    # Check if user is part of this session
    if session.mentor_id != current_user.id and session.mentee_id != current_user.id:
        flash('You can only view your own sessions.', 'error')
        return redirect(url_for('mentoring.index'))
    
    return render_template('mentoring/session_detail.html', session=session)

@mentoring_bp.route('/session/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_session(session_id):
    """Complete mentoring session"""
    session = MentoringSession.query.get_or_404(session_id)
    
    if session.mentor_id != current_user.id:
        flash('Only the mentor can complete the session.', 'error')
        return redirect(url_for('mentoring.session_detail', session_id=session_id))
    
    session.status = 'completed'
    db.session.commit()
    
    flash('Session marked as completed!', 'success')
    return redirect(url_for('mentoring.session_detail', session_id=session_id))
