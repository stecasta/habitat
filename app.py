from flask import Flask, render_template, redirect, url_for, request
from flask import flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route('/set-back-last-checked-in', methods=['POST'])
def set_back_last_checked_in():
    try:
        set_back_date()
        # Removed flash messages to avoid requiring a secret key
        return redirect(url_for('index'))  # Assuming 'index' is your view function for the main page
    except Exception as e:
        # Removed flash messages to avoid requiring a secret key
        return redirect(url_for('index'))

def set_back_date():
    with app.app_context():
        # Get all habits from the database
        habits = Habit.query.all()

        # Set back the last_checked_in date to yesterday for all habits
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for habit in habits:
            habit.last_checked_in = yesterday

        # Commit the changes to the database
        db.session.commit()

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
        # Data to initialize database with
        initial_habits = [
            {'name': 'Drink Water', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0},
            {'name': 'Exercise', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0},
            {'name': 'Read Book', 'current_status': 'Check-in your first day to get going', 'current_score': 0, 'streak': 0}
        ]

        for init_habit in initial_habits:
            habit = Habit(
                name=init_habit['name'],
                current_status=init_habit['current_status'],
                current_score=init_habit['current_score'],
                streak=init_habit['streak']
            )
            db.session.add(habit)

        db.session.commit()


if __name__ == '__main__':
    if not os.path.exists(r'instance\habits.db'):
        initialize_database()   
    app.run(debug=True)
