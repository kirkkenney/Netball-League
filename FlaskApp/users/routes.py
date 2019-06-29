from flask import (render_template, redirect, url_for, flash, request,
    Blueprint, current_app)
from FlaskApp import db, bcrypt, mail
from FlaskApp.models import User, PendingUser, Team
from FlaskApp.users.forms import (AddPlayerRequest, LoginForm,
    AddPlayer, UpdateAccountForm, RequestResetForm, ResetPasswordForm,
    ChangePassword)
from flask_login import login_user, logout_user, current_user, login_required
import secrets
from PIL import Image
import os
from flask_mail import Message


users = Blueprint('users', __name__)


@users.route('/register-player', methods=['POST', 'GET'])
@login_required
def register_player():
    # only team captains can add new players to their team
    if current_user.player_status == 'Captain':
        form = AddPlayerRequest()
        if form.validate_on_submit():
            # generate a random hashed password for the new user
            hashed_password = bcrypt.generate_password_hash(secrets.token_hex(8)).decode('utf-8')
            # new users must be confirmed by an admin or a rep. New users
            # therefore adding to a PendingUser db whilst awaiting approval
            user = PendingUser(name=form.name.data,
                    email=form.email.data,
                    team=current_user.team,
                    password=hashed_password,
                    address_1=form.address_1.data,
                    address_2=form.address_2.data,
                    postcode=form.postcode.data,
                    association_id=form.association_id.data)
            db.session.add(user)
            db.session.commit()
            flash(f'{form.name.data} has been submitted for approval', 'success')
            return redirect(url_for('main.dashboard'))
    else:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    return render_template('register_player.html', title='Register New Player',
        form=form)


@users.route('/admin/users', methods=['POST', 'GET'])
@login_required
def users_list():
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    # list all users for admin viewing and actions
    pending_users = PendingUser.query.all()
    approved_users = User.query.all()
    return render_template('users_list.html', title='All Users',
        pending_users=pending_users, approved_users=approved_users)


@users.route('/admin/add-player', methods=['POST', 'GET'])
@login_required
def admin_add_player():
    # admin/reps can add players to any team, with any level of permissions
    # for simplicity, route is therefore handled differently to captain functionality
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    form = AddPlayer()
    # get list of teams in db for admin/rep to assign new player to
    form.team.choices = [(a.name, a.name) for a in Team.query.order_by(Team.name)]
    if form.validate_on_submit():
        # generate random hashed password
        hashed_password = bcrypt.generate_password_hash(secrets.token_hex(8)).decode('utf-8')
        user = User(name=form.name.data,
                email=form.email.data,
                password=hashed_password,
                team=form.team.data,
                player_status=form.player_status.data,
                admin_level=form.admin_level.data,
                address_1=form.address_1.data,
                address_2=form.address_2.data,
                postcode=form.postcode.data,
                association_id=form.association_id.data)
        db.session.add(user)
        db.session.commit()
        # get new user's email to send them details about their account
        user_email = User.query.filter_by(email=form.email.data).first()
        user_approved_email(user_email)
        flash(f'{form.name.data} has been added to {form.team.data}', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('admin_new_player.html', title='Add New Player', form=form)


def user_approved_email(user):
    token = user.get_reset_token()
    msg = Message('Netball Registration Approved',
        sender='noreply@demo.com',
        recipients=[user.email])
    # _external=True argument is used to generate an absolute URL, instead of relative
    msg.body = f'''Your registration with {user.team} has been approved. \n \n
    Please visit the following link to set your password: \n \n
{url_for('users.reset_token', token=token, _external=True)} \n \n
If you did not make this request, then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@users.route('/delete/<string:user_email>', methods=['POST'])
@login_required
def delete_user(user_email):
    # only admins and reps can delete a user
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    # get both pending users and approved users from db
    pending_email = PendingUser.query.filter_by(email=user_email).first()
    approved_email = User.query.filter_by(email=user_email).first()
    # handle deletion logic depending on whether deletion refers to pending
    # user or approved user
    if pending_email:
        db.session.delete(pending_email)
        db.session.commit()
        flash('User deleted!', 'info')
    elif approved_email:
        db.session.delete(approved_email)
        db.session.commit()
        flash('User deleted!', 'info')
    else:
        flash('Unable to delete user!', 'info')
    return redirect(url_for('users.users_list'))


@users.route('/approve/<string:user_email>', methods=['POST'])
@login_required
def approve_user(user_email):
    # only admins and reps can approve new users
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    pending_user = PendingUser.query.filter_by(email=user_email).first()
    if pending_user:
        # once pending user has been approved, transfer their data from
        # PendingUser db table, to User db table
        user = User(name=pending_user.name,
                email=pending_user.email,
                password=pending_user.password,
                team=pending_user.team,
                player_status='Approved Player',
                admin_level='User',
                address_1=pending_user.address_1,
                address_2=pending_user.address_2,
                postcode=pending_user.postcode,
                approved_by=current_user.name,
                association_id=pending_user.association_id)
        # add to User db table and remove from PendingUser db table
        db.session.add(user)
        db.session.delete(pending_user)
        db.session.commit()
        # get new user details and email them about their account
        new_id = User.query.filter_by(email=user.email).first()
        user_approved_email(new_id)
        flash(f'{pending_user.name} added to {pending_user.team}!', 'success')
    else:
        flash('Unable to delete user!', 'info')
    return redirect(url_for('users.users_list'))


@users.route('/account/<int:user_id>/<string:user>', methods=['GET', 'POST'])
@login_required
def account(user_id, user):
    # current user is same as user being queried, give the option of
    # updating their account
    if user_id == current_user.id:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                # if they change their profile picture, run function to resize,
                # reformat etc
                picture_file = save_picture(form.picture.data)
                current_user.profile_pic = picture_file
            current_user.email = form.email.data
            current_user.address_1 = form.address_1.data
            current_user.address_2 = form.address_2.data
            current_user.postcode = form.postcode.data
            current_user.association_id = form.association_id.data
            db.session.commit()
            flash('Account updated!', 'success')
            return redirect(url_for('users.account', user_id=current_user.id, user=current_user.name))
        # if request method is GET, prepopulate form fields with the
        # current user data
        elif request.method == 'GET':
            form.email.data = current_user.email
            form.address_1.data = current_user.address_1
            form.address_2.data = current_user.address_2
            form.postcode.data = current_user.postcode
            form.association_id.data = current_user.association_id
        # get user's profile picture for HTML rendering
        image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('account.html', title='My Account',
            image_file=image_file, form=form)
    else:
        player = User.query.filter_by(id=user_id).first()
        image_file = url_for('static', filename='profile_pics/' + player.profile_pic)
        return render_template('user_account.html', title=player.name,
            player=player, image_file=image_file)


def save_picture(form_picture):
    # generate a randon string for file name
    random_hex = secrets.token_hex(8)
    # remove name of original file, make a note of the extension (jpeg, png)
    _, f_ext = os.path.splitext(form_picture.filename)
    # rename file with random string and file extension
    picture_fn = random_hex + f_ext
    # define where to store the image
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    # specify size of uploaded image
    output_size = (250, 250)
    # confirm resize, and save to disk
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    # get previous profile picture
    prev_picture = os.path.join(current_app.root_path, 'static/profile_pics', current_user.profile_pic)
    # if the previous profile pic is found on disk, and previous profile
    # pic is NOT the default, delete it from disk
    if os.path.exists(prev_picture) and current_user.profile_pic != 'default.jpg':
        os.remove(prev_picture)
    return picture_fn


@users.route('/account/change-password/<int:user_id>/<string:user>', methods=['GET', 'POST'])
@login_required
def change_password(user_id, user):
    if user_id == current_user.id:
        get_user = User.query.get(user_id)
        form = ChangePassword()
        image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        if form.validate_on_submit():
            new_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            get_user.password = new_pw
            db.session.commit()
            flash('Password changed!', 'success')
            return redirect(url_for('main.home'))
    else:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    return render_template('change_password.html', title='Change Password',
        form=form, image_file=image_file)


@users.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/login', methods=['POST', 'GET'])
def login():
    # if the user is already logged in, redirect them to the home page
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # bcrypt method takes db query and form data as parameters to check
        # if the email provided is in the db, and the password they entered
        # matches the decoded password hash store, log them in
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if user is trying to access a restrcited page, they will be
            # prompted to login. Below gets their requested page and passes
            # it to below return ternary conditional
            next_page = request.args.get('next')
            flash('Login was successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Cannot log in with those details. Check your email and password are correct!', 'danger')
    return render_template('login.html', title='Login', form=form)


def send_reset_email(user):
    # if user wants to reset their password, query call get_reset_token
    # function in User db model, and send them an email
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
        sender='noreply@demo.com',
        recipients=[user.email])
    # _external=True argument is used to generate an absolute URL, instead of relative
    msg.body = f'''To reset your password, visit the following link: \n \n
{url_for('users.reset_token', token=token, _external=True)} \n \n
If you did not make this request, then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@users.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    # check that user is not currently logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # call method from User class of models.py
    user = User.verify_reset_token(token)
    if user is None:
        flash('Password reset has expired or is invalid. Please try again.', 'warning')
        return redirect(url_for('users.reset_request'))
    # if user is valid:
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # take password value and hash it using bcrypt
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
