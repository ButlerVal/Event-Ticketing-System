from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)

# Complete schema for event ticketing system
schema_sql = """
-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS events CASCADE; 
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users table (enhanced)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Events table (enhanced)
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    location VARCHAR(255) NOT NULL,
    address TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    tickets_sold INTEGER DEFAULT 0 CHECK (tickets_sold >= 0),
    category_id INTEGER REFERENCES categories(id),
    organizer_id INTEGER REFERENCES users(id),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure end_date is after start_date
    CONSTRAINT valid_event_dates CHECK (end_date IS NULL OR end_date > event_date),
    -- Ensure we don't oversell
    CONSTRAINT valid_ticket_count CHECK (tickets_sold <= capacity)
);

-- Tickets table (enhanced)
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    ticket_code VARCHAR(50) UNIQUE NOT NULL,
    qr_code_data TEXT,
    qr_code_path VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'used', 'cancelled', 'expired')),
    purchase_date TIMESTAMP DEFAULT NOW(),
    amount_paid DECIMAL(10,2) NOT NULL CHECK (amount_paid >= 0),
    seat_number VARCHAR(20),
    special_instructions TEXT,
    
    -- Unique constraint to prevent duplicate tickets
    UNIQUE(user_id, event_id, seat_number)
);

-- Payments table (Paystack ready)
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    event_id INTEGER NOT NULL REFERENCES events(id), 
    ticket_id INTEGER REFERENCES tickets(id),
    paystack_reference VARCHAR(100) UNIQUE NOT NULL,
    paystack_access_code VARCHAR(100),
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'NGN',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'cancelled', 'abandoned')),
    payment_method VARCHAR(50),
    gateway_response TEXT,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_category ON events(category_id);
CREATE INDEX idx_tickets_user ON tickets(user_id);
CREATE INDEX idx_tickets_event ON tickets(event_id);
CREATE INDEX idx_payments_reference ON payments(paystack_reference);
CREATE INDEX idx_payments_status ON payments(status);

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Technology', 'Tech conferences, workshops, and meetups'),
('Music', 'Concerts, festivals, and live performances'), 
('Business', 'Networking events, conferences, and seminars'),
('Sports', 'Sporting events, matches, and tournaments'),
('Education', 'Educational workshops, training, and courses'),
('Entertainment', 'Comedy shows, theater, and entertainment events'),
('Food & Drink', 'Food festivals, wine tastings, and culinary events'),
('Health & Wellness', 'Fitness events, wellness workshops, and health seminars');

-- Insert sample events
INSERT INTO events (title, description, event_date, end_date, location, address, price, capacity, category_id) VALUES
('Lagos Tech Summit 2024', 'The biggest technology conference in West Africa featuring industry leaders and innovative startups.', 
 '2024-12-28 09:00:00', '2024-12-28 18:00:00', 'Eko Convention Centre', 'Victoria Island, Lagos', 25000.00, 1000, 1),

('Afrobeats Festival Lagos', 'Experience the best of Afrobeats music with top artists from across Africa.',
 '2024-12-30 19:00:00', '2024-12-31 02:00:00', 'Tafawa Balewa Square', 'Lagos Island, Lagos', 15000.00, 5000, 2),

('Startup Pitch Competition', 'Young entrepreneurs pitch their innovative ideas to investors and industry experts.',
 '2025-01-10 14:00:00', '2025-01-10 18:00:00', 'University of Lagos', 'Akoka, Lagos', 5000.00, 300, 3),

('Lagos Marathon 2025', 'Join thousands of runners in the biggest marathon event in West Africa.',
 '2025-02-15 06:00:00', '2025-02-15 12:00:00', 'National Stadium', 'Surulere, Lagos', 10000.00, 20000, 4),

('Digital Marketing Masterclass', 'Learn advanced digital marketing strategies from industry experts.',
 '2025-01-20 10:00:00', '2025-01-20 16:00:00', 'Sheraton Hotel', 'Ikeja, Lagos', 12000.00, 200, 5);
"""

print("Creating complete database schema...")
with engine.connect() as connection:
    connection.execute(text(schema_sql))
    connection.commit()
    print("✅ Database schema created successfully!")

# Verify the setup
verify_sql = """
SELECT 
    (SELECT COUNT(*) FROM categories) as categories_count,
    (SELECT COUNT(*) FROM events) as events_count,
    (SELECT COUNT(*) FROM users) as users_count;
"""

with engine.connect() as connection:
    result = connection.execute(text(verify_sql))
    count = result.fetchone()
    counts = count if count else (0, 0, 0)
    print(f"📊 Database populated:")
    print(f"   Categories: {counts[0]}")
    print(f"   Events: {counts[1]}") 
    print(f"   Users: {counts[2]}")