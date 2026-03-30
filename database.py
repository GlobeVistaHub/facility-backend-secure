import sqlite3

def init_db():
    # This creates a file called 'tickets.db' in your folder
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    
    # Create the table for Maintenance Tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE,
            phone_number TEXT,
            category TEXT,
            description TEXT,
            status TEXT DEFAULT 'جديد',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add a dummy ticket just so we can see it in the dashboard
    try:
        cursor.execute('''
            INSERT INTO tickets (ticket_number, phone_number, category, description, status)
            VALUES ('TKT-1001', '+201000000000', 'تكييف', 'التكييف ينقط مياه في الغرفة', 'جديد')
        ''')
    except:
        pass # Ignore if dummy data already exists

    conn.commit()
    conn.close()
    print("System Status: Database Initialized Successfully. 🟢")

if __name__ == '__main__':
    init_db()