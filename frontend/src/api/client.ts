import { useRouter } from 'expo-router';
import axios from "axios";
import * as SecureStore from "expo-secure-store";
import { Alert } from 'react-native';

console.log("Full Request URL:", `${process.env.EXPO_PUBLIC_BACKEND_URL}/your-endpoint`);

const apiClient = axios.create({
  baseURL: process.env.EXPO_PUBLIC_BACKEND_URL,
  timeout: 60000, // 60 seconds timeout
  headers: { "Content-Type": "application/json" },
});

const router = useRouter();
let isSessionExpiredHandled = false;

const buildRequestUrl = (baseURL?: string, url?: string): string => {
  if (!url) {
    return baseURL ?? "<unknown-url>";
  }

  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  if (!baseURL) {
    return url;
  }

  return `${baseURL.replace(/\/$/, "")}/${url.replace(/^\//, "")}`;
};

apiClient.interceptors.response.use(
  (response) => {
    const method = response.config.method?.toUpperCase() ?? "UNKNOWN";
    const fullUrl = buildRequestUrl(response.config.baseURL, response.config.url);
    console.log(`[API] ${method} ${fullUrl} -> ${response.status}`);
    return response;
  },
  (error) => {
    const method = error.config?.method?.toUpperCase() ?? "UNKNOWN";
    const fullUrl = buildRequestUrl(error.config?.baseURL, error.config?.url);
    const status = error.response?.status ?? "NO_STATUS";
    console.error(`[API] ${method} ${fullUrl} -> ${status}`);

    if (error.response && error.response.status === 401 && !isSessionExpiredHandled) {
      isSessionExpiredHandled = true;
      console.error("Unauthorized access - redirecting to login");
      SecureStore.deleteItemAsync("userToken");
      Alert.alert("Session expired", "Your session has expired. Please log in again.", [
        { text: "OK", onPress: () => router.replace("/loginPage") }
      ]);
    }
    return Promise.reject(error);
  },
);

apiClient.interceptors.request.use(
  async (config) => {
    const method = config.method?.toUpperCase() ?? "UNKNOWN";
    const fullUrl = buildRequestUrl(config.baseURL, config.url);
    console.log(`[API] ${method} ${fullUrl} -> REQUEST`);

    // You can add authorization headers here if needed, e.g., from localStorage
    const token = await SecureStore.getItemAsync("userToken");
    if (token) {
      isSessionExpiredHandled = false;
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

export default apiClient;

// TODO: handle token refresh (optional)
