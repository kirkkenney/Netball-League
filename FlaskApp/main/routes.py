from flask import render_template, redirect, url_for, flash, Blueprint
from FlaskApp.models import Match, Team
from flask_login import current_user, login_required
from sqlalchemy import desc
from datetime import date


main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    today = date.today()
    # get 4 most recent matches before today's date
    prev_matches = Match.query.filter(Match.date < today)\
        .order_by(desc(Match.date)).limit(4).all()
    # reverse the list for display
    prev_matches = prev_matches[::-1]
    # get next 4 matches after today's date
    next_matches = Match.query.filter(Match.date >= today)\
        .order_by(Match.date).limit(4).all()
    return render_template('home.html', title='Home',
            prev_matches=prev_matches,
            next_matches=next_matches)


@main.route('/dashboard')
@login_required
def dashboard():
    # dashboard page is restricted to admins, league reps and team captains
    # check user status and direct accordingly
    if current_user.admin_level in ['Admin', 'Rep']:
        return render_template('dashboard.html', title='Dashboard')
    elif current_user.player_status == 'Captain':
        return render_template('dashboard.html', title='Dashboard')
    else:
        flash("You don't have permission to view that page!", 'danger')
        return redirect(url_for('main.home'))


@main.route('/league-info')
@login_required
def league_info():
    teams = Team.query.order_by(desc(Team.points)).all()
    return render_template('league_info.html', title="League Info",
        teams=teams)
