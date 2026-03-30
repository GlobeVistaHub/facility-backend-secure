from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# CORS allows your Next.js app on port 3000 to talk to this Python app on port 5001
CORS(app) 

def get_real_tickets():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Grab all tickets, newest first
    cursor.execute("SELECT ticket_number, phone_number, category, description, status, timestamp FROM tickets ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

@app.route('/api/tickets', methods=['GET'])
def get_tickets_endpoint():
    tickets = get_real_tickets()
    return jsonify(tickets)

if __name__ == '__main__':
    print("System Status: Python API Server Running on Port 5001 🟢")
    app.run(port=5001, debug=True)