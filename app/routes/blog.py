from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..models import Blog, db

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def all_blogs():
    # Fetch all blogs ordered by creation date
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blog/blogs.html', blogs=blogs)

@blog.route('/blog/<slug>')
def single_blog(slug):
    # Fetch the blog by slug
    blog = Blog.query.filter_by(url_slug=slug).first_or_404()
    return render_template('blog/single_blog.html', blog=blog)