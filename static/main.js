document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const L = 100; // Updated road length from 80 to 100
    const cellWidth = 20; // Adjusted cell width based on desired canvas size
    const canvasWidth = L * cellWidth; // 100 * 20 = 2000px
    const canvasHeight = 600; // Maintain desired height

    const canvas = document.getElementById('simulation-canvas');
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext('2d');

    const roadHeight = 120; // Increased for better accommodation of larger cars
    const road1Y = canvas.height / 3; // 200px
    const road2Y = (2 * canvas.height) / 3; // 400px

    /**
     * Function to draw roads on the canvas with reduced opacity.
     */
    function drawRoads() {
        ctx.fillStyle = 'rgba(52, 58, 64, 0.3)'; // Dark gray with 30% opacity
        ctx.fillRect(0, road1Y - roadHeight / 2, canvas.width, roadHeight);
        ctx.fillRect(0, road2Y - roadHeight / 2, canvas.width, roadHeight);
    }

    /**
     * Function to draw vertical grid lines across the entire canvas.
     */
    function drawGrid() {
        // Removed horizontal grid lines as per requirement

        ctx.strokeStyle = 'rgba(0, 0, 0, 0.6)'; // Darker black with higher opacity
        ctx.lineWidth = 1.5; // Thicker lines for better visibility

        // Draw vertical lines aligned with cell boundaries
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
        const carSize = cellWidth; // Make car size equal to cell width

        // Define arrow dimensions relative to car size
        const arrowLength = 8; // Smaller arrow length
        const arrowWidth = 6;  // Smaller arrow width

        cars.forEach((car, index) => {
            const x = car.position * cellWidth; // Align to cell start
            const y = roadY;

            // Determine color based on velocity
            let carColor = 'rgb(255, 0, 0)'; // Default Red for stopped cars

            if (car.velocity > 0) {
                if (car.velocity < 2) { // Assuming max_speed is 3
                    const greenValue = Math.floor(255 * (car.velocity / 2));
                    carColor = `rgb(255, ${greenValue}, 0)`; // Gradient from red to yellow
                } else {
                    const redValue = Math.floor(255 * (1 - (car.velocity - 2) / 1)); // Adjusted denominator based on vmax=3
                    carColor = `rgb(${redValue}, 255, 0)`; // Gradient from yellow to green
                }
            }

            // Draw car square aligned to cell
            ctx.fillStyle = carColor;
            ctx.fillRect(x, y - carSize / 2, carSize, carSize); // Start at cell start

            // Add blue stroke outline if the car has ACC
            if (car.adaptive_cruise_control) {
                ctx.strokeStyle = '#0000FF'; // Blue outline
                ctx.lineWidth = 3;
                ctx.strokeRect(x, y - carSize / 2, carSize, carSize);
            }

            // Draw direction arrow scaled appropriately
            ctx.fillStyle = '#000000'; // Black color for arrow
            ctx.beginPath();
            if (car.velocity > 0) {
                // Forward arrow
                ctx.moveTo(x + carSize, y); // Starting at the right edge of the car
                ctx.lineTo(x + carSize - arrowLength, y - arrowWidth); // Top point
                ctx.lineTo(x + carSize - arrowLength, y + arrowWidth); // Bottom point
            } else {
                // Backward arrow
                ctx.moveTo(x, y); // Starting at the left edge of the car
                ctx.lineTo(x + arrowLength, y - arrowWidth); // Top point
                ctx.lineTo(x + arrowLength, y + arrowWidth); // Bottom point
            }
            ctx.closePath();
            ctx.fill();

            // Draw red dot above the first car on each road
            if (highlight && index === 0) { // Highlight only the first car
                ctx.beginPath();
                ctx.arc(x + carSize / 2, y - carSize / 2 - 10, 5, 0, 2 * Math.PI); // Positioned above the car
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
        const road1Info = `Road 1 | Density: ${state.metrics.road1.density.toFixed(2)} | Avg Speed: ${state.metrics.road1.average_speed.toFixed(2)} | Stopped: ${state.metrics.road1.stopped_vehicles} | Max-Vel: 3`;
        const road2Info = `Road 2 | Density: ${state.metrics.road2.density.toFixed(2)} | Avg Speed: ${state.metrics.road2.average_speed.toFixed(2)} | Stopped: ${state.metrics.road2.stopped_vehicles} | Max-Vel: 3`;

        document.getElementById('road1-info').innerText = road1Info;
        document.getElementById('road2-info').innerText = road2Info;
    }

    /**
     * Handle incoming simulation state and render graphics.
     */
    socket.on('simulation_state', (state) => {
        if (!state || typeof state.step !== 'number') {
            console.error('Invalid simulation state received:', state);
            return;
        }

        console.log(`Received state for step ${state.step}`);

        // Clear the canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw roads
        drawRoads();

        // Draw grid lines
        drawGrid();

        // Draw cars for Road 1 (ACC cars - Blue) and highlight the first car
        drawCars(state.road1, road1Y, 'blue', true);

        // Draw cars for Road 2 (Human drivers - Red) and highlight the first car
        drawCars(state.road2, road2Y, 'red', true);

        // Update metrics
        updateMetrics(state);
    });

    /**
     * Handle connection events.
     */
    socket.on('connect', () => {
        console.log('Connected to server.');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server.');
    });

    socket.on('connect_error', (err) => {
        console.error('Connection error:', err);
    });
});
