CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    user_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL  -- e.g., cardio, strength, flexibility
);
--The workout_plans table defines individual workout plans, while the workout_plan_exercises table
--links these plans to specific exercises, detailing the exercises included in each plan.

CREATE TABLE workout_plans (
    plan_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);


CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';


CREATE TRIGGER set_timestamp
BEFORE UPDATE ON workout_plans
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


CREATE TABLE workout_plan_exercises (
    plan_exercise_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    plan_id UUID NOT NULL,
    exercise_id INT NOT NULL,
    sets INT NOT NULL,
    reps INT NOT NULL,
    weight DECIMAL(10, 2),
    comments TEXT,
    FOREIGN KEY (plan_id) REFERENCES workout_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
);


CREATE TABLE scheduled_workouts (
    scheduled_workout_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    plan_id UUID NOT NULL,
    user_id UUID NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (plan_id) REFERENCES workout_plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE workout_logs (
    log_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    scheduled_workout_id UUID REFERENCES scheduled_workouts(scheduled_workout_id) ON DELETE SET NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_time INT,
    notes TEXT
);