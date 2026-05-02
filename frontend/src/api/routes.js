import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const fetchRoutes = async (startCoords, endCoords) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/routes`, {
      start: startCoords,
      end: endCoords
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching routes:', error);
    throw error;
  }
};
