import numpy as np
import threading
import time
import logging
from Car import Car

# Configure logging for simulation module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Simulation:
    def __init__(
        self,
        L=100,
        N=24,
        vmax=3,
        p_fault=0.1,
        p_slow=0.5,
        steps=1000,
        prob_faster=0.50,
        prob_slower=0.10,
        prob_normal=0.40,
        steps_per_second=2,  # New parameter
    ):
        # Initialize simulation parameters
        self.L = L
        self.N = N
        self.vmax = vmax
        self.p_fault = p_fault
        self.p_slow = p_slow
        self.steps = steps  # Currently unused for infinite simulation
        self.prob_faster = prob_faster
        self.prob_slower = prob_slower
        self.prob_normal = prob_normal
        self.steps_per_second = steps_per_second
        self.sleep_interval = 1.0 / self.steps_per_second

        self.rho = N / (L / 2.0)

        # Initialize cars on two roads
        self.cars_road1 = self.initialize_cars(adaptive_cruise_control=True)
        self.cars_road2 = self.initialize_cars(adaptive_cruise_control=False)

        self.step = 0
        self.running = False

        # Metrics
        self.metrics = {
            'road1': {},
            'road2': {}
        }

        # Lock for thread safety
        self.lock = threading.Lock()

    def set_steps_per_second(self, steps_per_second):
        with self.lock:
            self.steps_per_second = steps_per_second
            self.sleep_interval = 1.0 / self.steps_per_second
            #logging.info(f"Steps per second set to {self.steps_per_second}, sleep interval updated to {self.sleep_interval} seconds.")

    def initialize_cars(self, adaptive_cruise_control):
        occupied_positions = set()
        cars = []
        for _ in range(self.N):
            position = np.random.randint(0, self.L)
            while position in occupied_positions:
                position = np.random.randint(0, self.L)
            occupied_positions.add(position)
            car = Car(
                road_length=self.L,
                cell_width=1,  # For web visualization, cell_width is abstracted
                max_speed=self.vmax,
                p_fault=self.p_fault,
                p_slow=self.p_slow,
                prob_faster=self.prob_faster,
                prob_slower=self.prob_slower,
                prob_normal=self.prob_normal,
                position=position,
                velocity=np.random.randint(1, self.vmax + 1),
                adaptive_cruise_control=adaptive_cruise_control
            )
            cars.append(car)
        road_type = "Road 1 (ACC)" if adaptive_cruise_control else "Road 2 (Human)"
        #logging.debug(f"Initialized {len(cars)} cars on {road_type}.")
        return cars

    def run_step(self):
        try:
            #logging.debug(f"Starting run_step for step {self.step + 1}.")
            # Update Road 1
            self.update_road(self.cars_road1)

            # Update Road 2
            self.update_road(self.cars_road2)

            # Compute metrics
            self.compute_metrics()

            self.step += 1
            #logging.debug(f"Completed run_step for step {self.step}.")
        except Exception as e:
            logging.error(f"Exception in run_step: {e}")
            self.running = False  # Stop simulation on error

    def update_road(self, cars):
        try:
            cars_sorted = sorted(cars, key=lambda c: c.position)
            num_cars = len(cars_sorted)
            for i, car in enumerate(cars_sorted):
                if i < num_cars - 1:
                    next_car = cars_sorted[i + 1]
                    distance = next_car.position - car.position - 1
                    if distance < 0:
                        distance += self.L
                else:
                    next_car = cars_sorted[0]
                    distance = (next_car.position + self.L) - car.position - 1
                velocity_of_next_car = next_car.velocity
                car.update_velocity(distance, velocity_of_next_car)
                #logging.debug(f"Car at position {car.position} updated with distance {distance} and next car velocity {velocity_of_next_car}.")

            for car in cars_sorted:
                car.move()
                #logging.debug(f"Car moved to new position {car.position} with velocity {car.velocity}.")
        except Exception as e:
            logging.error(f"Exception in update_road: {e}")
            self.running = False  # Stop simulation on error

    def compute_metrics(self):
        try:
            average_speed_road1 = np.mean([c.velocity for c in self.cars_road1]) if self.cars_road1 else 0
            stopped_vehicles_road1 = sum(c.velocity == 0 for c in self.cars_road1)
            average_speed_road2 = np.mean([c.velocity for c in self.cars_road2]) if self.cars_road2 else 0
            stopped_vehicles_road2 = sum(c.velocity == 0 for c in self.cars_road2)

            self.metrics['road1'] = {
                'average_speed': average_speed_road1,
                'stopped_vehicles': stopped_vehicles_road1,
                'density': self.rho
            }
            self.metrics['road2'] = {
                'average_speed': average_speed_road2,
                'stopped_vehicles': stopped_vehicles_road2,
                'density': self.rho
            }

            #logging.debug(f"Metrics at step {self.step}: Road1 - Avg Speed: {average_speed_road1}, Stopped: {stopped_vehicles_road1}; Road2 - Avg Speed: {average_speed_road2}, Stopped: {stopped_vehicles_road2}")
        except Exception as e:
            logging.error(f"Exception in compute_metrics: {e}")
            self.running = False  # Stop simulation on error

    def start(self):
        with self.lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self.run)
                self.thread.start()
                logging.info("Simulation started.")

    def run(self):
        logging.info("Simulation thread is running.")
        while self.running:
            with self.lock:
                self.run_step()
            #logging.debug(f"Sleeping for {self.sleep_interval} seconds.")
            time.sleep(self.sleep_interval)
        logging.info("Simulation thread has stopped.")

    def stop(self):
        with self.lock:
            self.running = False
        self.thread.join()
        logging.info("Simulation stopped.")

    def get_state(self):
        with self.lock:
            state = {
                'step': self.step,
                'road1': [
                    {
                        'position': car.position,
                        'velocity': car.velocity,
                        'adaptive_cruise_control': car.adaptive_cruise_control
                    }
                    for car in self.cars_road1
                ],
                'road2': [
                    {
                        'position': car.position,
                        'velocity': car.velocity,
                        'adaptive_cruise_control': car.adaptive_cruise_control
                    }
                    for car in self.cars_road2
                ],
                'metrics': self.metrics
            }
        #logging.debug(f"State retrieved at step {self.step}")
        return state
