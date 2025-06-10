// Export Service Module
const ExportService = {
    async exportData(format = 'json') {
        try {
            const response = await axios.get(`${API_BASE_URL}/weather/export`, {
                params: { format },
                responseType: format === 'csv' ? 'blob' : 'json'
            });

            if (format === 'csv') {
                this.downloadFile(response.data, 'weather_data.csv', 'text/csv');
            } else {
                this.downloadJSON(response.data);
            }
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export data: ' + (error.response?.data?.message || error.message));
        }
    },

    downloadJSON(data) {
        // Convert data to formatted JSON string
        const jsonString = JSON.stringify(data, null, 2);
        
        // Create blob and download
        const blob = new Blob([jsonString], { type: 'application/json' });
        this.downloadFile(blob, 'weather_data.json', 'application/json');
    },

    downloadFile(data, filename, mimeType) {
        const blob = data instanceof Blob ? data : new Blob([data], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    },

    formatDataForExport(queries) {
        return queries.map(query => ({
            id: query.id,
            location: query.location,
            location_type: query.location_type,
            date_range: `${query.date_range_start} to ${query.date_range_end}`,
            temperature: `${Math.round(query.temperature)}°C`,
            weather_conditions: query.weather_conditions,
            created_at: new Date(query.created_at).toLocaleString(),
            updated_at: new Date(query.updated_at).toLocaleString()
        }));
    }
};

// Export button event handlers
function exportData(format) {
    ExportService.exportData(format).catch(error => {
        console.error('Export error:', error);
        alert('Failed to export data. Please try again.');
    });
}

// Register export buttons if they exist
document.addEventListener('DOMContentLoaded', () => {
    const exportButtons = document.querySelectorAll('[onclick^="exportData"]');
    exportButtons.forEach(button => {
        const format = button.getAttribute('onclick').match(/'([^']+)'/)[1];
        button.onclick = (e) => {
            e.preventDefault();
            exportData(format);
        };
    });
});

// Export the ExportService object
window.ExportService = ExportService;