workout_examples = {
    "normal": {
        "summary": "A normal Example",
        "description": "An example that has all appropriate fields filled, both optional and required",
        "value": {
            "plan_name": "Full Body Workout",
            "description": "This Workout focuses on your entire body",
            "exercises": [
                {
                    "exercise_id": 4,
                    "sets": 10,
                    "reps": 6,
                    "weight": 20,
                    "comments": "This may be strenuous",
                }
            ],
        },
    },
    "Only necessary fields filled": {
        "summary": "An example that meets the minimum requirements",
        "description": "An example that has only the minimum requirements to be accepted",
        "value": {
            "plan_name": "Full Body Workout",
            "exercises": [
                {
                    "exercise_id": 4,
                    "sets": 10,
                    "reps": 6,
                }
            ],
        },
    },
}

register_examples = {
    "normal": {
        "summary": "A normal Example",
        "description": "An example that has all appropriate fields filled with no errors",
        "value": {
            "email": "mike@example.com",
            "first_name": "Mike",
            "last_name": "Ekim",
            "password": "1%0TmlkiA220",
        },
    },
    "Invalid Password": {
        "summary": "Invalid Password returns a 422 error",
        "description": "The password must be at least 8 characters long, have at least 1 **special "
        "character**,1 **uppercase character**, 1 **digit** and one **lowercase character**",
        "value": {
            "email": "mike@example.com",
            "first_name": "Mike",
            "last_name": "Ekim",
            "password": "ABC123",
        },
    },
    "Invalid Email": {
        "summary": "Invalid email returns a 422 error",
        "description": "The email provided must be valid or else it will return an error",
        "value": {
            "email": "mike@example",
            "first_name": "Mike",
            "last_name": "Ekim",
            "password": "1%0TmlkiA220",
        },
    },
}


workout_schedule_examples = {
    "normal": {
        "summary": "A normal Example",
        "description": "An example that has all appropriate fields filled with no errors. "
        "Status can be any of `[pending,completed,missed]` ",
        "value": {
            "plan_id": "3db10787-b883-4429-98fe-46fd66ed1a5c",
            "scheduled_date": "2024-09-02",
            "scheduled_time": "21:43:19.716Z",
            "status": "pending",
        },
    },
}

workout_log_examples = {
    "normal": {
        "summary": "A normal Example",
        "description": "An example that has all appropriate fields filled with no errors. ",
        "value": {
            "completed_at": "2024-09-03T09:19:16.386Z",
            "total_time": 22,
            "notes": "It was a long and hard workout.",
            "scheduled_workout_id": "438b9097-4edf-4766-8d99-82992a86ce18",
        },
    },
}
