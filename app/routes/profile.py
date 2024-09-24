from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..forms import UpdateProfileForm, ChangePasswordForm
from ..models import User, Product, Order, db

profile = Blueprint('profile', __name__)

@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    update_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    if update_form.validate_on_submit():
        current_user.username = update_form.username.data
        current_user.location = update_form.location.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile.user_profile'))

    if password_form.validate_on_submit():
        if check_password_hash(current_user.password, password_form.current_password.data):
            current_user.password = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile.user_profile'))

    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    products = Product.query.filter_by(owner_id=current_user.id).order_by(Product.date_added.desc()).all()

    return render_template('pages/profile.html', update_form=update_form, password_form=password_form, orders=orders, products=products)
