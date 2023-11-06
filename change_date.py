from app import app, db, Habit
from datetime import datetime, timedelta

def set_back_last_checked_in():
    with app.app_context():
        # Get all habits from the database
        habits = Habit.query.all()

        # Set back the last_checked_in date to yesterday for all habits
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        for habit in habits:
            habit.last_checked_in = yesterday

        # Commit the changes to the database
        db.session.commit()

# Call the function
set_back_last_checked_in()
