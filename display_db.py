from app import app, db, Habit

def display_habits(app):
    with app.app_context():
        habits = Habit.query.all()
        for habit in habits:
            print(habit)

if __name__ == '__main__':
    display_habits(app)