// Constants
const API_BASE_URL = 'http://localhost:5000/api';
const DEVELOPER_NAME = 'John Doe'; // Replace with your name

// DOM Elements
const weatherForm = document.getElementById('weatherForm');
const locationInput = document.getElementById('location');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const currentWeatherDiv = document.getElementById('currentWeather');
const forecastDiv = document.getElementById('forecast');
const historyTableBody = document.getElementById('historyTableBody');

// Initialize date inputs with valid range
document.addEventListener('DOMContentLoaded', () => {
    setupDateInputs();
    loadWeatherHistory();
    updateDeveloperInfo();
});

function setupDateInputs() {
    const today = new Date();
    const maxPastDate = new Date(today);
    maxPastDate.setDate(today.getDate() - 7);
    
    const maxFutureDate = new Date(today);
    maxFutureDate.setDate(today.getDate() + 5);
    
    const formatDate = date => date.toISOString().split('T')[0];
    
    startDateInput.min = formatDate(maxPastDate);
    startDateInput.max = formatDate(maxFutureDate);
    endDateInput.min = formatDate(maxPastDate);
    endDateInput.max = formatDate(maxFutureDate);
    
    startDateInput.value = formatDate(today);
    endDateInput.value = formatDate(today);
}

function updateDeveloperInfo() {
    const developerElement = document.querySelector('.developer-name');
    if (developerElement) {
        developerElement.textContent = `Developer: ${DEVELOPER_NAME}`;
    }
}

// Form submission handler
weatherForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        showLoading(currentWeatherDiv);
        
        // Get current weather
        const currentWeather = await WeatherService.getCurrentWeather(locationInput.value);
        displayCurrentWeather(currentWeather);
        
        // Get forecast
        const forecast = await WeatherService.getForecast(locationInput.value);
        displayForecast(forecast);
        
        // Save search to history
        await saveWeatherQuery({
            location: locationInput.value,
            date_range_start: startDateInput.value,
            date_range_end: endDateInput.value,
            temperature: currentWeather.temperature,
            weather_conditions: currentWeather.description
        });
        
        // Update history display
        await loadWeatherHistory();
        
        // Load location media
        await loadLocationMedia(locationInput.value);
        
    } catch (error) {
        showError(currentWeatherDiv, error.message);
    }
});

// Display functions
function displayCurrentWeather(data) {
    currentWeatherDiv.innerHTML = `
        <div class="text-center">
            <div class="weather-icon-container">
                <img src="assets/weather-icons/${getWeatherIcon(data.description)}.png" 
                     alt="${data.description}" class="weather-icon">
            </div>
            <div class="temperature">${Math.round(data.temperature)}°C</div>
            <div class="weather-info">
                <p>${data.description}</p>
                <p>Feels like: ${Math.round(data.feels_like)}°C</p>
                <p>Humidity: ${data.humidity}%</p>
                <p>Wind Speed: ${data.wind_speed} m/s</p>
            </div>
        </div>
    `;
}

function displayForecast(forecast) {
    forecastDiv.innerHTML = forecast.map(day => `
        <div class="col">
            <div class="forecast-card">
                <div class="forecast-date">${formatDate(day.date)}</div>
                <img src="assets/weather-icons/${getWeatherIcon(day.description)}.png" 
                     alt="${day.description}" class="weather-icon">
                <div class="forecast-temp">${Math.round(day.average_temp)}°C</div>
                <div class="forecast-minmax">
                    H: ${Math.round(day.max_temp)}°C
                    L: ${Math.round(day.min_temp)}°C
                </div>
            </div>
        </div>
    `).join('');
}

async function loadWeatherHistory() {
    try {
        const queries = await WeatherService.getWeatherQueries();
        displayWeatherHistory(queries);
    } catch (error) {
        showError(historyTableBody, 'Failed to load weather history');
    }
}

function displayWeatherHistory(queries) {
    historyTableBody.innerHTML = queries.map(query => `
        <tr>
            <td>${query.location}</td>
            <td>${formatDate(query.date_range_start)} to ${formatDate(query.date_range_end)}</td>
            <td>${Math.round(query.temperature)}°C</td>
            <td>${query.weather_conditions}</td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-danger" 
                        onclick="deleteWeatherQuery(${query.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Utility functions
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

function showError(element, message) {
    hideLoading(element);
    element.innerHTML = `
        <div class="error-message">
            ${message}
        </div>
    `;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function getWeatherIcon(description) {
    const iconMap = {
        'clear sky': 'sunny',
        'few clouds': 'partly-cloudy',
        'scattered clouds': 'cloudy',
        'broken clouds': 'cloudy',
        'shower rain': 'rain',
        'rain': 'rain',
        'thunderstorm': 'storm',
        'snow': 'snow',
        'mist': 'fog'
    };
    
    const normalizedDescription = description.toLowerCase();
    return iconMap[normalizedDescription] || 'unknown';
}

// Error handler
window.onerror = function(message, source, lineno, colno, error) {
    console.error('Global error:', error);
    showError(currentWeatherDiv, 'An unexpected error occurred. Please try again.');
    return false;
};