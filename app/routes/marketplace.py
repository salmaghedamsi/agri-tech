from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import json
import os
from app import db
from app.models.product import Product, ProductCategory, ProductReview
from app.models.user import User
from app.forms.product import ProductForm, ProductReviewForm, FarmerProfileForm, ProductSearchForm
from app.utils.file_upload import save_uploaded_file, save_multiple_files, delete_product_images, validate_image_file
from sqlalchemy import or_, desc, asc

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
def index():
    """Marketplace home page with product listings"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'newest')
    organic_only = request.args.get('organic', type=bool)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build query
    query = Product.query.filter_by(is_available=True).filter(Product.quantity > 0)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            Product.name.contains(search),
            Product.description.contains(search)
        ))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if organic_only:
        query = query.filter_by(is_organic=True)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Apply sorting
    if sort_by == 'price':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        query = query.order_by(Product.name.desc())
    elif sort_by == 'rating':
        query = query.order_by(desc(Product.created_at))  # TODO: Implement rating-based sorting
    else:  # newest
        query = query.order_by(desc(Product.created_at))
    
    # Paginate results
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get categories for filter
    categories = ProductCategory.query.all()
    
    # Create search form for filters
    search_form = ProductSearchForm()
    search_form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in categories]
    
    return render_template('marketplace/index.html',
                         products=products,
                         categories=categories,
                         search=search,
                         category_id=category_id,
                         sort_by=sort_by,
                         search_form=search_form)

@marketplace_bp.route('/product/<int:id>')
def product_detail(id):
    """Product detail page"""
    product = Product.query.get_or_404(id)
    
    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('marketplace/product_detail.html',
                         product=product,
                         related_products=related_products)

@marketplace_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product (farmers only)"""
    if not current_user.is_farmer():
        flash('Only farmers can add products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in ProductCategory.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            category_id=form.category_id.data,
            seller_id=current_user.id,
            is_organic=form.is_organic.data
        )
        
        # Add optional fields if they exist in the form
        if hasattr(form, 'harvest_date') and form.harvest_date.data:
            product.harvest_date = form.harvest_date.data
        if hasattr(form, 'expiry_date') and form.expiry_date.data:
            product.expiry_date = form.expiry_date.data
        if hasattr(form, 'min_order_quantity') and form.min_order_quantity.data:
            product.min_order_quantity = form.min_order_quantity.data
        if hasattr(form, 'delivery_available'):
            product.delivery_available = form.delivery_available.data
        if hasattr(form, 'delivery_radius') and form.delivery_radius.data:
            product.delivery_radius = form.delivery_radius.data
        
        # Handle image upload - use the correct field name
        if form.image.data:
            image_result = save_uploaded_file(form.image.data, 'products')
            if image_result:
                product.image = image_result['filename']
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('marketplace.farmer_dashboard'))
    
    return render_template('marketplace/add_product.html', form=form)

@marketplace_bp.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Edit existing product"""
    product = Product.query.get_or_404(id)
    
    if product.seller_id != current_user.id:
        flash('You can only edit your own products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in ProductCategory.query.all()]
    
    if form.validate_on_submit():
        # Handle delete action
        if request.form.get('action') == 'delete':
            # Delete product images
            if product.image:
                delete_product_images([product.image])
            
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully!', 'success')
            return redirect(url_for('marketplace.farmer_dashboard'))
        
        # Update product fields
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.unit = form.unit.data
        product.category_id = form.category_id.data
        product.is_organic = form.is_organic.data
        
        # Update optional fields if they exist
        if hasattr(form, 'harvest_date') and form.harvest_date.data:
            product.harvest_date = form.harvest_date.data
        if hasattr(form, 'expiry_date') and form.expiry_date.data:
            product.expiry_date = form.expiry_date.data
        if hasattr(form, 'min_order_quantity') and form.min_order_quantity.data:
            product.min_order_quantity = form.min_order_quantity.data
        if hasattr(form, 'delivery_available'):
            product.delivery_available = form.delivery_available.data
        if hasattr(form, 'delivery_radius') and form.delivery_radius.data:
            product.delivery_radius = form.delivery_radius.data
        if hasattr(form, 'is_active'):
            product.is_active = form.is_active.data
        
        # Handle image update
        if form.image.data:
            image_result = save_uploaded_file(form.image.data, 'products')
            if image_result:
                # Delete old image
                if product.image:
                    delete_product_images([product.image])
                product.image = image_result['filename']
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('marketplace.farmer_dashboard'))
    
    return render_template('marketplace/edit_product.html', form=form, product=product)

@marketplace_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product"""
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        flash('You can only delete your own products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    # Delete associated images
    delete_product_images(product)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('marketplace.farmer_dashboard'))

@marketplace_bp.route('/farmer-dashboard')
@login_required
def farmer_dashboard():
    """Farmer dashboard for managing products and profile"""
    if not current_user.is_farmer():
        flash('Only farmers can access this page.', 'error')
        return redirect(url_for('marketplace.index'))
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(seller_id=current_user.id).order_by(desc(Product.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get dashboard statistics
    total_products = Product.query.filter_by(seller_id=current_user.id).count()
    active_products = Product.query.filter_by(seller_id=current_user.id, is_available=True).count()
    total_reviews = ProductReview.query.join(Product).filter(Product.seller_id == current_user.id).count()
    
    stats = {
        'total_products': total_products,
        'active_products': active_products,
        'inactive_products': total_products - active_products,
        'total_reviews': total_reviews
    }
    
    return render_template('marketplace/farmer_dashboard.html', products=products, stats=stats)

@marketplace_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_farmer_profile():
    """Edit farmer profile"""
    if not current_user.is_farmer():
        flash('Only farmers can access this page.', 'error')
        return redirect(url_for('marketplace.index'))
    
    form = FarmerProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.farm_name = form.farm_name.data
        current_user.farm_location = form.farm_location.data
        current_user.farm_size = form.farm_size.data
        current_user.farm_type = form.farm_type.data
        current_user.years_experience = form.years_experience.data
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data
        current_user.farm_description = form.farm_description.data
        current_user.certifications = form.certifications.data
        
        # Handle profile image upload if field exists
        if hasattr(form, 'profile_image') and form.profile_image.data:
            profile_image_result = save_uploaded_file(form.profile_image.data, 'profiles')
            if profile_image_result:
                current_user.profile_image = profile_image_result['filename']
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('marketplace.farmer_dashboard'))
    
    return render_template('marketplace/farmer_profile.html', form=form)

@marketplace_bp.route('/farmer/<int:farmer_id>')
def farmer_profile(farmer_id):
    """View farmer's public profile and products"""
    farmer = User.query.get_or_404(farmer_id)
    
    if not farmer.is_farmer():
        flash('This user is not a farmer.', 'error')
        return redirect(url_for('marketplace.index'))
    
    # Get farmer's products
    products = Product.query.filter_by(
        seller_id=farmer_id, 
        is_active=True
    ).filter(Product.quantity > 0).order_by(desc(Product.created_at)).limit(6).all()
    
    # Get farmer stats
    farmer_stats = {
        'total_products': Product.query.filter_by(seller_id=farmer_id).count(),
        'active_products': Product.query.filter_by(seller_id=farmer_id, is_active=True).count(),
        'organic_products': Product.query.filter_by(seller_id=farmer_id, is_organic=True).count(),
        'price_range': None
    }
    
    # Get price range
    if products:
        prices = [p.price for p in Product.query.filter_by(seller_id=farmer_id, is_active=True).all()]
        if prices:
            farmer_stats['price_range'] = {
                'min': min(prices),
                'max': max(prices)
            }
    
    # Get similar farmers (same location or farm type)
    similar_farmers = User.query.filter(
        User.user_type == 'farmer',
        User.id != farmer_id,
        or_(
            User.farm_location == farmer.farm_location,
            User.farm_type == farmer.farm_type
        )
    ).limit(3).all()
    
    return render_template('marketplace/farmer_profile_public.html', 
                         farmer=farmer, 
                         products=products,
                         farmer_stats=farmer_stats,
                         similar_farmers=similar_farmers)

@marketplace_bp.route('/product/<int:product_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(product_id):
    """Add product review"""
    product = Product.query.get_or_404(product_id)
    
    # Check if user already reviewed this product
    existing_review = ProductReview.query.filter_by(
        product_id=product_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this product.', 'info')
        return redirect(url_for('marketplace.product_detail', id=product_id))
    
    form = ProductReviewForm()
    if form.validate_on_submit():
        review = ProductReview(
            rating=form.rating.data,
            comment=form.comment.data,
            product_id=product_id,
            user_id=current_user.id
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review added successfully!', 'success')
        return redirect(url_for('marketplace.product_detail', id=product_id))
    
    return render_template('marketplace/add_review.html', form=form, product=product)

@marketplace_bp.route('/my-products')
@login_required
def my_products():
    """User's own products - redirect to farmer dashboard"""
    if not current_user.is_farmer():
        flash('Only farmers can view their products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    return redirect(url_for('marketplace.farmer_dashboard'))

@marketplace_bp.route('/product/<int:product_id>/toggle-availability', methods=['POST'])
@login_required
def toggle_availability(product_id):
    """Toggle product availability"""
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        flash('You can only manage your own products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    product.is_available = not product.is_available
    db.session.commit()
    
    status = 'available' if product.is_available else 'unavailable'
    flash(f'Product is now {status}.', 'success')
    return redirect(url_for('marketplace.farmer_dashboard'))

@marketplace_bp.route('/api/search')
def api_search():
    """API endpoint for product search"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        Product.is_available == True,
        or_(
            Product.name.contains(query),
            Product.description.contains(query)
        )
    ).limit(limit).all()
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'seller': product.seller.get_full_name()
        })
    
    return jsonify(results)
