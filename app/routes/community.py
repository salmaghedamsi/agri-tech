from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.forum import ForumPost, ForumComment, ForumCategory
from app.forms.forum import ForumPostForm, ForumCommentForm
from sqlalchemy import desc, or_

community_bp = Blueprint('community', __name__)

@community_bp.route('/')
def index():
    """Community forum home page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'latest')
    
    # Build query
    query = ForumPost.query
    
    if search:
        query = query.filter(or_(
            ForumPost.title.contains(search),
            ForumPost.content.contains(search)
        ))
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Apply sorting
    if sort_by == 'popular':
        query = query.order_by(desc(ForumPost.view_count))
    elif sort_by == 'most_commented':
        query = query.order_by(desc(ForumPost.comments.count()))
    else:  # latest
        query = query.order_by(desc(ForumPost.created_at))
    
    # Paginate results
    posts = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get categories
    categories = ForumCategory.query.all()
    
    return render_template('community/index.html',
                         posts=posts,
                         categories=categories,
                         search=search,
                         category_id=category_id,
                         sort_by=sort_by)

@community_bp.route('/category/<int:category_id>')
def category_posts(category_id):
    """Posts in a specific category"""
    category = ForumCategory.query.get_or_404(category_id)
    
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'latest')
    
    query = ForumPost.query.filter_by(category_id=category_id)
    
    if sort_by == 'popular':
        query = query.order_by(desc(ForumPost.view_count))
    elif sort_by == 'most_commented':
        query = query.order_by(desc(ForumPost.comments.count()))
    else:  # latest
        query = query.order_by(desc(ForumPost.created_at))
    
    posts = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('community/category_posts.html',
                         category=category,
                         posts=posts,
                         sort_by=sort_by)

@community_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """Forum post detail page"""
    post = ForumPost.query.get_or_404(post_id)
    
    # Increment view count
    post.increment_view_count()
    
    # Get comments
    page = request.args.get('page', 1, type=int)
    comments = ForumComment.query.filter_by(post_id=post_id, parent_id=None).order_by(ForumComment.created_at).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('community/post_detail.html',
                         post=post,
                         comments=comments)

@community_bp.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new forum post"""
    form = ForumPostForm()
    form.category_id.choices = [(c.id, c.name) for c in ForumCategory.query.all()]
    
    if form.validate_on_submit():
        post = ForumPost(
            title=form.title.data,
            content=form.content.data,
            category_id=form.category_id.data,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('community.post_detail', post_id=post.id))
    
    return render_template('community/create_post.html', form=form)

@community_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    form = ForumCommentForm()
    if form.validate_on_submit():
        comment = ForumComment(
            content=form.content.data,
            post_id=post_id,
            author_id=current_user.id,
            parent_id=request.form.get('parent_id', type=int)  # For nested comments
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Comment added successfully!', 'success')
        return redirect(url_for('community.post_detail', post_id=post_id))
    
    return render_template('community/post_detail.html', post=post, form=form)

@community_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    """Like/unlike forum post"""
    post = ForumPost.query.get_or_404(post_id)
    
    # TODO: Implement like functionality with user tracking
    post.like_count += 1
    db.session.commit()
    
    return jsonify({'likes': post.like_count})

@community_bp.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    """Like/unlike forum comment"""
    comment = ForumComment.query.get_or_404(comment_id)
    
    # TODO: Implement like functionality with user tracking
    comment.like_count += 1
    db.session.commit()
    
    return jsonify({'likes': comment.like_count})

@community_bp.route('/my-posts')
@login_required
def my_posts():
    """User's forum posts"""
    page = request.args.get('page', 1, type=int)
    posts = ForumPost.query.filter_by(author_id=current_user.id).order_by(desc(ForumPost.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('community/my_posts.html', posts=posts)

@community_bp.route('/search')
def search():
    """Search forum posts"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('community.index'))
    
    posts = ForumPost.query.filter(or_(
        ForumPost.title.contains(query),
        ForumPost.content.contains(query)
    )).order_by(desc(ForumPost.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('community/search_results.html',
                         posts=posts,
                         query=query)

@community_bp.route('/api/search')
def api_search():
    """API endpoint for forum search"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify([])
    
    posts = ForumPost.query.filter(or_(
        ForumPost.title.contains(query),
        ForumPost.content.contains(query)
    )).limit(limit).all()
    
    results = []
    for post in posts:
        results.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': post.author.get_full_name(),
            'created_at': post.created_at.isoformat(),
            'comment_count': post.get_comment_count(),
            'view_count': post.view_count
        })
    
    return jsonify(results)

@community_bp.route('/categories')
def categories():
    """Forum categories page"""
    categories = ForumCategory.query.all()
    
    # Add post counts to categories
    for category in categories:
        category.post_count = category.get_post_count()
        category.latest_post = category.get_latest_post()
    
    return render_template('community/categories.html', categories=categories)
