from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models import Product, Category, Tag, Blog, Subscription, Review, product_tag
from .. import db
from sqlalchemy.orm import joinedload

main = Blueprint('main', __name__)

@main.route('/shop')
def shop():
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category', None, type=str)
    tag_slugs = request.args.get('tags', None)
    players = request.args.get('players', None)
    sort_by = request.args.get('sort', 'date_added')
    order = request.args.get('order', 'desc')
    search_query = request.args.get('search', '', type=str)
    sold_by = request.args.get('sold_by', None)

    query = Product.query.options(joinedload(Product.category), joinedload(Product.tags)).filter(Product.stock > 0)

    if category_slug:
        category = Category.query.filter_by(url_slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)

    if tag_slugs:
        tag_names = tag_slugs.split(',')
        tags = Tag.query.filter(Tag.url_slug.in_(tag_names)).all()
        query = query.filter(Product.tags.any(Tag.id.in_([tag.id for tag in tags])))

    if players:
        player_counts = players.split(',')
        player_conditions = [Product.players.ilike(f'%{player}%') for player in player_counts]
        query = query.filter(db.or_(*player_conditions))

    if search_query:
        query = query.join(Category).outerjoin(product_tag).outerjoin(Tag).filter(
            db.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%'),
                Category.name.ilike(f'%{search_query}%'),
                Tag.name.ilike(f'%{search_query}%')
            )
        )

    if sold_by == "1":
        query = query.filter_by(owner_id=1)
    elif sold_by == "others":
        query = query.filter(Product.owner_id != 1)

    if sort_by:
        if order == 'desc':
            query = query.order_by(getattr(Product, sort_by).desc())
        else:
            query = query.order_by(getattr(Product, sort_by).asc())

    total_count = query.count()
    products = query.paginate(page=page, per_page=9)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_list_html = render_template('partials/_product_list.html', products=products)
        pagination_html = render_template('partials/_pagination.html', products=products)
        return {'product_list': product_list_html, 'pagination': pagination_html, 'total_count': total_count}

    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('pages/shop.html', products=products, categories=categories, tags=tags, total_count=total_count)

@main.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    existing_subscription = Subscription.query.filter_by(email=email).first()
    if existing_subscription:
        flash('This email is already subscribed.', 'warning')
    else:
        new_subscription = Subscription(email=email)
        db.session.add(new_subscription)
        db.session.commit()
        flash('Thank you for subscribing!', 'success')
    
    return redirect(url_for('main.index'))

@main.route('/')
def index():
    latest_products = Product.query.filter(Product.stock > 0).order_by(Product.date_added.desc()).limit(10).all()
    quality_products = Product.query.filter(Product.stock > 0).order_by(Product.condition.desc()).limit(10).all()
    latest_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(3).all()
    reviews = Review.query.order_by(Review.date_added.desc()).limit(5).all()
    return render_template('pages/index/index_main.html', latest_products=latest_products, quality_products=quality_products, latest_blogs=latest_blogs, reviews=reviews)

