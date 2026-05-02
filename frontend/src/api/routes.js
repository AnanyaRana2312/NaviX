import axios from 'axios';

const API_BASE_URL = '/api/v1';

export const fetchRoutes = async (startCoords, endCoords, place = "New York City") => {
  try {
    const response = await axios.post(`${API_BASE_URL}/routes`, {
      origin_lat: startCoords[0],
      origin_lon: startCoords[1],
      destination_lat: endCoords[0],
      destination_lon: endCoords[1],
      place: place,
      max_routes: 3
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching routes:', error);
    throw error;
  }
};
