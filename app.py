from flask import Flask, render_template, redirect, url_for, request
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
    current_score = db.Column(db.String(50))
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

@app.route('/check-in', methods=['GET', 'POST'])
def check_in():
    today = datetime.utcnow().date()
    if request.method == 'POST':
        checked_habits = request.form.getlist('habit_check')
        for habit_id in checked_habits:
            habit = Habit.query.get(habit_id)
            if habit:
                # Ensure current_score is an integer
                habit.current_score = int(habit.current_score) if habit.current_score else 0
                habit.current_score += 1  # Increment the score by 1
                habit.last_checked_in = datetime.utcnow().date()
                db.session.commit()
        return redirect(url_for('index'))
    else:
        habits = Habit.query.all()
        # Check if any habit was checked in today
        already_checked_in = any(habit.last_checked_in == today for habit in habits)
        return render_template('check_in.html', habits=habits, already_checked_in=already_checked_in)

def initialize_database():
    with app.app_context():
        db.create_all()
        # Data to initialize database with
        initial_habits = [
            {'name': 'Drink Water', 'current_status': 'Pending', 'current_score': '0'},
            {'name': 'Exercise', 'current_status': 'Pending', 'current_score': '0'},
            {'name': 'Read Book', 'current_status': 'Pending', 'current_score': '0'}
        ]

        for init_habit in initial_habits:
            habit = Habit(
                name=init_habit['name'],
                current_status=init_habit['current_status'],
                current_score=init_habit['current_score']
            )
            db.session.add(habit)

        db.session.commit()

if __name__ == '__main__':
    if not os.path.exists(r'instance\habits.db'):
        initialize_database()   
    app.run(debug=True)
