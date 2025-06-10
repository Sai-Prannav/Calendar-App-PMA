// Weather Service Module
const WeatherService = {
    async getCurrentWeather(location) {
        try {
            const response = await axios.get(`${API_BASE_URL}/weather/current`, {
                params: { location }
            });
            
            if (response.data.status === 'success') {
                return response.data.data;
            }
            throw new Error(response.data.message || 'Failed to fetch current weather');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    async getForecast(location, days = 5) {
        try {
            const response = await axios.get(`${API_BASE_URL}/weather/forecast`, {
                params: { location, days }
            });
            
            if (response.data.status === 'success') {
                return response.data.data;
            }
            throw new Error(response.data.message || 'Failed to fetch forecast');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    async getWeatherQueries() {
        try {
            const response = await axios.get(`${API_BASE_URL}/weather`);
            
            if (response.data.status === 'success') {
                return response.data.data;
            }
            throw new Error(response.data.message || 'Failed to fetch weather history');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    async saveWeatherQuery(queryData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/weather`, queryData);
            
            if (response.data.status === 'success') {
                return response.data;
            }
            throw new Error(response.data.message || 'Failed to save weather query');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    async updateWeatherQuery(queryId, data) {
        try {
            const response = await axios.put(`${API_BASE_URL}/weather/${queryId}`, data);
            
            if (response.data.status === 'success') {
                return response.data;
            }
            throw new Error(response.data.message || 'Failed to update weather query');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    async deleteWeatherQuery(queryId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/weather/${queryId}`);
            
            if (response.data.status === 'success') {
                return response.data;
            }
            throw new Error(response.data.message || 'Failed to delete weather query');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    // Helper methods for weather data processing
    processWeatherData(data) {
        return {
            temperature: this._convertTemperature(data.temperature),
            description: this._capitalizeDescription(data.description),
            humidity: data.humidity,
            windSpeed: this._convertWindSpeed(data.wind_speed),
            timestamp: new Date(data.timestamp).toLocaleString()
        };
    },

    _convertTemperature(celsius) {
        return {
            celsius: Math.round(celsius),
            fahrenheit: Math.round((celsius * 9/5) + 32)
        };
    },

    _convertWindSpeed(mps) {
        return {
            mps: Math.round(mps * 10) / 10,
            kph: Math.round(mps * 3.6),
            mph: Math.round(mps * 2.237)
        };
    },

    _capitalizeDescription(description) {
        return description
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
};

// Export the WeatherService object
window.WeatherService = WeatherService;