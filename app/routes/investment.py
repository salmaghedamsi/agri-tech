from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.investment import Investment, InvestmentProposal
from app.models.land import Land, LandInvestment, LandLease
from app.forms.investment import InvestmentForm, InvestmentProposalForm
from app.forms.land import LandInvestmentForm, LandLeaseForm
from sqlalchemy import desc, or_

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/')
def index():
    """Investment hub home page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    investment_type = request.args.get('type', '')
    risk_level = request.args.get('risk', '')
    
    # Build query for investments
    query = Investment.query.filter_by(status='active')
    
    if search:
        query = query.filter(or_(
            Investment.title.contains(search),
            Investment.description.contains(search)
        ))
    
    if investment_type:
        query = query.filter_by(investment_type=investment_type)
    
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    
    investments = query.order_by(desc(Investment.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Build query for land
    land_query = Land.query.filter_by(is_available=True)
    if search:
        land_query = land_query.filter(or_(
            Land.title.contains(search),
            Land.description.contains(search),
            Land.location.contains(search)
        ))
    
    land_listings = land_query.order_by(desc(Land.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('investment/index.html',
                         investments=investments,
                         land_listings=land_listings,
                         search=search,
                         investment_type=investment_type,
                         risk_level=risk_level)

@investment_bp.route('/investment/<int:investment_id>')
def investment_detail(investment_id):
    """Investment detail page"""
    investment = Investment.query.get_or_404(investment_id)
    
    # Get investment proposals
    proposals = InvestmentProposal.query.filter_by(investment_id=investment_id).order_by(desc(InvestmentProposal.created_at)).all()
    
    # Check if user has already proposed
    user_proposal = None
    if current_user.is_authenticated:
        user_proposal = InvestmentProposal.query.filter_by(
            investment_id=investment_id,
            investor_id=current_user.id
        ).first()
    
    return render_template('investment/investment_detail.html',
                         investment=investment,
                         proposals=proposals,
                         user_proposal=user_proposal)

@investment_bp.route('/investment/<int:investment_id>/propose', methods=['GET', 'POST'])
@login_required
def propose_investment(investment_id):
    """Propose investment (investors only)"""
    if not current_user.is_investor():
        flash('Only investors can make investment proposals.', 'error')
        return redirect(url_for('investment.index'))
    
    investment = Investment.query.get_or_404(investment_id)
    
    # Check if already proposed
    existing_proposal = InvestmentProposal.query.filter_by(
        investment_id=investment_id,
        investor_id=current_user.id
    ).first()
    
    if existing_proposal:
        flash('You have already submitted a proposal for this investment.', 'info')
        return redirect(url_for('investment.investment_detail', investment_id=investment_id))
    
    form = InvestmentProposalForm()
    if form.validate_on_submit():
        proposal = InvestmentProposal(
            amount=form.amount.data,
            message=form.message.data,
            investment_id=investment_id,
            investor_id=current_user.id
        )
        
        db.session.add(proposal)
        db.session.commit()
        
        flash('Investment proposal submitted successfully!', 'success')
        return redirect(url_for('investment.investment_detail', investment_id=investment_id))
    
    return render_template('investment/propose_investment.html', form=form, investment=investment)

@investment_bp.route('/create-investment', methods=['GET', 'POST'])
@login_required
def create_investment():
    """Create investment opportunity (farmers only)"""
    if not current_user.is_farmer():
        flash('Only farmers can create investment opportunities.', 'error')
        return redirect(url_for('investment.index'))
    
    form = InvestmentForm()
    if form.validate_on_submit():
        investment = Investment(
            title=form.title.data,
            description=form.description.data,
            investment_type=form.investment_type.data,
            amount_requested=form.amount_requested.data,
            minimum_investment=form.minimum_investment.data,
            maximum_investment=form.maximum_investment.data,
            interest_rate=form.interest_rate.data,
            expected_return=form.expected_return.data,
            duration_months=form.duration_months.data,
            risk_level=form.risk_level.data,
            target_date=form.target_date.data,
            farmer_id=current_user.id
        )
        
        db.session.add(investment)
        db.session.commit()
        
        flash('Investment opportunity created successfully!', 'success')
        return redirect(url_for('investment.investment_detail', investment_id=investment.id))
    
    return render_template('investment/create_investment.html', form=form)

@investment_bp.route('/land/<int:land_id>')
def land_detail(land_id):
    """Land detail page"""
    land = Land.query.get_or_404(land_id)
    
    # Get land investments
    investments = LandInvestment.query.filter_by(land_id=land_id).order_by(desc(LandInvestment.created_at)).all()
    
    # Get land leases
    leases = LandLease.query.filter_by(land_id=land_id).order_by(desc(LandLease.created_at)).all()
    
    return render_template('investment/land_detail.html',
                         land=land,
                         investments=investments,
                         leases=leases)

@investment_bp.route('/land/<int:land_id>/invest', methods=['GET', 'POST'])
@login_required
def invest_in_land(land_id):
    """Invest in land (investors only)"""
    if not current_user.is_investor():
        flash('Only investors can invest in land.', 'error')
        return redirect(url_for('investment.index'))
    
    land = Land.query.get_or_404(land_id)
    
    form = LandInvestmentForm()
    if form.validate_on_submit():
        investment = LandInvestment(
            investment_amount=form.investment_amount.data,
            ownership_percentage=form.ownership_percentage.data,
            land_id=land_id,
            investor_id=current_user.id
        )
        
        db.session.add(investment)
        db.session.commit()
        
        flash('Land investment proposal submitted successfully!', 'success')
        return redirect(url_for('investment.land_detail', land_id=land_id))
    
    return render_template('investment/invest_in_land.html', form=form, land=land)

@investment_bp.route('/land/<int:land_id>/lease', methods=['GET', 'POST'])
@login_required
def lease_land(land_id):
    """Lease land (farmers only)"""
    if not current_user.is_farmer():
        flash('Only farmers can lease land.', 'error')
        return redirect(url_for('investment.index'))
    
    land = Land.query.get_or_404(land_id)
    
    form = LandLeaseForm()
    if form.validate_on_submit():
        lease = LandLease(
            monthly_rent=form.monthly_rent.data,
            lease_duration_months=form.lease_duration_months.data,
            start_date=form.start_date.data,
            terms_conditions=form.terms_conditions.data,
            land_id=land_id,
            tenant_id=current_user.id
        )
        
        # Calculate end date
        from datetime import timedelta
        lease.end_date = lease.start_date + timedelta(days=lease.lease_duration_months * 30)
        
        db.session.add(lease)
        db.session.commit()
        
        flash('Land lease proposal submitted successfully!', 'success')
        return redirect(url_for('investment.land_detail', land_id=land_id))
    
    return render_template('investment/lease_land.html', form=form, land=land)

@investment_bp.route('/my-investments')
@login_required
def my_investments():
    """User's investments"""
    if current_user.is_farmer():
        # Farmer's created investments
        investments = Investment.query.filter_by(farmer_id=current_user.id).order_by(desc(Investment.created_at)).all()
        land_listings = Land.query.filter_by(owner_id=current_user.id).order_by(desc(Land.created_at)).all()
        
        return render_template('investment/my_investments_farmer.html',
                             investments=investments,
                             land_listings=land_listings)
    
    elif current_user.is_investor():
        # Investor's proposals
        proposals = InvestmentProposal.query.filter_by(investor_id=current_user.id).order_by(desc(InvestmentProposal.created_at)).all()
        land_investments = LandInvestment.query.filter_by(investor_id=current_user.id).order_by(desc(LandInvestment.created_at)).all()
        land_leases = LandLease.query.filter_by(tenant_id=current_user.id).order_by(desc(LandLease.created_at)).all()
        
        return render_template('investment/my_investments_investor.html',
                             proposals=proposals,
                             land_investments=land_investments,
                             land_leases=land_leases)
    
    else:
        flash('Access denied.', 'error')
        return redirect(url_for('investment.index'))

@investment_bp.route('/proposal/<int:proposal_id>/accept', methods=['POST'])
@login_required
def accept_proposal(proposal_id):
    """Accept investment proposal (farmers only)"""
    proposal = InvestmentProposal.query.get_or_404(proposal_id)
    
    if proposal.investment.farmer_id != current_user.id:
        flash('You can only accept proposals for your own investments.', 'error')
        return redirect(url_for('investment.my_investments'))
    
    proposal.status = 'accepted'
    
    # Update investment amount raised
    proposal.investment.amount_raised += proposal.amount
    
    db.session.commit()
    
    flash('Investment proposal accepted!', 'success')
    return redirect(url_for('investment.my_investments'))

@investment_bp.route('/proposal/<int:proposal_id>/reject', methods=['POST'])
@login_required
def reject_proposal(proposal_id):
    """Reject investment proposal (farmers only)"""
    proposal = InvestmentProposal.query.get_or_404(proposal_id)
    
    if proposal.investment.farmer_id != current_user.id:
        flash('You can only reject proposals for your own investments.', 'error')
        return redirect(url_for('investment.my_investments'))
    
    proposal.status = 'rejected'
    db.session.commit()
    
    flash('Investment proposal rejected.', 'info')
    return redirect(url_for('investment.my_investments'))
