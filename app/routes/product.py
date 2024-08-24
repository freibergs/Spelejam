from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ..models import Product, Category, Tag
from .. import db
from ..utils import save_image, convert_url_to_api
import json
import requests
from bs4 import BeautifulSoup
from slugify import slugify
from markupsafe import Markup
from ..forms import AddProductForm, EditProductForm

product = Blueprint('product', __name__)

@product.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.user_level < 2:
        flash('You do not have permission to add products. Please verify your account.', 'danger')
        return redirect(url_for('main.index'))

    form = AddProductForm()

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        
        main_image_filename = save_image(form.main_image.data) if form.main_image.data else None

        uploaded_files = request.files.getlist('images')
        image_filenames = [save_image(file) for file in uploaded_files if file]

        players_json = form.players.data
        try:
            players_data = json.loads(players_json)
            players = [player['value'] for player in players_data]
            players_str = ','.join(players)
        except json.JSONDecodeError:
            flash('There was an error processing the number of players.', 'danger')
            return redirect(url_for('product.add_product'))

        new_product = Product(
            name=form.name.data,
            slug=slug,
            description=form.description.data,
            price=form.price.data,
            condition=form.condition.data,
            missing_parts=form.missing_parts.data,
            main_image=main_image_filename,
            images=','.join(image_filenames),
            bgg_url=form.bgg_url.data,
            owner_id=current_user.id,
            category_id=form.category.data,
            players=players_str
        )

        tag_names = [tag['value'] for tag in json.loads(form.tags.data)]
        tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
        new_product.tags.extend(tags)

        db.session.add(new_product)
        db.session.commit()

        flash(Markup(f'Product added successfully! <a href="{url_for("product.product_detail", product_id=new_product.id, slug=new_product.slug)}" class="alert-link">View Product</a>'), 'success')
        return redirect(url_for('main.shop'))

    return render_template('product/add_product.html', form=form, tags=Tag.query.all())

from sqlalchemy import func, and_

@product.route('/product/<slug>-<int:product_id>')
def product_detail(slug, product_id):
    product = Product.query.get_or_404(product_id)

    if product.slug != slug:
        return redirect(url_for('product.product_detail', slug=product.slug, product_id=product.id))
    
    max_related_products = 10

    related_products_query = db.session.query(Product).filter(
        Product.id != product.id,
        Product.stock > 0,
        Product.category_id == product.category_id
    ).outerjoin(Product.tags)

    if product.tags:
        related_products_query = related_products_query.filter(
            Tag.id.in_([tag.id for tag in product.tags])
        ).group_by(Product.id).order_by(
            func.count(Tag.id).desc(),
            Product.date_added.desc()
        )

    related_products = related_products_query.limit(max_related_products).all()
    related_count = len(related_products)

    if related_count < max_related_products:
        additional_products_query = db.session.query(Product).filter(
            Product.id != product.id,
            Product.stock > 0,
            Product.category_id == product.category_id
        ).order_by(Product.date_added.desc())

        additional_products = additional_products_query.limit(max_related_products - related_count).all()
        related_products.extend(additional_products)
        related_count = len(related_products)

    if related_count < max_related_products and product.tags:
        single_tag_products_query = db.session.query(Product).filter(
            Product.id != product.id,
            Product.stock > 0,
            Product.tags.any(Tag.id.in_([tag.id for tag in product.tags]))
        ).order_by(Product.date_added.desc())

        single_tag_products = single_tag_products_query.limit(max_related_products - related_count).all()
        related_products.extend(single_tag_products)

    related_products = list({prod.id: prod for prod in related_products}.values())

    return render_template('product/product.html', product=product, related_products=related_products)

@product.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.owner_id != current_user.id and current_user.user_level <= 2:
        flash('You do not have permission to edit this product.', 'danger')
        return redirect(url_for('main.index'))

    form = EditProductForm(obj=product)

    form.players.data = json.dumps([{'value': player} for player in product.players.split(',')])
    form.tags.data = json.dumps([{'value': tag.name} for tag in product.tags])

    if not product.bgg_url:
        form.bgg_url.render_kw = {'readonly': False}
    else:
        form.bgg_url.render_kw = {'readonly': True}

    if form.validate_on_submit():
        product.description = form.description.data
        product.price = form.price.data
        product.condition = form.condition.data
        product.missing_parts = form.missing_parts.data
        product.category_id = form.category.data

        if not product.bgg_url:
            product.bgg_url = form.bgg_url.data

        players_json = form.players.data
        try:
            players_data = json.loads(players_json)
            players = [player['value'] for player in players_data]
            product.players = ','.join(players)
        except json.JSONDecodeError:
            flash('There was an error processing the number of players.', 'danger')
            return redirect(url_for('product.edit_product', product_id=product.id))

        tag_names = [tag['value'] for tag in json.loads(form.tags.data)]
        tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
        product.tags = tags

        if form.main_image.data:
            product.main_image = save_image(form.main_image.data)

        uploaded_files = request.files.getlist('images')
        if uploaded_files and any(file.filename for file in uploaded_files):
            image_filenames = [save_image(file) for file in uploaded_files if file]
            product.images = ','.join(image_filenames)

        db.session.commit()

        flash(Markup(f'Product updated! <a href="{url_for("product.product_detail", product_id=product.id, slug=product.slug)}" class="alert-link">View Product</a>'), 'success')

        # Determine where to redirect after updating
        next_page = request.form.get('next')
        if next_page:
            return redirect(next_page + '#products')
        else:
            return redirect(url_for('main.shop'))

    return render_template('product/edit_product.html', form=form, product=product, tags=Tag.query.all())


@product.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    next_page = request.form.get('next')
    product = Product.query.get_or_404(product_id)

    if product.owner_id != current_user.id and current_user.user_level <= 2:
        flash('You do not have permission to delete this product.', 'danger')
    else:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully.', 'success')

    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('main.index'))

@product.route('/autofill_bgg_info', methods=['POST'])
@login_required
def autofill_bgg_info():
    bgg_url = request.form.get('bgg_url')
    
    if not bgg_url:
        return jsonify({'success': False, 'error': 'Invalid BGG URL'}), 400

    api_url = convert_url_to_api(bgg_url)
    response = requests.get(api_url)
    
    if response.status_code != 200:
        return jsonify({'success': False, 'error': 'Failed to retrieve data from BGG'}), 500
    
    soup = BeautifulSoup(response.content, 'xml')
    
    name_tag = soup.find('name', primary="true")
    game_name = name_tag.text if name_tag else "N/A"
    
    description_tag = soup.find('description')
    description = description_tag.text if description_tag else "N/A"
    
    min_players_tag = soup.find('minplayers')
    max_players_tag = soup.find('maxplayers')
    
    min_players = int(min_players_tag.text) if min_players_tag else 1
    max_players = int(max_players_tag.text) if max_players_tag else 10
    
    players = [str(i) for i in range(min_players, max_players + 1)]
    
    return jsonify({
        'success': True,
        'name': game_name,
        'description': description,
        'players': players
    })