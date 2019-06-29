from flask import render_template, redirect, url_for, flash, Blueprint
from FlaskApp import db
from FlaskApp.models import User, Match, Team, Post
from FlaskApp.teams.forms import AddTeam
from flask_login import current_user, login_required
from sqlalchemy import desc


teams = Blueprint('teams', __name__)


@teams.route('/add-team', methods=['POST', 'GET'])
@login_required
def add_team():
    # only league admins and reps can add a new team
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    form = AddTeam()
    if form.validate_on_submit():
        new_team = Team(name=form.name.data)
        db.session.add(new_team)
        db.session.commit()
        flash(f"{form.name.data} added!", 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_team.html', title='Add New Team', form=form)


@teams.route('/<string:user_team>')
@login_required
def my_team(user_team):
    # get team details to display on page
    players = User.query.filter_by(team=user_team).all()
    team = Team.query.filter_by(name=user_team).first()
    return render_template('team_details.html', title=user_team, players=players,
        team=team)


@teams.route('/<string:team>/posts')
@login_required
def team_posts(team):
    # posts are restricted on a per team basis. Check that current user's
    # team is the same as the team associated with posts being queried
    if current_user.team != team:
        flash("You must be a player on this team to view this page.", 'danger')
        return redirect(url_for('teams.my_team', user_team=team))
    else:
        # get posts from db and order by descending date (newest first)
        posts = Post.query.filter_by(team=team).order_by(desc(Post.date_posted)).all()
        return render_template('team_posts.html', title=f'{team} Posts',
            team=team, posts=posts)


@teams.route('/<string:team>/matches')
@login_required
def team_matches(team):
    # admins and reps can view team matches, but otherwise restricted
    # to users belonging to the team being queried
    # first check if the user is not an admin or a rep
    if current_user.admin_level not in ['Admin', 'Rep']:
        # if the current user does not belong to team being queried, deny access
        if current_user.team != team:
            flash("You must be a player on this team to view this page", 'danger')
            return redirect(url_for('teams.my_team', user_team=team))
        else:
            # if user is admin, rep or player for team being queried
            # get all matches where the user's team is playing at home or away
            matches = Match.query.filter((Match.home_team==team) | \
                (Match.away_team==team)).order_by(Match.date).all()
            return render_template('team_matches.html',
                    title=f'{team} Matches',
                    matches=matches, team=team)
