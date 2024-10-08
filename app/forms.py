from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TelField, SelectField, RadioField, TextAreaField, DecimalField, IntegerField, FileField
from wtforms.validators import InputRequired, Length, ValidationError, Email, EqualTo, NumberRange
from wtforms.widgets import HiddenInput
from .models import User, Category
from .utils import get_omnivas

class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    location = StringField(validators=[Length(max=120)], render_kw={"placeholder": "Location"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('This username is already taken. Please choose a different one.')

    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError('This email is already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class AddProductForm(FlaskForm):
    bgg_url = StringField('BoardGameGeek URL', validators=[Length(max=255)])
    name = StringField('Name', validators=[InputRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[InputRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=0)], places=2)
    players = StringField('Number of Players', validators=[InputRequired()], render_kw={"placeholder": "Add number of players"})
    condition = IntegerField('Condition', validators=[InputRequired(), NumberRange(min=1, max=10)], widget=HiddenInput())
    missing_parts = StringField('Missing Parts', validators=[Length(max=255)])
    category = SelectField('Category', validators=[InputRequired()], coerce=int)
    tags = StringField('Tags', validators=[Length(max=255)])
    main_image = FileField('Main Image', validators=[InputRequired()])
    images = FileField('Additional Images', render_kw={"multiple": True})
    submit = SubmitField('Add Product')

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]

class EditProductForm(AddProductForm):
    def __init__(self, product=None, *args, **kwargs):
        super(EditProductForm, self).__init__(*args, **kwargs)
        self.name.render_kw = {'readonly': True}
        self.main_image.validators = []
        self.main_image.render_kw = {'required': False}
        self.submit.label.text = 'Edit Product'
        
        if product and product.bgg_url:
            self.bgg_url.render_kw = {'readonly': True}

class OrderForm(FlaskForm):
    customer_name = StringField('Name', validators=[InputRequired(), Length(max=120)])
    customer_email = EmailField('Email', validators=[InputRequired(), Email(), Length(max=120)])
    customer_phone = TelField('Phone Number', validators=[InputRequired(), Length(max=20)])
    shipping_method = RadioField('Shipping Method', validators=[InputRequired()],
                                 choices=[('self_pickup', 'Self Pickup'), ('omniva', 'Omniva Pickup Point')])
    omniva_pickup_point = SelectField('Omniva Pickup Point', validators=[InputRequired()],
                                      choices=[(location, location) for location in get_omnivas()])
    submit = SubmitField('Place Order')

class PhoneVerificationForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[InputRequired(), Length(min=8, max=15)])
    submit = SubmitField('Verify')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=80)])
    location = StringField('Location', validators=[Length(max=120)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=4, max=20)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])
    meta_title = StringField('Meta Title')
    meta_description = TextAreaField('Meta Description')
    meta_keywords = StringField('Meta Keywords')
    cover_image = FileField('Cover Image')