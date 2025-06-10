// Maps Service Module
const MapsService = {
    mapContainer: null,
    map: null,
    marker: null,

    async loadLocationMedia(location) {
        try {
            const response = await axios.get(`${API_BASE_URL}/location/media`, {
                params: { location }
            });

            if (response.data.status === 'success') {
                this.updateMapEmbed(response.data.data.location);
                return response.data.data;
            }
            throw new Error(response.data.message || 'Failed to load location media');
        } catch (error) {
            throw new Error(error.response?.data?.message || error.message);
        }
    },

    updateMapEmbed(locationData) {
        // Create map container if it doesn't exist
        if (!this.mapContainer) {
            this.createMapContainer();
        }

        // Update map URL with location data
        const mapUrl = this.generateMapUrl(locationData);
        const mapFrame = document.getElementById('locationMap');
        if (mapFrame) {
            mapFrame.src = mapUrl;
        }
    },

    createMapContainer() {
        // Create map section if it doesn't exist
        if (!document.getElementById('mapSection')) {
            const mapHtml = `
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="card-title mb-0">Location Map</h5>
                            </div>
                            <div class="card-body">
                                <div class="map-container">
                                    <iframe
                                        id="locationMap"
                                        width="100%"
                                        height="450"
                                        style="border:0;"
                                        loading="lazy"
                                        allowfullscreen
                                        referrerpolicy="no-referrer-when-downgrade">
                                    </iframe>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Insert map section before the history section
            const historySection = document.querySelector('.row:last-child');
            historySection.insertAdjacentHTML('beforebegin', mapHtml);
            this.mapContainer = document.getElementById('locationMap');
        }
    },

    generateMapUrl(locationData) {
        let mapUrl = 'https://www.google.com/maps/embed/v1/place';
        mapUrl += `?key=${this.getGoogleMapsKey()}`;

        if (locationData.type === 'coordinates') {
            mapUrl += `&q=${locationData.latitude},${locationData.longitude}`;
        } else {
            mapUrl += `&q=${encodeURIComponent(locationData.normalized)}`;
        }

        return mapUrl;
    },

    getGoogleMapsKey() {
        // In a real application, this would be securely managed
        // For this demo, we'll use a placeholder
        return 'YOUR_GOOGLE_MAPS_API_KEY';
    },

    // Helper method to format coordinates for display
    formatCoordinates(lat, lng) {
        const latitude = Math.abs(lat).toFixed(4) + '°' + (lat >= 0 ? 'N' : 'S');
        const longitude = Math.abs(lng).toFixed(4) + '°' + (lng >= 0 ? 'E' : 'W');
        return `${latitude}, ${longitude}`;
    }
};

// Load location media when a new location is searched
weatherForm.addEventListener('submit', async (e) => {
    try {
        const location = locationInput.value;
        await MapsService.loadLocationMedia(location);
    } catch (error) {
        console.error('Error loading location media:', error);
        // Don't throw error here to prevent blocking weather data display
    }
});

// Export the MapsService object
window.MapsService = MapsService;