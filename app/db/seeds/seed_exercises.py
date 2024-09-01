from app.db import connection

exercises = [
    {"name": "Push Up", "description": "A basic push-up.", "category": "strength"},
    {"name": "Squat", "description": "A basic squat.", "category": "strength"},
    {"name": "Running", "description": "A basic running exercise.", "category": "cardio"},
    {"name": "Plank", "description": "A basic plank.", "category": "flexibility"},
    {"name": "Deadlift", "description": "A strength exercise targeting the lower back, hamstrings, and glutes.",
     "category": "strength"},
    {"name": "Bench Press", "description": "A compound exercise that targets the chest, shoulders, and triceps.",
     "category": "strength"},
    {"name": "Burpee", "description": "A full-body exercise combining a squat, push-up, and jump.",
     "category": "cardio"},
    {"name": "Lunge", "description": "A lower body exercise focusing on the quadriceps, hamstrings, and glutes.",
     "category": "strength"},
    {"name": "Bicep Curl", "description": "An isolation exercise targeting the biceps.", "category": "strength"},
    {"name": "Mountain Climbers", "description": "A cardio exercise that also engages the core and lower body.",
     "category": "cardio"},
    {"name": "Russian Twist", "description": "A core exercise focusing on the obliques.", "category": "flexibility"},
    {"name": "Leg Raise", "description": "An abdominal exercise that targets the lower abs.",
     "category": "flexibility"},
    {"name": "Pull Up", "description": "A compound exercise targeting the back, shoulders, and biceps.",
     "category": "strength"},
    {"name": "Tricep Dip", "description": "An exercise that focuses on the triceps using body weight.",
     "category": "strength"},
    {"name": "Jump Rope",
     "description": "A cardio exercise involving jumping over a rope swung under the feet and over the head.",
     "category": "cardio"},
    {"name": "Shoulder Press", "description": "A strength exercise targeting the shoulders and triceps.",
     "category": "strength"},
]

num_exercises = len(exercises)


def insert_exercise(conn, cursor, exercise):
    insert_query = """
        INSERT INTO exercises (name, description, category)
        VALUES (%s, %s, %s)
        RETURNING exercise_id;
    """

    cursor.execute(insert_query, (exercise['name'], exercise['description'], exercise['category']))
    exercise_id = cursor.fetchone()
    conn.commit()
    print(f"Exercise inserted with ID: {exercise_id}")
    return exercise_id


def seed_exercise_data():
    conn, cursor = connection.get_db()
    for exercise in exercises:
        try:
            insert_exercise(conn=conn, cursor=cursor, exercise=exercise)
        except Exception as error:
            print(f"Error inserting exercise {exercise['name']}: {error}")
    conn.close()
    cursor.close()


if __name__ == '__main__':
    print('Starting...')
    seed_exercise_data()
    print('...Ending')
