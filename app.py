from flask import Flask, render_template
import random
import os
import json
from gevent.pywsgi import WSGIServer
from flask_socketio import SocketIO
from geventwebsocket.handler import WebSocketHandler
import redis

# Connect to Redis (example configuration)
redis_client = redis.StrictRedis(host='your-redis-host', port=6379, db=0)

app = Flask(__name__)

# Initialize SocketIO with gevent for compatibility
socketio = SocketIO(app, async_mode='gevent')

def write_message_to_redis(name, message):
    redis_client.set('message_to_send', json.dumps({'name': name, 'message': message}))

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
