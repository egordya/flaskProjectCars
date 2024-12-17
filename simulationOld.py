# simulation.py

import numpy as np

from Car import Car


def run_simulation(
    L=120,               # Road length
    N=25,                # Number of cars per road
    vmax=4,              # Maximum speed
    p_fault=0.1,         # Probability of random slowdown
    p_slow=0.5,          # Probability of slow-to-start behavior
    steps=1000,          # Number of steps
    prob_faster=0.70,    # Probability that a driver is faster
    prob_slower=0.10,    # Probability that a driver is slower
    prob_normal=0.20,    # Probability that a driver is normal
    headless=False
):
    # Ensure probabilities sum to 1
    if not np.isclose(prob_faster + prob_slower + prob_normal, 1.0):
        raise ValueError("prob_faster, prob_slower, and prob_normal must sum to 1.")

    rho = N / (L / 2.0)  # rho = N / (L/2) = 2N/L

    DRAW_GRID = True
    SIM_STEPS_PER_SECOND = 20
    SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
    cruise_control_percentage_road1 = 100

    N_ACC_CARS = int(cruise_control_percentage_road1 / 100 * N)

    # Setup Pygame if not headless
    if not headless:
        import pygame
        pygame.init()
        WINDOW_WIDTH = 2500
        WINDOW_HEIGHT = 800
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Traffic Simulation")
        font = pygame.font.SysFont(None, 24)
        clock = pygame.time.Clock()
        FPS = 60

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        DODGERBLUE = (30, 144, 255)
        SALMON = (250, 128, 114)

        ROAD_Y_TOP = WINDOW_HEIGHT // 3
        ROAD_Y_BOTTOM = 2 * WINDOW_HEIGHT // 3
        CELL_WIDTH = WINDOW_WIDTH / L
        CAR_HEIGHT = 20
    else:
        WHITE = BLACK = DODGERBLUE = SALMON = None
        CELL_WIDTH = 1
        CAR_HEIGHT = 1
        ROAD_Y_TOP = ROAD_Y_BOTTOM = None

    # Initialize Roads
    occupied_positions_road1 = set()
    cars_road1 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road1:
            position = np.random.randint(0, L)
        occupied_positions_road1.add(position)
        acc_enabled = (np.random.rand() < (cruise_control_percentage_road1 / 100))
        car = Car(
            road_length=L,
            cell_width=CELL_WIDTH,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            position=position,
            adaptive_cruise_control=acc_enabled
        )
        cars_road1.append(car)

    occupied_positions_road2 = set()
    cars_road2 = []
    for _ in range(N):
        position = np.random.randint(0, L)
        while position in occupied_positions_road2:
            position = np.random.randint(0, L)
        occupied_positions_road2.add(position)
        car = Car(
            road_length=L,
            cell_width=CELL_WIDTH,
            max_speed=vmax,
            p_fault=p_fault,
            p_slow=p_slow,
            prob_faster=prob_faster,
            prob_slower=prob_slower,
            prob_normal=prob_normal,
            position=position,
            adaptive_cruise_control=False
        )
        cars_road2.append(car)

    highlight_car_road1 = cars_road1[0] if cars_road1 else None
    highlight_car_road2 = cars_road2[0] if cars_road2 else None

    paused = False
    running = True
    step = 0

    # For stop-start frequency tracking
    prev_velocity_road1 = {}
    prev_velocity_road2 = {}
    stop_start_count_road1 = {}
    stop_start_count_road2 = {}

    for c in cars_road1:
        prev_velocity_road1[c] = c.velocity
        stop_start_count_road1[c] = 0

    for c in cars_road2:
        prev_velocity_road2[c] = c.velocity
        stop_start_count_road2[c] = 0



    if not headless:
        import pygame
        last_simulation_step_time = pygame.time.get_ticks()
    else:
        last_simulation_step_time = 0


    try:
        while running and step < steps:
            if not headless:
                import pygame
                current_time = pygame.time.get_ticks()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            paused = not paused
                        elif event.key == pygame.K_UP:
                            SIM_STEPS_PER_SECOND += 1
                            SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                        elif event.key == pygame.K_DOWN:
                            SIM_STEPS_PER_SECOND = max(1, SIM_STEPS_PER_SECOND - 1)
                            SIMULATION_STEP_INTERVAL = 1000 / SIM_STEPS_PER_SECOND
                        elif event.key == pygame.K_g:
                            DRAW_GRID = not DRAW_GRID
                        elif event.key == pygame.K_ESCAPE:
                            running = False


                if paused or (current_time - last_simulation_step_time < SIMULATION_STEP_INTERVAL):
                    if paused:
                        clock.tick(FPS)
                        continue
                    else:
                        clock.tick(FPS)
                        continue
                else:
                    last_simulation_step_time = current_time

            # Update Road 1
            cars_sorted_road1 = sorted(cars_road1, key=lambda c: c.position)
            for i, car in enumerate(cars_sorted_road1):
                if i < len(cars_sorted_road1) - 1:
                    next_car = cars_sorted_road1[i + 1]
                    distance = next_car.position - car.position - 1
                    if distance < 0:
                        distance += L
                else:
                    next_car = cars_sorted_road1[0]
                    distance = (next_car.position + L) - car.position - 1
                velocity_of_next_car = next_car.velocity
                car.update_velocity(distance, velocity_of_next_car)

            for car in cars_sorted_road1:
                car.move()

            # Update Road 2
            cars_sorted_road2 = sorted(cars_road2, key=lambda c: c.position)
            for i, car in enumerate(cars_sorted_road2):
                if i < len(cars_sorted_road2) - 1:
                    next_car = cars_sorted_road2[i + 1]
                    distance = next_car.position - car.position - 1
                    if distance < 0:
                        distance += L
                else:
                    next_car = cars_sorted_road2[0]
                    distance = (next_car.position + L) - car.position - 1
                velocity_of_next_car = next_car.velocity
                car.update_velocity(distance, velocity_of_next_car)

            for car in cars_sorted_road2:
                car.move()


            # Track stop-start transitions
            for car in cars_road1:
                if (prev_velocity_road1[car] == 0 and car.velocity > 0) or (
                        prev_velocity_road1[car] > 0 and car.velocity == 0):
                    stop_start_count_road1[car] += 1
                prev_velocity_road1[car] = car.velocity

            for car in cars_road2:
                if (prev_velocity_road2[car] == 0 and car.velocity > 0) or (
                        prev_velocity_road2[car] > 0 and car.velocity == 0):
                    stop_start_count_road2[car] += 1
                prev_velocity_road2[car] = car.velocity

            # Compute metrics again after updating
            average_speed_road1 = np.mean([c.velocity for c in cars_road1]) if cars_road1 else 0
            stopped_vehicles_road1 = sum(c.velocity == 0 for c in cars_road1)
            average_speed_road2 = np.mean([c.velocity for c in cars_road2]) if cars_road2 else 0
            stopped_vehicles_road2 = sum(c.velocity == 0 for c in cars_road2)


            step += 1

            if not headless:
                screen.fill(WHITE)
                import pygame
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_TOP), (2500, ROAD_Y_TOP), 2)
                pygame.draw.line(screen, BLACK, (0, ROAD_Y_BOTTOM), (2500, ROAD_Y_BOTTOM), 2)
                draw_grid(screen, ROAD_Y_TOP, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)
                draw_grid(screen, ROAD_Y_BOTTOM, L, CELL_WIDTH, WINDOW_HEIGHT=800, DRAW_GRID=DRAW_GRID)

                for car in cars_road1:
                    car.draw(screen, ROAD_Y_TOP, CAR_HEIGHT, highlight=(car == highlight_car_road1))
                for car in cars_road2:
                    car.draw(screen, ROAD_Y_BOTTOM, CAR_HEIGHT, highlight=(car == highlight_car_road2))

                # Dynamic Text Rendering
                road1_text = f"Road 1 - {N_ACC_CARS} ACC Cars - Step: {step} | Density: {rho:.2f} | Avg Speed: {average_speed_road1:.2f} | Stopped: {stopped_vehicles_road1}"
                road1_surface = font.render(road1_text, True, DODGERBLUE)
                screen.blit(road1_surface, (20, 20))

                road2_text = f"Road 2 - {N} Human Drivers (No ACC) - Step: {step} | Density: {rho:.2f} | Avg Speed: {average_speed_road2:.2f} | Stopped: {stopped_vehicles_road2}"
                road2_surface = font.render(road2_text, True, SALMON)
                road2_text_x = 20
                road2_text_y = ROAD_Y_TOP + (ROAD_Y_BOTTOM - ROAD_Y_TOP) // 2
                screen.blit(road2_surface, (road2_text_x, road2_text_y))

                pygame.display.flip()
                clock.tick(FPS)


    finally:
        if not headless:
            import pygame
            pygame.quit()


        return cars_road1, cars_road2


def draw_grid(screen, road_y, L, CELL_WIDTH, WINDOW_HEIGHT, DRAW_GRID):
    if DRAW_GRID:
        for i in range(L + 1):
            x = i * CELL_WIDTH
            import pygame
            pygame.draw.line(screen, (200, 200, 200),
                             (x, road_y - WINDOW_HEIGHT // 8),
                             (x, road_y + WINDOW_HEIGHT // 8), 1)

if __name__ == "__main__":
    # Running with defaults
    run_simulation(headless=False)
