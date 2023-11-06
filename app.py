from flask import Flask, render_template, redirect, url_for, request
from flask import flash, get_flashed_messages, jsonify
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
    today_date = datetime.now().strftime("%Y-%m-%d")
    habits = Habit.query.all()
    print("Habits:", habits)  # This will print to your console where you run the Flask app
    already_checked_in = any(habit.last_checked_in and habit.last_checked_in.strftime("%Y-%m-%d") == today_date for habit in habits)
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


@app.route('/check-in', methods=['POST'])
def check_in():
    today = datetime.utcnow().date()
    if request.method == 'POST':
        checked_habits = request.form.getlist('habit_check')
        all_habits = Habit.query.all()

        for habit in all_habits:
            # Update last_checked_in date for each habit
            habit.last_checked_in = today

            # If the habit was checked today
            if str(habit.id) in checked_habits:
                if habit.streak >= 0:
                    habit.streak += 1
                else:
                    habit.streak = 1  # Reset streak to 1 if it was negative
                habit.current_score += 1  # Increase score
            else:
                if habit.streak > 0:
                    habit.streak = -1  # If streak was positive, set to -1
                else:
                    habit.streak -= 1  # Decrease negative streak
                
                # Score decrease logic based on the negative streak
                # Since we know the user checks in every day, the streak will always be the number of consecutive missed days
                if habit.streak < 0:
                    decrease_amount = 2 ** abs(habit.streak + 1)  # 2 to the power of the number of days missed
                else:
                    decrease_amount = 1  # If it's the first miss, decrease by 1
                
                habit.current_score = max(0, habit.current_score - decrease_amount)  # Ensure score doesn't go below 0

        db.session.commit()

    return redirect(url_for('index'))




def initialize_database():
    with app.app_context():
        db.create_all()
        # # Data to initialize database with
        # initial_habits = [
        #     {'name': 'Drink Water', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0},
        #     {'name': 'Exercise', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0},
        #     {'name': 'Read Book', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0}
        # ]

        # for init_habit in initial_habits:
        #     habit = Habit(
        #         name=init_habit['name'],
        #         current_status=init_habit['current_status'],
        #         current_score=init_habit['current_score'],
        #         streak=init_habit['streak']
        #     )
        #     db.session.add(habit)

        db.session.commit()


if __name__ == '__main__':
    if not os.path.exists(r'instance\habits.db'):
        initialize_database()   
    app.run(debug=True)
