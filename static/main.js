document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');

    const road1Y = canvas.height / 3;
    const road2Y = (2 * canvas.height) / 3;
    const roadHeight = 100; // Adjusted for better visibility

    const L = 120; // Road length as per simulation.py

    /**
     * Function to draw roads on the canvas with reduced opacity.
     */
    function drawRoads() {
        ctx.fillStyle = 'rgba(52, 58, 64, 0.3)'; // Dark gray with 70% opacity
        ctx.fillRect(0, road1Y - roadHeight / 2, canvas.width, roadHeight);
        ctx.fillRect(0, road2Y - roadHeight / 2, canvas.width, roadHeight);
    }

    /**
     * Function to draw vertical grid lines across the entire canvas.
     */
    function drawGrid() {
        const cellWidth = canvas.width / L;
        // Removed horizontal grid lines as per requirement

        ctx.strokeStyle = 'rgba(0, 0, 0, 0.6)'; // Darker black with higher opacity
        ctx.lineWidth = 1.5; // Thicker lines for better visibility

        // Draw vertical lines
        for (let i = 0; i <= L; i++) {
            const x = i * cellWidth;
            ctx.beginPath();
            ctx.moveTo(x, 0); // Start from top of the canvas
            ctx.lineTo(x, canvas.height); // Extend to bottom of the canvas
            ctx.stroke();
        }

        // No horizontal lines
    }

    /**
     * Function to draw cars with dynamic colors, outlines, and direction arrows.
     * @param {Array} cars - Array of car objects.
     * @param {number} roadY - Y-coordinate of the road.
     * @param {string} color - Base color of the car.
     * @param {boolean} highlight - Whether to highlight a car.
     */
    function drawCars(cars, roadY, color, highlight = false) {
        cars.forEach((car, index) => {
            const x = (car.position / L) * canvas.width;
            const y = roadY;
            const carSize = Math.min((canvas.width / L) * 2, roadHeight * 0.2); // Adjusted for square-like appearance

            // Determine color based on velocity
            let carColor = 'rgb(255, 0, 0)'; // Default Red for stopped cars

            if (car.velocity > 0) {
                if (car.velocity < 2) { // Assuming max_speed is 4
                    const greenValue = Math.floor(255 * (car.velocity / 2));
                    carColor = `rgb(255, ${greenValue}, 0)`; // Gradient from red to yellow
                } else {
                    const redValue = Math.floor(255 * (1 - (car.velocity - 2) / 2));
                    carColor = `rgb(${redValue}, 255, 0)`; // Gradient from yellow to green
                }
            }

            // Draw car square
            ctx.fillStyle = carColor;
            ctx.fillRect(x, y - carSize / 2, carSize, carSize); // Equal width and height

            // Add blue stroke outline if the car has ACC
            if (car.adaptive_cruise_control) {
                ctx.strokeStyle = '#0000FF'; // Blue outline
                ctx.lineWidth = 3;
                ctx.strokeRect(x, y - carSize / 2, carSize, carSize);
            }

            // Draw direction arrow
            ctx.fillStyle = '#000000'; // Black color for arrow
            ctx.beginPath();
            if (car.velocity > 0) {
                // Forward arrow
                ctx.moveTo(x + carSize, y);
                ctx.lineTo(x + carSize - 10, y - 10); // Adjusted for square size
                ctx.lineTo(x + carSize - 10, y + 10);
            } else {
                // Backward arrow
                ctx.moveTo(x, y);
                ctx.lineTo(x + 10, y - 10);
                ctx.lineTo(x + 10, y + 10);
            }
            ctx.closePath();
            ctx.fill();

            // Draw red dot above the first car on each road
            if (highlight && index === 0) { // Highlight only the first car
                ctx.beginPath();
                ctx.arc(x + carSize / 2, y - carSize / 2 - 10, 5, 0, 2 * Math.PI); // Positioning the dot above the car
                ctx.fillStyle = 'red';
                ctx.fill();
            }
        });
    }

    /**
     * Function to update simulation metrics on the webpage.
     * @param {Object} state - Current simulation state.
     */
    function updateMetrics(state) {
        const road1Info = `Road 1 - Step: ${state.step} | Density: ${state.metrics.road1.density.toFixed(2)} | Avg Speed: ${state.metrics.road1.average_speed.toFixed(2)} | Stopped: ${state.metrics.road1.stopped_vehicles}`;
        const road2Info = `Road 2 - Step: ${state.step} | Density: ${state.metrics.road2.density.toFixed(2)} | Avg Speed: ${state.metrics.road2.average_speed.toFixed(2)} | Stopped: ${state.metrics.road2.stopped_vehicles}`;

        document.getElementById('road1-info').innerText = road1Info;
        document.getElementById('road2-info').innerText = road2Info;
    }

    /**
     * Handle incoming simulation state and render graphics.
     */
    socket.on('simulation_state', (state) => {
        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw roads
        drawRoads();

        // Draw extended grid lines
        drawGrid();

        // Draw cars for Road 1 (ACC cars - Blue) and highlight the first car
        drawCars(state.road1, road1Y, 'blue', true);

        // Draw cars for Road 2 (Human drivers - Red) and highlight the first car
        drawCars(state.road2, road2Y, 'red', true);

        // Update metrics
        updateMetrics(state);
    });

    /**
     * Handle connection errors.
     */
    socket.on('connect_error', (err) => {
        console.error('Connection error:', err);
    });
});
