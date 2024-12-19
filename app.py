import eventlet
eventlet.monkey_patch()

import logging
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from simulation import Simulation

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Use environment variables for security
socketio = SocketIO(app, async_mode='eventlet')

# Initialize the simulation
simulation = Simulation(steps_per_second=6)  # Set to 6 steps/sec

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    # Send the initial state
    emit('simulation_state', simulation.get_state())
    # Start the simulation thread if not already running
    if not simulation.running:
        simulation.start()
        # Start the background task to emit states
        socketio.start_background_task(target=emit_states)
        logging.info('Simulation thread and state emitter initiated.')

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

def emit_states():
    """Background task to emit simulation states."""
    while simulation.running:
        socketio.sleep(simulation.sleep_interval)
        state = simulation.get_state()
        socketio.emit('simulation_state', state)
        #logging.debug(f"Emitted state for step {state['step']}")

# The 'if __name__ == "__main__":' block remains commented out for deployment
# It is only used for local development with Flask's built-in server

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000, debug=False)
