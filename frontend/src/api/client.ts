import axios from "axios";
import * as SecureStore from 'expo-secure-store';

const apiClient = axios.create({
  baseURL: "http://192.168.0.155:5000/api",
  timeout: 120000, // 120 seconds, 2 minutes
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized access, e.g., redirect to login page
      console.error("Unauthorized access - redirecting to login");
    }
    return Promise.reject(error);
  },
);

apiClient.interceptors.request.use(
  async (config) => {
    // You can add authorization headers here if needed, e.g., from localStorage
    const token = await SecureStore.getItemAsync("userToken");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default apiClient;

// TODO: handle token refresh (optional)
