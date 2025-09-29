-- Create database if it doesn't exist
SELECT 'CREATE DATABASE ticketing_system_dev' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ticketing_system_dev');

-- Connect to the database
\c ticketing_system_dev;

-- Create the complete schema
-- (This will be created by SQLAlchemy, but we can add any custom setup here)

-- Create indexes for better performance
-- (These will be created by our models, but good to have as backup)

-- Insert initial data if needed
-- (We can add some default categories here if needed)

-- Set up any database-level configurations
ALTER DATABASE ticketing_system_dev SET timezone TO 'UTC';