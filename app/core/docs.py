get_exercises = """
## Retrieve All Exercises

Retrieves a list of all exercises, returning a JSON array with exercise details (`exercise_id`, `name`, `description`, `category`).

### Responses

- **Success**: Returns a `200 OK` status with the exercise data.
- **Error**: Returns `400 Bad Request` with an error message if the retrieval fails. 

"""

get_exercise_by_id = """
## Retrieve Exercise by ID

Retrieves a specific exercise by its ID. 

### Path Parameter:

- `exercise_id` (integer): The ID of the exercise you want to retrieve. Must be greater than zero but lower than 
the total number of exercises(typically 16).

### Responses

- **Success**: Returns `200 OK` with exercise details.
- **Error**: Returns `400 Bad Request` if the request fails or `404 Not Found` if the exercise ID does not exist.
"""

login = """
## User Login

Logs in a user using their credentials and returns a JWT token.

**Request Body:**
- `username` (string): The user's email.
- `password` (string): The user's password.

**Response:**
- **Success**: Returns `202 Accepted` with a JWT token.
- **Error**: Returns `404 Not Found` for invalid credentials or `400 Bad Request` for other errors.
"""


create_user = """
## Register New User

Creates a new user in the database.

**Request Body:**
- `email` (EmailStr): The user's email address.
- `first_name` (string): The user's first name.
- `last_name` (string): The user's last name.
- `password` (string): The user's password (will be hashed before storage).The password must be at least
 8 characters long,have at least 1 **special character**,1 **uppercase character**, 
 1 **digit** and one **lowercase character**

**Response:**
- **Success**: Returns `201 Created` with the created user's details.
- **Error**: Returns `400 Bad Request` if the email is already in use or if another error occurs.
"""

create_workout_plan = """
## Create Workout Plan

Creates a new workout plan for the logged-in user.

**Request Body:**
- `plan_name` (string): The name of the workout plan.
- `description` (string, optional): A brief description of the workout plan.
- `exercises` (list): A list of exercises with details:
  - `exercise_id` (integer): The ID of the exercise.
  - `sets` (integer): Number of sets.
  - `reps` (integer): Number of reps.
  - `weight` (float, optional): The weight to be used (kg). 
  - `comments` (string, optional): Any additional comments.

**Response:**
- **Success**: Returns `201 Created` with the workout plan details, including the exercises.
- **Error**: Returns `400 Bad Request` if there's an error during creation, such as a non-existent exercise ID.
"""

delete_workout_plan = """
## Delete Workout Plan

Deletes a workout plan belonging to the logged-in user.

**Path Parameter:**
- `plan_id` (UUID4): The ID of the workout plan to be deleted.

**Response:**
- **Success**: Returns `200 OK` with a confirmation message.
- **Error**: Returns `404 Not Found` if the plan is not found or the user doesn't have permission to delete it. Returns `400 Bad Request` if there's an error during deletion.
"""

update_workout_plan = """
## Update Workout Plan

Updates an existing workout plan for the logged-in user.

**Path Parameter:**
- `plan_id` (UUID4): The ID of the workout plan to be updated.

**Request Body:**
- `plan_name` (string): The new name of the workout plan.
- `description` (string, optional): The new description of the workout plan.
- `exercises` (list): A list of exercises with details:
  - `exercise_id` (integer): The ID of the exercise.
  - `sets` (integer): Number of sets.
  - `reps` (integer): Number of reps.
  - `weight` (float, optional): The weight to be used (kg).
  - `comments` (string, optional): Any additional comments.

**Response:**
- **Success**: Returns `200 OK` with the updated workout plan details, including the exercises.
- **Error**: Returns `404 Not Found` if the plan is not found or not owned by the user. Returns `400 Bad Request` if there's an error during the update, such as a non-existent exercise ID.
"""

list_workout_plans = """
## List All Workout Plans

Retrieves a list of all workout plans created by the current user.

**Query Parameters:**
- `limit` (integer, optional): The maximum number of workout plans to return. Default is 10.
- `skip` (integer, optional): The number of workout plans to skip before starting to return results. Default is 0.

**Response:**
- **Success**: Returns `200 OK` with a list of workout plans, including their exercises and metadata (e.g., exercise count).
- **Error**: Returns `404 Not Found` if no workout plans are found for the user. Returns `400 Bad Request` if there's an error during the retrieval process.
"""

get_workout_plan = """
## Retrieve Specific Workout Plan

Fetches details of a specific workout plan for the current user by `plan_id`.

**Path Parameter:**
- `plan_id` (UUID4): The ID of the workout plan to retrieve.

**Response:**
- **Success**: Returns `200 OK` with the workout plan details, including exercises and metadata.
- **Error**: Returns `404 Not Found` if the workout plan is not found or does not belong to the user. Returns `400 Bad Request` for any other errors.
"""

create_workout_schedule = """
## Create Workout Schedule

Creates a new workout schedule for the logged-in user.

**Request Body:**
- `plan_id` (UUID4): The ID of the workout plan the schedule is based on.
- `schedule_date` (datetime.date): The date the workout is meant to be done
- `schedule_time` (datetime.time): The time the workout is meant to be done
- `status` (StatusEnum): A custom field, only values allowed are pending, missed and completed



**Response:**
- **Success**: Returns `201 Created` with the workout schedule details, including additional data.
- **Error**: Returns `400 Bad Request` if there's an error during creation. Returns `404 Not Found` if the workout plan is not found 
"""

get_workout_schedule = """
## Retrieve Specific Workout Schedule

Fetches details of a specific workout plan for the current user by `scheduled_workout_id.

**Path Parameter:**
- `scheduled_workout_id` (UUID4): The ID of the workout schedule to retrieve.

**Response:**
- **Success**: Returns `200 OK` with the workout plan details, including exercises and metadata.
- **Error**: Returns `404 Not Found` if the workout plan is not found or does not belong to the user. Returns `400 Bad Request` for any other errors.
"""

list_workout_schedules = """
## List All Workout Schedules

Retrieves a list of all workout schedules created by the current user.

**Query Parameters:**
- `limit` (integer, optional): The maximum number of workout plans to return. Default is 10.
- `skip` (integer, optional): The number of workout plans to skip before starting to return results. Default is 0.
- `workout_status` (StatusChoice): A custom field, only values allowed are pending, missed, completed and all

**Response:**
- **Success**: Returns `200 OK` with a list of workout schedules, including their exercises.
- **Error**: Returns `404 Not Found` if no workout schedules are found for the user. Returns `400 Bad Request` if there's an error during the retrieval process.
"""

update_workout_schedule = """
## Update Workout Schedule

Updates a workout schedule for the logged-in user. All fields are optional.

**Path Parameter:**
- `scheduled_workout_id` (UUID4): The ID of the workout schedule to update.

**Request Body:**
- `plan_id` (UUID4, optional): The ID of the workout plan the schedule is based on.
- `schedule_date` (datetime.date,optional): The date the workout is meant to be done
- `schedule_time` (datetime.time,optional): The time the workout is meant to be done
- `status` (StatusEnum,optional): A custom field, only values allowed are pending, missed and completed



**Response:**
- **Success**: Returns `200 Ok` with the workout schedule details, including additional data.
- **Error**: Returns `400 Bad Request` if there's an error during creation. Returns `404 Not Found` if the workout plan is not found 
"""
delete_workout_schedule = """
## Delete Workout Schedule

Deletes a workout schedule belonging to the logged-in user.

**Path Parameter:**
- `schedule_workout_id` (UUID4): The ID of the workout schedule to be deleted.

**Response:**
- **Success**: Returns `200 OK` with a confirmation message.
- **Error**: Returns `404 Not Found` if the schedule is not found or the user doesn't have permission to delete it. 
Returns `400 Bad Request` if there's an error during deletion.
"""
create_workout_log = """
## Create Workout Log

Creates a new workout og for the logged-in user.

**Request Body:**
- `completed_at` (datetime.datetime): The date and time the workout was completed.
- `total_time` (int): The total time in minutes it took to complete the workout
- `notes` (string): Any notes the user wants to keep relating to the workout
- `scheduled_workout_id` (UUID4): The ID of the scheduled workout that's being logged



**Response:**
- **Success**: Returns `201 Created` with the workout log details.
- **Error**: Returns `400 Bad Request` if there's an error during creation. Returns `404 Not Found` 
if the workout schedule is not found 
"""


get_workout_log = """
## Retrieve Specific Workout Log

Fetches details of a specific workout log for the current user by `log_id.

**Path Parameter:**
- `log_id` (UUID4): The ID of the workout Log to retrieve.

**Response:**
- **Success**: Returns `200 OK` with the workout log details.
- **Error**: Returns `404 Not Found` if the workout log is not found or does not belong to the user. Returns `400 Bad Request` for any other errors.
"""

list_workout_logs = """
## List All Workout Logs

Retrieves a list of all workout logs created by the current user.

**Query Parameters:**
- `limit` (integer, optional): The maximum number of workout logs to return. Default is 10.
- `skip` (integer, optional): The number of workout logs to skip before starting to return results. Default is 0.

**Response:**
- **Success**: Returns `200 OK` with a list of workout logs.
- **Error**: Returns `404 Not Found` if no workout logs are found for the user. Returns `400 Bad Request` if there's an error during the retrieval process.
"""
