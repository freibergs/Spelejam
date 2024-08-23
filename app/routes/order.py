from flask import Blueprint, render_template, redirect, url_for, session, flash, current_app
from flask_login import current_user
from ..forms import OrderForm, PhoneVerificationForm
from ..models import Product, Order, db
import json
import stripe

order = Blueprint('order', __name__)

@order.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    products = []
    total_price = 0
    for product_id, quantity in cart_items.items():
        product = Product.query.get(product_id)
        if product:
            products.append({
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': product.price * quantity
            })
            total_price += product.price * quantity
    
    form = OrderForm()
    if current_user.is_authenticated:
        form.customer_email.data = current_user.email
    
    default_shipping_method = 'omniva'
    shipping_cost = current_app.config['OMNIVA_COST'] if default_shipping_method == 'omniva' else 0.0
    
    if form.validate_on_submit():
        if form.shipping_method.data == 'omniva':
            shipping_cost = current_app.config['OMNIVA_COST']
            form.omniva_pickup_point.flags.required = True
        else:
            shipping_cost = 0.0
            form.omniva_pickup_point.flags.required = False
        
        total_price_with_shipping = total_price + shipping_cost

        order = Order(
            products=json.dumps(products),
            total_price=total_price_with_shipping,
            shipping_cost=shipping_cost,
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            customer_phone=form.customer_phone.data,
            shipping_method=form.shipping_method.data,
            omniva_pickup_point=form.omniva_pickup_point.data if form.shipping_method.data == 'omniva' else None,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()

        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        session_items = [{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': item['quantity'],
        } for item in products]

        if shipping_cost > 0:
            session_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Shipping to {order.omniva_pickup_point}',
                    },
                    'unit_amount': int(shipping_cost * 100),
                },
                'quantity': 1,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=session_items,
            mode='payment',
            success_url=url_for('order.order_success', order_id=order.id, _external=True),
            cancel_url=url_for('order.payment_failed', order_id=order.id, _external=True),
        )

        session['order_id'] = order.id

        return redirect(checkout_session.url)

    return render_template(
        'flow/checkout.html', 
        form=form, 
        products=products, 
        shipping_cost=shipping_cost, 
        total_price=total_price,
        default_shipping_method=default_shipping_method
    )

@order.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get_or_404(order_id)

    order.status = 'paid'
    db.session.commit()

    products = json.loads(order.products)
    for item in products:
        product = Product.query.get(item['product_id'])
        if product:
            product.stock -= item['quantity']
            db.session.add(product)

    db.session.commit()

    session.pop('cart', None)

    flash('Thank you for your purchase!', 'success')
    return redirect(url_for('order.order_details', order_id=order.id))

@order.route('/payment_failed/<int:order_id>')
def payment_failed(order_id):
    order = Order.query.get_or_404(order_id)

    order.status = 'failed'
    db.session.commit()

    flash('Payment failed. Please try again.', 'danger')
    return redirect(url_for('order.checkout'))

@order.route('/order_details/<int:order_id>', methods=['GET', 'POST'])
def order_details(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.is_authenticated:
        if current_user.id == order.user_id or current_user.user_level > 2:
            return render_template('flow/order_details.html', order=order)

    if 'order_id' in session and session['order_id'] == order_id:
        return render_template('flow/order_details.html', order=order)

    form = PhoneVerificationForm()

    if form.validate_on_submit():
        if form.phone_number.data == order.customer_phone:
            session['order_id'] = order_id
            return redirect(url_for('order.order_details', order_id=order.id))
        else:
            flash('Incorrect phone number.', 'danger')

    return render_template('utils/order_verification.html', form=form)
