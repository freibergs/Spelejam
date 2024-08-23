from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from .utils import fromjson

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('instance.config.Config')

    app.jinja_env.filters['fromjson'] = fromjson

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Product, Message

    from .routes.main import main as main_blueprint
    from .routes.auth import auth as auth_blueprint
    from .routes.product import product as product_blueprint
    from .routes.cart import cart as cart_blueprint
    from .routes.order import order as order_blueprint
    from .routes.chat import chat as chat_blueprint
    from .routes.profile import profile as profile_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(cart_blueprint)
    app.register_blueprint(order_blueprint)
    app.register_blueprint(chat_blueprint)
    app.register_blueprint(profile_blueprint)

    @app.context_processor
    def cart_totals():
        cart_items = session.get('cart', {})
        total_quantity = 0
        total_price = 0.0

        for product_id, quantity in list(cart_items.items()):
            try:
                product = Product.query.get(int(product_id))
                if product:
                    total_quantity += int(quantity)
                    total_price += product.price * int(quantity)
                else:
                    cart_items.pop(product_id)
            except Exception as e:
                cart_items.pop(product_id)
        
        session['cart'] = cart_items
        
        return {'total_quantity': total_quantity, 'total_price': total_price}

    @app.context_processor
    def inject_unread_count():
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Message.query.filter_by(is_read=False).filter(
                Message.receiver_id == current_user.id
            ).count()
        return dict(unread_count=unread_count)

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
