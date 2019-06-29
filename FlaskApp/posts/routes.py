from flask import render_template, redirect, url_for, flash, Blueprint
from FlaskApp import db, mail
from FlaskApp.models import User, Post
from FlaskApp.posts.forms import PostForm
from flask_login import current_user, login_required
from flask_mail import Message
from datetime import datetime


posts = Blueprint('posts', __name__)


@posts.route('/<string:team>/posts/<int:post_id>')
@login_required
def post_page(team, post_id):
    # posts pages are on a per-team basis eg Team1 cannot view posts of Team2
    # check that the current user's team is the same as the team associated
    # with the posts
    if current_user.team != team:
        flash("You must be a player on this team to view this page.", 'danger')
        return redirect(url_for('teams.my_team', user_team=team))
    else:
        # get relevant post from the db
        post = Post.query.get_or_404(post_id)
        return render_template('post_page.html', title=post.title,
            post=post)


@posts.route('/post/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # only post author can delete a post, check that this is the case
    if post.author != current_user:
        flash("You don't have permission to do this!", 'danger')
        return redirect(url_for('posts.post_page', team=post.team, post_id=post.id))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('teams.team_posts', team=post.team))


@posts.route('/<string:team>/posts/new', methods=['GET', 'POST'])
@login_required
def add_new_post(team):
    # posts pages are on a per-team basis eg Team1 cannot view posts of Team2
    # check that the current user's team is the same as the team associated
    # with the posts
    if current_user.team != team:
        flash("You must be a player on this team to view this page.", 'danger')
        return redirect(url_for('teams.my_team', user_team=team))
    else:
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data,
                    content=form.content.data,
                    date_posted=datetime.now(),
                    team=current_user.team,
                    author=current_user)
            db.session.add(post)
            db.session.commit()
            # allows captain to send the post as an email to all team players
            # (logic to check user is a captain is handled in the HTML templating)
            if form.send_email.data:
                send_post_email(post)
            return redirect(url_for('teams.team_posts', team=team))
    return render_template('new_post.html', title=f'New {team} Post', form=form)


def send_post_email(post):
    with mail.connect() as conn:
        # get all users for this team
        users = User.query.filter_by(team=post.team).all()
        for user in users:
            message = render_template('post_email.html',
            post=post)
            subject = f'New Post In {post.team}'
            sender = 'noreply@demo.com'
            msg = Message(recipients=[user.email],
            sender=sender,
            subject=subject,
            html=message)
            conn.send(msg)
