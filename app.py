from flask import Flask, render_template
import random
import os
import json
import fcntl
from gevent.pywsgi import WSGIServer
from flask_socketio import SocketIO, emit
from geventwebsocket.handler import WebSocketHandler

# Import the send_twitch_message function from the bot script

app = Flask(__name__)

# Initialize SocketIO with gevent for compatibility
socketio = SocketIO(app, async_mode='gevent')

def write_message_to_file(name, message):
    with open('message_to_send.json', 'w') as f:
        # Lock the file to prevent simultaneous writes
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump({'name': name, 'message': message}, f)
        fcntl.flock(f, fcntl.LOCK_UN)

# Function to load bingo items from a text file
def load_bingo_items(filename='bingo_items.txt'):
    try:
        with open(filename, "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        return lines
    except FileNotFoundError:
        return []

@app.route('/')
def index():
    # Load bingo items from text file
    bingo_items = load_bingo_items()
    
    # Check if we have enough items to create the bingo card
    if len(bingo_items) < 25:
        return "Not enough items to create a bingo card. Please add more items to the text file."
    
    # Randomly select 25 unique items for the bingo card
    random_items = random.sample(bingo_items, 25)
    random_items[12] = "Free Space"  # Middle space is typically free
    return render_template('index.html', card=random_items)

# Handle socket connection
@socketio.on('bingo')
def handle_bingo_event(data):
    player_name = data.get('name')
    message = data.get('message')
    cells = data.get('cells')
    # Write the message and player name to the file
    write_message_to_file(player_name, message)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Create a WSGI server with gevent and websocket handler
    http_server = WSGIServer(('0.0.0.0', port), app, handler_class=WebSocketHandler)
    print(f"Running on port {port}")
    http_server.serve_forever()
