from database_connection import create_db_engine
from sqlalchemy import text

def get_all_events():
    engine = create_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM events;"))
        events = result.fetchall()
    
        print("Events In Your Database:")
        for event in events:
            print(f"- {event[1]} on {event[3]} at {event[4]} - ₦{event[5]}")

def create_test_user():
    engine = create_db_engine()
    with engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO users (name, email,password_hash)
            VALUES ('Test User', 'testuser@example.com', 'hashed_password123')
            ON CONFLICT (email) DO NOTHING;
        """))
        connection.commit()
        print("Test user created!")

def get_event_statistics():
    engine = create_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                COUNT(*) as total_events,
                AVG(price) as average_price,
                SUM(capacity) as total_capacity
            FROM events
        """))
        rows = result.fetchone()
        stats = rows if rows else (0, 0.0, 0)
        print(f"📊 Event Statistics:")
        print(f"   Total Events: {stats[0]}")
        print(f"   Average Price: ₦{stats[1]:.2f}")
        print(f"   Total Capacity: {stats[2]} people")

if __name__ == "__main__":
    print("🚀 Testing database operations...")
    create_test_user()
    get_all_events()
    get_event_statistics()