from flask import Blueprint, render_template, redirect, url_for, flash, current_app as app
from flask_login import login_required, current_user
from ..models import Blog, db
from ..forms import BlogForm
from slugify import slugify
import os
from ..utils import save_image

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def all_blogs():
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blog/blogs.html', blogs=blogs)

@blog.route('/blog/<slug>')
def single_blog(slug):
    blog = Blog.query.filter_by(url_slug=slug).first_or_404()
    return render_template('blog/single_blog.html', blog=blog)

@blog.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_blog():
    if current_user.user_level <= 2:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blog.all_blogs'))

    form = BlogForm()
    if form.validate_on_submit():
        title = form.title.data
        
        cover_image_filename = save_image(form.cover_image.data) if form.cover_image.data else None

        blog_post = Blog(
            title=title,
            url_slug=slugify(title),
            content=form.content.data,
            meta_title=form.meta_title.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            cover_image=cover_image_filename
        )
        db.session.add(blog_post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog.all_blogs'))
    return render_template('blog/create_blog.html', form=form)

@blog.route('/blog/update/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    blog_post = Blog.query.get_or_404(blog_id)
    if current_user.user_level <= 2:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blog.single_blog', slug=blog_post.url_slug))

    form = BlogForm(obj=blog_post)
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.url_slug = slugify(blog_post.title)
        blog_post.content = form.content.data
        blog_post.meta_title = form.meta_title.data
        blog_post.meta_description = form.meta_description.data
        blog_post.meta_keywords = form.meta_keywords.data

        if form.cover_image.data:
            if blog_post.cover_image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], blog_post.cover_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            blog_post.cover_image = save_image(form.cover_image.data)

        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('blog.single_blog', slug=blog_post.url_slug))
    return render_template('blog/update_blog.html', form=form, blog_post=blog_post)

@blog.route('/blog/delete/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog_post = Blog.query.get_or_404(blog_id)
    if current_user.user_level <= 2:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('blog.single_blog', slug=blog_post.url_slug))

    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('blog.all_blogs'))