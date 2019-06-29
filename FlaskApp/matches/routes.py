from flask import render_template, redirect, url_for, flash, request, Blueprint
from FlaskApp import db
from FlaskApp.models import User, Match, Team
from FlaskApp.matches.forms import UpdateScore, UpdateMatch, AddMatch
from flask_login import current_user, login_required
from sqlalchemy import desc
from datetime import date, datetime


matches = Blueprint('matches', __name__)


@matches.route('/match/<int:match_id>', methods=['POST', 'GET'])
def match_page(match_id):
    match = Match.query.get_or_404(match_id)
    form = UpdateScore()
    # get all players associated with current user's team
    # these are displayed on match page for captain to confirm who will
    # be playing
    players_team = User.query.filter_by(team=current_user.team).all()
    # allow_players_submission variable determines whether captain
    # can update who is playing this match. they can only do so up
    # until the beginning of the match
    allow_players_submission = compare_times(match)
    print(allow_players_submission)
    if form.validate_on_submit():
        # home team captain updates score for away team - away team later
        # validates. If/Else checks which way around to update the db
        # according to current user team
        if current_user.team == match.home_team:
            match.away_score = int(form.score.data)
            db.session.commit()
        else:
            match.home_score = int(form.score.data)
            db.session.commit()
        return redirect(url_for('matches.match_page', match_id=match_id))
    return render_template('match_details.html',
            title=f'{match.home_team}-vs-{match.away_team}',
            match=match,
            form=form,
            players_team=players_team,
            allow_players_submission=allow_players_submission)


def compare_times(match):
    now = datetime.now()
    today = date.today()
    condition = True
    if today > match.date:
        condition = False
        return condition
    elif today == match.date:
        if now.hour > match.time.hour:
            condition = False
            return condition
        elif now.hour == match.time.hour:
            if now.minute >= match.time.minute:
                condition = False
                return condition
    else:
        return True


@matches.route('/upcoming-matches')
def upcoming_matches():
    today = date.today()
    # list all matches after today's date
    matches = Match.query.filter(Match.date >= today).order_by(Match.date).all()
    return render_template('upcoming_matches.html',
            title='Upcoming Matches',
            matches=matches)


@matches.route('/previous-matches')
def previous_matches():
    today = date.today()
    # list all matches before today's date
    matches = Match.query.filter(Match.date < today).order_by(desc(Match.date)).all()
    return render_template('previous_matches.html',
            title='Previous Matches',
            matches=matches)


@matches.route('/admin/add-match', methods=['GET', 'POST'])
@login_required
def add_match():
    # only league admins and reps can add a match to the league roster
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('main.home'))
    form = AddMatch()
    # limit form choices for team to only those teams listed in db
    form.home_team.choices = [(a.name, a.name) for a in Team.query.order_by(Team.name)]
    form.away_team.choices = [(a.name, a.name) for a in Team.query.order_by(Team.name)]
    # if no validation errors occur, add the match to the database
    if form.validate_on_submit():
        match = Match(home_team=form.home_team.data,
                away_team=form.away_team.data,
                location=form.location.data,
                time=form.time.data,
                date=form.date.data)
        db.session.add(match)
        db.session.commit()
        print(form.date.data)
        flash('Match has been added to the roster', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_match.html', title='Add Match', form=form)


@matches.route('/update_players/<int:match_id>', methods=["POST"])
@login_required
def update_players(match_id):
    # only team captains can confirm who is playing
    if current_user.player_status != 'Captain':
        flash("You don't have permission to do this!")
        return redirect(url_for('matches.match_page', match_id=match_id))
    # get the selected players (checkboxes in html)
    selected_players = request.form.getlist('users')
    # get the correct match from db
    match = Match.query.get(match_id)
    # check which team to confirm players for according to crrent user's team
    if current_user.team == match.home_team:
        match.home_players = selected_players
        db.session.commit()
    elif current_user.team == match.away_team:
        match.away_players = selected_players
        db.session.commit()
    return redirect(url_for('matches.match_page', match_id=match_id))


@matches.route('/match/confirm/<int:match_id>', methods=['POST'])
@login_required
def confirm_score(match_id):
    # only team captains can confirm the score
    if current_user.player_status != 'Captain':
        flash("You don't have permission to do this!")
        return redirect(url_for('matches.match_page', match_id=match_id))
    match = Match.query.get(match_id)
    if match:
        now = datetime.now()
        # update match data
        if current_user.team == match.home_team:
            match.home_approved = True
            match.home_approved_by = current_user.name
            match.home_approved_time = now
            db.session.commit()
            # go to separate function for passing match data to team data (database)
            update_points(match_id)
            flash(f'{match.home_team} score updated!', 'success')
            return redirect(url_for('matches.match_page', match_id=match.id))
        elif current_user.team == match.away_team:
            match.away_approved = True
            match.away_approved_by = current_user.name
            match.away_approved_time = now
            db.session.commit()
            update_points(match_id)
            flash(f'{match.away_team} score updated!', 'success')
            return redirect(url_for('matches.match_page', match_id=match.id))
        else:
            flash('Something went wrong! Score could not be updated', 'danger')
            return redirect(url_for('matches.match_page', match_id=match.id))
    else:
        flash('Something went wrong! Score could not be updated', 'danger')
        return redirect(url_for('matches.match_page', match_id=match.id))


# once scores have been confirmed for a match, following function will
# pass the data from the match table to the team table (for points, games won etc)
def update_points(match_id):
    match = Match.query.get(match_id)
    # function only runs if both home and away scores have been confirmed
    if match.home_approved and match.away_approved:
        home = Team.query.filter_by(name=match.home_team).first()
        away = Team.query.filter_by(name=match.away_team).first()
        home.points += match.home_score
        away.points += match.away_score
        if match.home_score > match.away_score:
            home.matches_won += 1
            away.matches_lose += 1
        elif match.home_score == match.away_score:
            home.matches_drawn += 1
            away.matches_drawn += 1
            db.session.commit()
        else:
            home.matches_lose += 1
            away.matches_won += 1
        db.session.commit()


@matches.route('/match/delete/<int:match_id>', methods=['POST'])
@login_required
def delete_match(match_id):
    # deleting matches is restricted to league admins and reps
    if current_user.admin_level not in ['Admin', 'Rep']:
        flash("You don't have permission to do this!")
        return redirect(url_for('matches.match_page',
                match_id=match_id))
    match = Match.query.get(match_id)
    if match:
        db.session.delete(match)
        db.session.commit()
        flash('Match deleted!', 'success')
        return redirect(url_for('main.home'))
    else:
        flash('Unable to delete match', 'info')
        return redirect(url_for('main.home'))


@matches.route('/match/update/<int:match_id>', methods=['GET', 'POST'])
@login_required
def update_match(match_id):
    form = UpdateMatch()
    # generate form list options as team names stored in db
    form.home_team.choices = [(a.name, a.name) for a in Team.query.order_by(Team.name)]
    form.away_team.choices = [(a.name, a.name) for a in Team.query.order_by(Team.name)]
    # updating matches is restricted to league admins and reps
    if current_user.admin_level in ['Admin', 'Rep']:
        match = Match.query.get(match_id)
        if form.validate_on_submit():
            match.home_team = form.home_team.data
            match.away_team = form.away_team.data
            match.location = form.location.data
            match.date = form.date.data
            match.time = form.time.data
            db.session.commit()
            flash("Match updated!", 'success')
            return redirect(url_for('matches.match_page', match_id=match.id))
        elif request.method == 'GET':
            form.home_team.data = match.home_team
            form.away_team.data = match.away_team
            form.location.data = match.location
            form.date.data = match.date
            form.time.data = match.time
    else:
        flash("You don't have permission to view this page!", 'danger')
        return redirect(url_for('matches.match_page',
                match_id=match_id))
    return render_template('update_match.html', title="Update Match",
                form=form)
