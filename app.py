from flask import Flask, render_template, redirect, url_for, request
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fdrebee'
db = SQLAlchemy(app)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    current_status = db.Column(db.String(50))
    current_score = db.Column(db.Integer, default=0)  # Now an integer
    streak = db.Column(db.Integer, default=0)  # Added as an integer with a default value of 0
    last_checked_in = db.Column(db.Date)

    def __repr__(self):
        return f"<Habit {self.name}>"

@app.route('/')
def index():
    today_date = datetime.utcnow().date()
    habits = Habit.query.all()
    print("Habits:", habits)  # This will print to your console where you run the Flask app
    already_checked_in = all(habit.last_checked_in and habit.last_checked_in == today_date for habit in habits)
    return render_template('index.html', habits=habits, today_date=today_date, already_checked_in=already_checked_in)

@app.route('/add-initial-habits', methods=['POST'])
def add_initial_habits():
    habit_names = request.form.getlist('habit_names')  # This gets a list of all habit names
    for name in habit_names:
        if name:  # Make sure it's not an empty string
            new_habit = Habit(name=name, current_status="Not started", current_score=0, streak=0)
            db.session.add(new_habit)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/set-back-last-checked-in', methods=['POST'])
def set_back_last_checked_in():
    try:
        db.session.rollback()  # Ensure the session is clean
        set_back_date()
        print('Dates set back successfully.')  # Print to console for debugging
    except Exception as e:
        print(f'An error occurred: {e}')  # Print the actual error to the console
    return redirect(url_for('index'))

def set_back_date():
    # Get all habits from the database
    habits = Habit.query.all()
    # Set back the last_checked_in date to yesterday for all habits
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    for habit in habits:
        habit.last_checked_in = yesterday
        print(f'Updating habit {habit.id} last checked-in date to {yesterday}')  # Print each update for debugging

    # Commit the changes to the database
    db.session.commit()

@app.route('/delete-all', methods=['POST'])
def delete_all():
    try:
        # This deletes all entries from the Habit table
        db.session.query(Habit).delete()
        # Commit the changes to the database
        db.session.commit()
        # Flash a success message
        flash('All entries have been deleted.')
    except Exception as e:
        # If something goes wrong, rollback the session
        db.session.rollback()
        # Flash an error message
        flash('An error occurred while trying to delete entries.')
        # Print the exception for debugging purposes
        print(e)  # Replace with proper logging in production
    # Redirect back to the index page
    return redirect(url_for('index'))

@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
def delete_habit(habit_id):
    habit_to_delete = Habit.query.get_or_404(habit_id)
    db.session.delete(habit_to_delete)
    db.session.commit()
    flash('Habit deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/rename_habit/<int:habit_id>', methods=['POST'])
def rename_habit(habit_id):
    habit_to_rename = Habit.query.get_or_404(habit_id)
    habit_to_rename.name = request.form['habit_name']
    db.session.commit()
    flash('Habit renamed successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_habit', methods=['POST'])
def add_habit():
    new_habit_name = request.form['new_habit_name']
    if new_habit_name:
        new_habit = Habit(name=new_habit_name, current_status="Not started", current_score=0, streak=0)
        db.session.add(new_habit)
        db.session.commit()
        flash('New habit added successfully!', 'success')
    else:
        flash('Habit name cannot be empty.', 'error')
    return redirect(url_for('index'))

def update_habit_status(habit, completed):
    today = datetime.utcnow().date()
    habit.last_checked_in = today

    if completed:
        if habit.streak >= 0:
            habit.streak += 1
        else:
            habit.streak = 1
        habit.current_score += 1
    else:
        if habit.streak > 0:
            habit.streak = -1
        else:
            habit.streak -= 1
        decrease_amount = 2 ** abs(habit.streak + 1)
        habit.current_score = max(0, habit.current_score - decrease_amount)

    db.session.commit()

@app.route('/mark_habit/<int:habit_id>/<status>', methods=['POST'])
def mark_habit(habit_id, status):
    habit = Habit.query.get_or_404(habit_id)
    completed = status == 'done'
    update_habit_status(habit, completed)
    return redirect(url_for('index'))


@app.route('/check-in', methods=['POST'])
def check_in():
    checked_habits = request.form.getlist('habit_check')
    all_habits = Habit.query.all()

    for habit in all_habits:
        if str(habit.id) in checked_habits:
            update_habit_status(habit, True)
        else:
            update_habit_status(habit, False)

    return redirect(url_for('index'))


def initialize_database():
    with app.app_context():
        db.create_all()
        db.session.commit()


if __name__ == '__main__':
    if not os.path.exists(r'instance\habits.db'):
        initialize_database()   
    app.run(debug=True)
