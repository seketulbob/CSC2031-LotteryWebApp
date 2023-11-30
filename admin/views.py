# IMPORTS
import random
from flask import Blueprint, render_template, flash, redirect, url_for, request
from app import db
from models import User, Draw
from flask_login import login_required, current_user
from functools import wraps
import logging
from sqlalchemy.orm import make_transient

# CONFIG
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorized access attempt - User ID: %s, Username: %s, Role: %s, IP: %s',
                                current_user.id, current_user.email, current_user.role, request.remote_addr)
                return render_template('error/403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper


# VIEWS
# view admin homepage
@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    return render_template('admin/admin.html', name=current_user.firstname)


# create a new winning draw
@admin_blueprint.route('/generate_winning_draw')
@login_required
@requires_roles('admin')
def generate_winning_draw():

    # get current winning draw
    current_winning_draw = Draw.query.filter_by(master_draw=True).first()
    lottery_round = 1

    # if a current winning draw exists
    if current_winning_draw:
        # update lottery round by 1
        lottery_round = current_winning_draw.lottery_round + 1

        # delete current winning draw
        db.session.delete(current_winning_draw)
        db.session.commit()

    # get new winning numbers for draw
    winning_numbers = random.sample(range(1, 60), 6)
    winning_numbers.sort()
    winning_numbers_string = ''
    for i in range(6):
        winning_numbers_string += str(winning_numbers[i]) + ' '
    winning_numbers_string = winning_numbers_string[:-1]

    admin_user = User.query.filter_by(role='admin').first()

    if admin_user:
        # create a new draw object.
        new_winning_draw = Draw(user_id=admin_user.id, numbers=winning_numbers_string, master_draw=True,
                                lottery_round=lottery_round, post_key=admin_user.post_key)

        # add the new winning draw to the database
        db.session.add(new_winning_draw)
        db.session.commit()

        flash("New winning draw %s added." % winning_numbers_string)
    else:
        flash("Admin user not found")

    # re-render admin page
    return redirect(url_for('admin.admin'))


# view current winning draw
@admin_blueprint.route('/view_winning_draw')
@login_required
@requires_roles('admin')
def view_winning_draw():
    admin_user = User.query.filter_by(role='admin').first()
    # get winning draw from DB
    current_winning_draw = Draw.query.filter_by(master_draw=True, been_played=False).first()

    if current_winning_draw:
        make_transient(current_winning_draw)
        current_winning_draw.view_draw(admin_user.post_key)
        decrypted_winning_draw = current_winning_draw

        # re-render admin page with current winning draw and lottery round
        return render_template('admin/admin.html', winning_draw=decrypted_winning_draw, name=current_user.firstname)

    # if no winning draw exists, rerender admin page
    flash("No valid winning draw exists. Please add new winning draw.")
    return redirect(url_for('admin.admin'))


# view lottery results and winners
@admin_blueprint.route('/run_lottery')
@login_required
@requires_roles('admin')
def run_lottery():

    # get current unplayed winning draw
    current_winning_draw = Draw.query.filter_by(master_draw=True, been_played=False).first()

    # if current unplayed winning draw exists
    if current_winning_draw:

        # get all unplayed user draws
        user_draws = Draw.query.filter_by(master_draw=False, been_played=False).all()
        results = []

        # if at least one unplayed user draw exists
        if user_draws:

            # update current winning draw as played
            current_winning_draw.been_played = True
            db.session.add(current_winning_draw)
            db.session.commit()

            # for each unplayed user draw
            for draw in user_draws:

                # get the owning user (instance/object)
                user = User.query.filter_by(id=draw.user_id).first()

                # decrypt draw numbers
                decrypted_winning_numbers = current_winning_draw.decrypt_numbers(current_user.post_key)
                decrypted_user_numbers = draw.decrypt_numbers(user.post_key)

                # if user draw matches current unplayed winning draw
                if decrypted_user_numbers == decrypted_winning_numbers:

                    # add details of winner to list of results
                    results.append((current_winning_draw.lottery_round, decrypted_user_numbers, draw.user_id, user.email))

                    # update draw as a winning draw (this will be used to highlight winning draws in the user's
                    # lottery page)
                    draw.matches_master = True

                # update draw as played
                draw.been_played = True

                # update draw with current lottery round
                draw.lottery_round = current_winning_draw.lottery_round

                # store decrypted numbers in decrypted_numbers column in database
                draw.decrypted_numbers = decrypted_user_numbers
                current_winning_draw.decrypted_numbers = decrypted_winning_numbers

                # commit draw changes to DB
                db.session.add(draw)
                db.session.commit()

            # if no winners
            if len(results) == 0:
                flash("No winners.")

            return render_template('admin/admin.html', results=results, name="PLACEHOLDER FOR FIRSTNAME")

        flash("No user draws entered.")
        return admin()

    # if current unplayed winning draw does not exist
    flash("Current winning draw expired. Add new winning draw for next round.")
    return redirect(url_for('admin.admin'))


# view all registered users
@admin_blueprint.route('/view_all_users')
@login_required
@requires_roles('admin')
def view_all_users():
    current_users = User.query.filter_by(role='user').all()

    return render_template('admin/admin.html', name=current_user.firstname, current_users=current_users)


# view last 10 log entries
@admin_blueprint.route('/logs')
@login_required
@requires_roles('admin')
def logs():
    with open("lottery.log", "r") as f:
        content = f.read().splitlines()[-10:]
        content.reverse()

    return render_template('admin/admin.html', logs=content, name=current_user.firstname)

# view user activity logs
@admin_blueprint.route('/view_user_activity')
@login_required
@requires_roles('admin')
def view_user_activity():
    user_activity_logs = User.query.filter_by(role='user').all()

    return render_template('admin/admin.html', name=current_user.firstname, user_activity_logs=user_activity_logs)