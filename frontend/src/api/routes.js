// frontend/src/api/routes.js

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Fetches route recommendations from the NaviX FastAPI backend.
 * @param {Object} params - The routing parameters
 * @param {number} params.origin_lat - Latitude of the origin
 * @param {number} params.origin_lon - Longitude of the origin
 * @param {number} params.destination_lat - Latitude of the destination
 * @param {number} params.destination_lon - Longitude of the destination
 * @param {string} params.place - The city/place name for the bounding box
 * @param {number} [params.max_routes=3] - Maximum number of routes to return
 * @returns {Promise<Object>} The route data including geometry and safety scores
 */
export async function fetchRoutes(params) {
    try {
        const response = await fetch(`${API_BASE_URL}/routes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                origin_lat: params.origin_lat,
                origin_lon: params.origin_lon,
                destination_lat: params.destination_lat,
                destination_lon: params.destination_lon,
                place: params.place,
                max_routes: params.max_routes || 3
            }),
        });

        if (!response.ok) {
            const errBody = await response.json().catch(() => ({}));
            throw new Error(errBody.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching routes from NaviX API:', error);
        throw error;
    }
}
