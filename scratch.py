import eventlet
eventlet.monkey_patch()

import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pyngrok import ngrok

from simulation import Simulation

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet')

# Set up ngrok
ngrok.set_auth_token("2qID5F1Dl9OuCZZSIbRrCkGpqJa_r6gctcVh4U4Z8VD9pnbP")
port = 5000
public_url = ngrok.connect(port).public_url
print(f"ngrok tunnel available at: {public_url}")

# Initialize the simulation with fixed steps_per_second
simulation = Simulation(steps_per_second=6)  # Set to 6 steps/sec
simulation.start()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    # Send the initial state
    emit('simulation_state', simulation.get_state())
    # Start the background thread if not already started
    socketio.start_background_task(target=background_thread)

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

def background_thread():
    """Send simulation state to clients periodically."""
    steps_per_second = simulation.steps_per_second  # Use the fixed steps_per_second
    sleep_interval = simulation.sleep_interval  # Interval between steps in seconds

    while simulation.running and simulation.step < simulation.steps:
        socketio.sleep(sleep_interval)
        state = simulation.get_state()
        socketio.emit('simulation_state', state)
        logging.debug(f"Emitted state for step {public_url}")

        print(f"ngrok tunnel available at: {public_url}")

        #logging.debug(f"Emitted state for step {state['step']}")

if __name__ == '__main__':
    print(f"Starting Flask app on port {port}")
    socketio.run(app, host='0.0.0.0', port=5000)
