from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from markupsafe import Markup
from ..models import Product

cart = Blueprint('cart', __name__)

@cart.route('/cart')
def view_cart():
    cart_items = session.get('cart', {})
    products = []
    total_price = 0

    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            products.append({
                'product': product,
                'quantity': quantity
            })
            total_price += product.price * quantity

    return render_template('flow/cart.html', products=products, total_price=total_price)

@cart.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart_items = session.get('cart', {})

    product_id_str = str(product_id)

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('main.shop'))

    if product.owner_id != 1:
        flash('This product can not be added to the cart!', 'danger')
        return redirect(url_for('main.shop'))

    current_quantity = cart_items.get(product_id_str, 0)
    if current_quantity + 1 > product.stock:
        flash('Cannot add more items than are available in stock.', 'warning')
    else:
        cart_items[product_id_str] = current_quantity + 1
        session['cart'] = cart_items
        flash(Markup(f'Product added to cart! <a href="{url_for("cart.view_cart")}" class="alert-link">View Cart</a>'), 'success')

    return redirect(url_for('product.product_detail', product_id=product.id, slug=product.slug))

@cart.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_items = session.get('cart', {})

    product_id_str = str(product_id)

    if product_id_str in cart_items:
        del cart_items[product_id_str]
        session['cart'] = cart_items
        flash('Product removed from cart.', 'info')

    return redirect(url_for('cart.view_cart'))

@cart.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart_items = session.get('cart', {})

    product_id_str = str(product_id)

    try:
        quantity = int(request.form.get('quantity', 1))
    except ValueError:
        quantity = 1

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if quantity <= 0:
        cart_items.pop(product_id_str, None)
        flash('Product removed from cart.', 'info')
    elif quantity > product.stock:
        cart_items[product_id_str] = product.stock
        flash(f'Cannot exceed available stock. Quantity adjusted to {product.stock}.', 'warning')
    else:
        cart_items[product_id_str] = quantity
        flash('Cart updated.', 'success')

    session['cart'] = cart_items
    return redirect(url_for('cart.view_cart'))

