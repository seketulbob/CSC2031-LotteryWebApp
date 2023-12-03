# IMPORTS
import cryptography.fernet
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from lottery.forms import DrawForm
from models import Draw, User
from flask_login import login_user, logout_user, login_required, current_user
from admin.views import requires_roles
from sqlalchemy.orm import make_transient
from cryptography.fernet import Fernet, InvalidToken

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    return render_template('lottery/lottery.html', name=current_user.firstname)


@lottery_blueprint.route('/create_draw', methods=['POST'])
@login_required
@requires_roles('user')
def create_draw():
    form = DrawForm()

    if form.validate_on_submit():
        numbers = [
            form.number1.data, form.number2.data, form.number3.data,
            form.number4.data, form.number5.data, form.number6.data
        ]

        # Check for unique numbers
        if len(set(numbers)) != 6:
            flash('Numbers must be unique.')
            return redirect(url_for('lottery.lottery'))

        # Validate the form to contain exactly 6 numbers and the numbers between 1 and 60
        if len(numbers) != 6 or any(num is None or not 1 <= num <= 60 for num in numbers):
            flash('Draw must contain exactly 6 numbers between 1 and 60.')
            return redirect(url_for('lottery.lottery'))

        submitted_numbers = ' '.join(map(str, numbers))

        # create a new draw with the form data.
        new_draw = Draw(
            user_id=current_user.id, numbers=submitted_numbers,
            master_draw=False, lottery_round=0, post_key=current_user.post_key
        )

        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html', name=current_user.firstname, form=form)


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    user = User.query.filter_by(id=current_user.id).first()

    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(been_played=False).all()
    decrypted_draws = []

    for draw in playable_draws:
        make_transient(draw)

        try:
            draw.view_draw(user.post_key)
            decrypted_draws.append(draw)
        except cryptography.fernet.InvalidToken:
            pass

    # if playable draws exist
    if len(playable_draws) != 0:
        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=decrypted_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(been_played=True).all()
    user = User.query.filter_by(id=current_user.id).first()
    decrypted_draws = []

    for draw in played_draws:
        make_transient(draw)

        try:
            draw.view_draw(user.post_key)
            decrypted_draws.append(draw)
        except cryptography.fernet.InvalidToken:
            pass

    # if played draws exist
    if len(played_draws) != 0:
        return render_template('lottery/lottery.html', results=decrypted_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    Draw.query.filter_by(been_played=True, master_draw=False).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


