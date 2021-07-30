from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Post
from flaskblog.posts.forms import PostForm

posts = Blueprint('posts', __name__)

#Making a post
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
#You need to be logged in to make a post
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        #The posts has been made
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

#Looking at a post
@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#Editing a post (Must be logged in to edit post and can only be your own post)
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
        #If the author of the post is not the current user then show a 403 error
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        #Editing the title or content of the post
        flash('Your Post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

#Deleting a post (Must be logged in to delete post and can only be your own post)
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
#You need a login to delete a post
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
        #If you are not the author of the post a 403 error will run
    db.session.delete(post)
    db.session.commit()
    #Post has been deleted
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))