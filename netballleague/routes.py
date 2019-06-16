from flask import render_template, redirect, url_for, flash, request
from netballleague import app, db, bcrypt
from netballleague.models import User, Match, PendingUser, Team
from netballleague.forms import (AddPlayerRequest, AddMatch, LoginForm,
    AddPlayer, UpdateAccountForm)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc
import secrets
from PIL import Image
import os


@app.route('/')
@app.route('/home')
def home():
    # matches = Match.query.all()
    matches = Match.query.order_by(Match.date).all()
    return render_template('home.html', title='Home', matches=matches)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.admin_level == 'Admin' or current_user.admin_level == 'Rep':
        return render_template('dashboard.html', title='Dashboard')
    elif current_user.player_status == 'Captain':
        return render_template('dashboard.html', title='Dashboard')
    else:
        flash("You don't have permission to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route('/match/<int:match_id>')
def match_page(match_id):
    match = Match.query.get_or_404(match_id)
    return render_template('match_details.html',
        title=f'{match.home_team}-vs-{match.away_team}', match=match)


@app.route('/register-player', methods=['POST', 'GET'])
@login_required
def register_player():
    if current_user.player_status == 'Captain':
        form = AddPlayerRequest()
        if form.validate_on_submit():
            user = PendingUser(name=form.name.data, email=form.email.data,
                team=current_user.team, password='password')
            db.session.add(user)
            db.session.commit()
            flash(f'{form.name.data} has been submitted for approval', 'success')
            return redirect(url_for('dashboard'))
    else:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    return render_template('register_player.html', title='Register New Player',
        form=form)


@app.route('/admin/add-player', methods=['POST', 'GET'])
@login_required
def admin_add_player():
    if current_user.admin_level != 'Admin' and current_user.admin_level != 'Rep':
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    form = AddPlayer()
    if form.validate_on_submit():
        # generate hashed password from form data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password,
            team=form.team.data, player_status=form.player_status.data,
            admin_level=form.admin_level.data)
        db.session.add(user)
        db.session.commit()
        flash(f'''{form.name.data} - {form.email.data} - {form.team.data}
            - {form.player_status.data} - {form.admin_level.data} added!''', 'success')
        return redirect(url_for('dashboard'))
    return render_template('admin_new_player.html', title='Add New Player', form=form)


@app.route('/admin/add-match', methods=['GET', 'POST'])
@login_required
def add_match():
    if current_user.admin_level != 'Admin' and current_user.admin_level != 'Rep':
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    form = AddMatch()
    if form.validate_on_submit():
        match = Match(home_team=form.home_team.data, away_team=form.away_team.data,
            location=form.location.data, time=form.time.data, date=form.date.data)
        db.session.add(match)
        db.session.commit()
        print(form.date.data)
        flash('Match has been added to the roster', 'success')
        return redirect(url_for('home'))
    return render_template('add_match.html', title='Add Match', form=form)


@app.route('/admin/users', methods=['POST', 'GET'])
@login_required
def users_list():
    if current_user.admin_level != 'Admin' and current_user.admin_level != 'Rep':
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    pending_users = PendingUser.query.all()
    approved_users = User.query.all()
    return render_template('users_list.html', title='All Users',
        pending_users=pending_users, approved_users=approved_users)


@app.route('/delete/<string:user_email>', methods=['POST'])
@login_required
def delete_user(user_email):
    if current_user.admin_level != 'Admin' and current_user.admin_level != 'Rep':
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    pending_email = PendingUser.query.filter_by(email=user_email).first()
    approved_email = User.query.filter_by(email=user_email).first()
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
    return redirect(url_for('users_list'))


@app.route('/approve/<string:user_email>', methods=['POST'])
@login_required
def approve_user(user_email):
    if current_user.admin_level != 'Admin' and current_user.admin_level != 'Rep':
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('home'))
    pending_user = PendingUser.query.filter_by(email=user_email).first()
    if pending_user:
        user = User(name=pending_user.name, email=pending_user.email,
            password='password', team=pending_user.team,
            player_status='Approved Player', admin_level='User')
        db.session.add(user)
        db.session.delete(pending_user)
        db.session.commit()
        flash(f'{pending_user.name} added to {pending_user.team}!', 'success')
    else:
        flash('Unable to delete user!', 'info')
    return redirect(url_for('users_list'))


@app.route('/<string:user_team>')
def my_team(user_team):
    players = User.query.filter_by(team=user_team)
    print(type(players))
    return render_template('team_details.html', title=user_team, players=players)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.profile_pic)
    if os.path.exists(prev_picture) and current_user.profile_pic != 'default.jpg':
        os.remove(prev_picture)
    return picture_fn


@app.route('/account/<int:user_id>/<string:user>', methods=['GET', 'POST'])
@login_required
def account(user_id, user):
    if user_id == current_user.id:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.profile_pic = picture_file
            current_user.email = form.email.data
            db.session.commit()
            flash('Account updated!', 'success')
            return redirect(url_for('account'))
        elif request.method == 'GET':
            form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
        return render_template('account.html', title='My Account',
            image_file=image_file, form=form)
    else:
        player = User.query.filter_by(id=user_id).first()
        image_file = url_for('static', filename='profile_pics/' + player.profile_pic)
        return render_template('user_account.html', title=player.name,
            player=player, image_file=image_file)


@app.route('/league-info')
@login_required
def league_info():
    teams = Team.query.order_by(desc(Team.points)).all()
    return render_template('league_info.html', title="League Info",
        teams=teams)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # bcrypt method takes db query and form data as parameters to check
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # uses login_manager functionality to manager user session
            # 'remember' parameter is declared as a True/False in form
            login_user(user, remember=form.remember.data)
            # if user is trying to access a restrcited page, they will be
            # prompted to login. Below gets their requested page and passes
            # it to below return ternary conditional
            next_page = request.args.get('next')
            flash('Login was successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Cannot log in with those details. Check your email and password are correct!', 'danger')
    return render_template('login.html', title='Login', form=form)
