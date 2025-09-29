from flask import Blueprint, render_template, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from datetime import datetime
import os
import time
from werkzeug.utils import secure_filename
from app import db
from app.models.grant import GrantApplication, ApplicationDocument

grant_bp = Blueprint('grant', __name__)

@grant_bp.route('/grants')
@login_required
def grants_dashboard():
    applications = GrantApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('grants/dashboard.html', applications=applications)

@grant_bp.route('/grants/apply', methods=['GET', 'POST'])
@login_required
def apply_grant():
    from app.forms.grant_forms import GrantApplicationForm
    form = GrantApplicationForm()
    
    if form.validate_on_submit():
        try:
            application = GrantApplication(
                user_id=current_user.id,
                grant_type=form.grant_type.data,
                amount_requested=form.amount_requested.data,
                purpose=form.purpose.data
            )
            
            db.session.add(application)
            db.session.commit()
            
            flash('✅ Your grant application has been submitted successfully!', 'success')
            return redirect(url_for('grant.grants_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('❌ Error submitting the application', 'error')
    
    return render_template('grants/apply.html', form=form)

@grant_bp.route('/grants/<application_id>')
@login_required
def view_application(application_id):
    application = GrantApplication.query.filter_by(
        application_id=application_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('grants/view_application.html', application=application)

@grant_bp.route('/grants/<application_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_application(application_id):
    application = GrantApplication.query.filter_by(
        application_id=application_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if application.status != 'Submitted':
        flash('❌ This application can no longer be modified', 'error')
        return redirect(url_for('grant.grants_dashboard'))
    
    from app.forms.grant_forms import GrantApplicationForm
    form = GrantApplicationForm(obj=application)
    
    if form.validate_on_submit():
        try:
            application.grant_type = form.grant_type.data
            application.amount_requested = form.amount_requested.data
            application.purpose = form.purpose.data
            application.last_updated = datetime.utcnow()
            
            db.session.commit()
            flash('✅ Application updated successfully!', 'success')
            return redirect(url_for('grant.grants_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('❌ Error updating the application', 'error')
    
    return render_template('grants/edit_application.html', form=form, application=application)

@grant_bp.route('/grants/<application_id>/withdraw')
@login_required
def withdraw_application(application_id):
    application = GrantApplication.query.filter_by(
        application_id=application_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if application.status != 'Submitted':
        flash('❌ This application can no longer be withdrawn', 'error')
        return redirect(url_for('grant.grants_dashboard'))
    
    try:
        ApplicationDocument.query.filter_by(application_id=application.id).delete()
        db.session.delete(application)
        db.session.commit()
        flash('✅ Application withdrawn successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('❌ Error withdrawing the application', 'error')
    
    return redirect(url_for('grant.grants_dashboard'))