import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://192.168.0.155:5000/api",
  timeout: 120000, // 120 seconds, 2 minutes
  // headers: { 'Content-Type': 'application/json' },
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

export default apiClient;
