from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.product import Product, ProductCategory, ProductReview
from app.forms.product import ProductForm, ProductReviewForm
from sqlalchemy import or_, desc

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
def index():
    """Marketplace home page with product listings"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'newest')
    
    # Build query
    query = Product.query.filter_by(is_available=True)
    
    # Apply filters
    if search:
        query = query.filter(or_(
            Product.name.contains(search),
            Product.description.contains(search)
        ))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
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
    
    return render_template('marketplace/index.html',
                         products=products,
                         categories=categories,
                         search=search,
                         category_id=category_id,
                         sort_by=sort_by)

@marketplace_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    
    # Get reviews
    reviews = ProductReview.query.filter_by(product_id=product_id).order_by(desc(ProductReview.created_at)).all()
    
    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product_id,
        Product.is_available == True
    ).limit(4).all()
    
    return render_template('marketplace/product_detail.html',
                         product=product,
                         reviews=reviews,
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
        
        # Handle image upload
        if form.image.data:
            # TODO: Implement image upload logic
            pass
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('marketplace.product_detail', product_id=product.id))
    
    return render_template('marketplace/add_product.html', form=form)

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
        return redirect(url_for('marketplace.product_detail', product_id=product_id))
    
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
        return redirect(url_for('marketplace.product_detail', product_id=product_id))
    
    return render_template('marketplace/add_review.html', form=form, product=product)

@marketplace_bp.route('/my-products')
@login_required
def my_products():
    """User's own products"""
    if not current_user.is_farmer():
        flash('Only farmers can view their products.', 'error')
        return redirect(url_for('marketplace.index'))
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(seller_id=current_user.id).order_by(desc(Product.created_at)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('marketplace/my_products.html', products=products)

@marketplace_bp.route('/product/<int:product_id>/toggle-availability')
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
    return redirect(url_for('marketplace.my_products'))

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
