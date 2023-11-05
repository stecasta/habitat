from app import app, db, Habit

def create_database(app):
    with app.app_context():
        # Create the database and the database table
        db.create_all()

        # Initialize database with data if empty
        if Habit.query.count() == 0:
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
    create_database(app)
