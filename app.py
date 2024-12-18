import eventlet
eventlet.monkey_patch()

import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from simulation import Simulation

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, async_mode='eventlet')

# Initialize the simulation with fixed steps_per_second
simulation = Simulation(steps_per_second=6)  # Set to 6 steps/sec

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
    sleep_interval = simulation.sleep_interval  # Interval between steps in seconds
    logging.info("Background thread started.")

    while simulation.running:
        socketio.sleep(sleep_interval)
        state = simulation.get_state()
        socketio.emit('simulation_state', state)
        logging.debug(f"Emitted state for step {state['step']}")

    logging.info("Background thread stopped.")

simulation.start()

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000, debug=False)
# #https://7dd1-46-239-114-85.ngrok-free.app
# #ngrok http 5000
