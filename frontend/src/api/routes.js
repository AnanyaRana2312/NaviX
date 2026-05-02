import axios from 'axios';

const API_BASE_URL = '/api/v1';

export const fetchRoutes = async (startCoords, endCoords, place = "Dehradun", taskId = null) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/routes`, {
      origin_lat: startCoords[0],
      origin_lon: startCoords[1],
      destination_lat: endCoords[0],
      destination_lon: endCoords[1],
      place: place,
      max_routes: 3,
      task_id: taskId
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching routes:', error);
    throw error;
  }
};

export const fetchRouteProgress = async (taskId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/routes/progress/${taskId}`);
    return response.data;
  } catch (error) {
    return { percent: 0, message: "Waiting..." };
  }
};
