import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stadium_ops.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def run_query(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid

def get_all(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_one(sql, params=()):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def initialize_database():
    print("Initializing database tables...")
    
    # Create Tables
    run_query("""
        CREATE TABLE IF NOT EXISTS crowd_zones (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            occupancy INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Normal'
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS concessions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            queue_time INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Open',
            inventory_status TEXT DEFAULT 'Good'
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            category TEXT DEFAULT 'Other',
            severity TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'Open',
            assigned_team TEXT DEFAULT 'Unassigned',
            ai_protocol TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    run_query("""
        CREATE TABLE IF NOT EXISTS sustainability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action_type TEXT NOT NULL,
            points INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed data if empty
    zone_count = get_one("SELECT COUNT(*) as count FROM crowd_zones")
    if zone_count["count"] == 0:
        print("Seeding crowd zones...")
        zones = [
            ("sec-a", "Sector A (West Stand)", 15000, 12400, "Normal"),
            ("sec-b", "Sector B (North Stand - Active Fans)", 12000, 11800, "Warning"),
            ("sec-c", "Sector C (East Stand)", 18000, 17200, "Normal"),
            ("sec-d", "Sector D (South Stand - Family Zone)", 10000, 8500, "Normal"),
            ("gate-1", "Gate 1 (Main Entrance)", 5000, 4200, "Warning"),
            ("gate-2", "Gate 2 (East Entrance)", 4000, 1200, "Normal"),
            ("gate-3", "Gate 3 (South Entrance)", 4000, 3900, "Congested"),
            ("gate-4", "Gate 4 (VIP & Accessibility)", 2000, 450, "Normal")
        ]
        for z in zones:
            run_query(
                "INSERT INTO crowd_zones (id, name, capacity, occupancy, status) VALUES (?, ?, ?, ?, ?)",
                z
            )

    concession_count = get_one("SELECT COUNT(*) as count FROM concessions")
    if concession_count["count"] == 0:
        print("Seeding concession stands...")
        concessions = [
            ("c-1", "Stadium Bites (Sector A)", 15, "Open", "Good"),
            ("c-2", "El Tri Tacos & Nachos (Sector B)", 25, "Open", "Low Stock"),
            ("c-3", "Maple Leaf Grill (Sector C)", 8, "Open", "Good"),
            ("c-4", "Stars & Stripes Brews (Sector D)", 12, "Open", "Good"),
            ("c-5", "FIFA Official Merch Store", 35, "Open", "Good")
        ]
        for c in concessions:
            run_query(
                "INSERT INTO concessions (id, name, queue_time, status, inventory_status) VALUES (?, ?, ?, ?, ?)",
                c
            )

    incident_count = get_one("SELECT COUNT(*) as count FROM incidents")
    if incident_count["count"] == 0:
        print("Seeding initial incidents...")
        incidents = [
            (
                "Elevator malfunction near Gate 4",
                "Elevator #2 is stuck on Level 2. Fans with mobility assistance request support.",
                "Gate 4 Lobby - Level 2",
                "Facilities",
                "High",
                "Open",
                "Tech Support",
                "1. Dispatch technician to elevator #2 immediately.\n2. Guide fans needing accessibility routes to escalators or elevator #1.\n3. Station volunteer at Gate 4 lobby to assist incoming fans."
            ),
            (
                "Concession stand queue overcrowding",
                "Long queues at El Tri Tacos (Sector B) spilling into the concourse walkway.",
                "Sector B Concourse",
                "Crowd Control",
                "Medium",
                "In Progress",
                "Steward Team B",
                "1. Setup crowd barriers to organize the queue.\n2. Update the stadium fan app showing maple leaf grill queue is only 8 mins.\n3. Direct stewards to manage the walkway flow."
            )
        ]
        for i in incidents:
            run_query(
                "INSERT INTO incidents (title, description, location, category, severity, status, assigned_team, ai_protocol) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                i
            )

    sustainability_count = get_one("SELECT COUNT(*) as count FROM sustainability")
    if sustainability_count["count"] == 0:
        print("Seeding sustainability logs...")
        actions = [
            ("GreenFan99", "Recycled Plastic Bottle", 50),
            ("WorldCupEco", "Used Compostable Bin", 30),
            ("EcoTraveler", "Traveled via Metro Train", 100),
            ("ZeroWasteGuy", "Used Reusable Cup", 40)
        ]
        for a in actions:
            run_query(
                "INSERT INTO sustainability (username, action_type, points) VALUES (?, ?, ?)",
                a
            )

    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database()
