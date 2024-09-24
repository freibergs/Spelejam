from . import db
from flask_login import UserMixin
from datetime import datetime
from slugify import slugify

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    user_level = db.Column(db.Integer, nullable=False)  # 1 - unverified, 2 - verified, 3 - admin

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('chats', lazy=True))
    participants = db.relationship('User', secondary='chat_user', backref=db.backref('chats', lazy=True))

class ChatUser(db.Model):
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    chat = db.relationship('Chat', backref=db.backref('messages', lazy=True))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    url_slug = db.Column(db.String(80), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True, default=0)
    parent = db.relationship('Category', remote_side=[id], backref='children')

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.name)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    url_slug = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        if not self.url_slug:
            self.url_slug = slugify(self.name)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.Integer, nullable=False)  # 1-10
    players = db.Column(db.String(20), nullable=False) 
    missing_parts = db.Column(db.String(120), nullable=True)
    main_image = db.Column(db.String(120), nullable=True)
    images = db.Column(db.Text, nullable=True)
    bgg_url = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    tags = db.relationship('Tag', secondary='product_tag', lazy='subquery', backref=db.backref('products', lazy=True))
    owner = db.relationship('User', backref=db.backref('products', lazy=True))
    stock = db.Column(db.Integer, nullable=False, default=1)
    date_added = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.name)

product_tag = db.Table('product_tag',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    shipping_method = db.Column(db.String(50), nullable=False)  # "omniva" or "self_pickup"
    omniva_pickup_point = db.Column(db.String(120), nullable=True)  # Nullable, only required if shipping_method is "omniva"
    omniva_tracking_code = db.Column(db.String(120), nullable=True, default='')
    status = db.Column(db.String(20), nullable=False, default='pending')
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url_slug = db.Column(db.String(150), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_title = db.Column(db.String(150), nullable=True)
    meta_description = db.Column(db.String(255), nullable=True)
    meta_keywords = db.Column(db.String(255), nullable=True)
    cover_image = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(Blog, self).__init__(*args, **kwargs)
        if not self.url_slug:
            self.url_slug = slugify(self.title)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_subscribed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
