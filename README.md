# Workout Tracker API

This API, built using FastAPI, allows users to manage their workouts,
exercises, and track their progress effectively. 
It is inspired by the [Fitness Workout Tracker project](https://roadmap.sh/projects/fitness-workout-tracker) from the Developer Roadmap.

## Table of Contents

- [Installation](#installation)
- [Database Setup](#database-setup)
- [Usage](#usage)
  - [Users](#users)
  - [Exercises](#exercises)
  - [Workout Management](#workout-management)
  - [Scheduled Workout Management](#scheduled-workout-management)
  - [Workout Logs](#workout-logs)
  - [Reports](#reports)
- [Inspiration](#inspiration)


## Installation

To run this project locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/Oluwatooki/Workout-Tracker.git
   cd Workout-Tracker
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Copy the `.env.example` file to a new `.env` file:

     ```bash
     cp .env.example .env
     ```

   - Edit the `.env` file to include your specific configuration (e.g., database port, JWT secret, etc.).

5. Ensure the content root is set correctly:

   - The content root should be the root directory of the cloned Git repository. This means that when you run the FastAPI application, the working directory should be the root of the project where the `main.py` file and the `app` directory are located. This setup is essential for relative paths and module imports to work correctly.
6. Run the application:

   Simply execute the `run.py` file:

   ```bash
   python run.py
   ```
   The application will start, and you can access the API documentation at `http://127.0.0.1:8000/docs`.

## Database Setup

1. Make sure you have PostgreSQL installed and running.

2. Create a new database for the application.

3. Run the `create_schema.sql` script to set up the necessary tables:


## Usage

### Users

- **POST** `/register`  
  Register a new user.

- **POST** `/login`  
  Log in a user and return a JWT.

- **GET** `/me`  
  Checks the logged-in user's details.

### Exercises

- **GET** `/exercises`  
  Retrieves all exercises.

- **GET** `/exercises/{exercise_id}`  
  Retrieves a particular exercise.

### Workout Management

- **POST** `/workout-plans`  
  Create a new workout plan.

- **GET** `/workout-plans`  
  List all workout plans for the current user.

- **PUT** `/workout-plans/{plan_id}`  
  Update a workout plan.

- **GET** `/workout-plans/{plan_id}`  
  List a specific workout plan for the current user.

- **DELETE** `/workout-plans/{plan_id}`  
  Delete a workout plan.

### Scheduled Workout Management

- **POST** `/scheduled-workouts`  
  Schedule a workout.

- **GET** `/scheduled-workouts`  
  List all scheduled workouts for the authenticated user.

- **GET** `/scheduled-workouts/{scheduled_workout_id}`  
  Get a scheduled workout.

- **PATCH** `/scheduled-workouts/{scheduled_workout_id}`  
  Update a scheduled workout.

- **DELETE** `/scheduled-workouts/{scheduled_workout_id}`  
  Cancel a scheduled workout.

### Workout Logs

- **POST** `/workout-logs`  
  Log a workout.

- **GET** `/workout-logs`  
  List all workout logs for the current user.

- **GET** `/workout-logs/{log_id}`  
  List a specific workout log for the current user.

### Reports

- **GET** `/reports/progress`  
  Generate reports on past workouts and progress.

## Inspiration

This project is inspired by the [Fitness Workout Tracker project](https://roadmap.sh/projects/fitness-workout-tracker) from the Developer Roadmap.

