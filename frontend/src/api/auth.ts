import axios from "axios";
import apiClient from "./client";

export const login = async (email: string, password: string) => {
  try {
    const response = await apiClient.post("/user/login", {
      email: email,
      password: password,
    });
    return response.data; // Assuming the token is in response.data
  } catch (error) {
    console.error("Login failed:", error);
    throw error;
  }
};

export const register = async (email: string, username: string, password: string) => {
  try {
    const response = await apiClient.post("/user/create", {
      email: email,
      username: username,
      password: password,
    });
    return response.data; // Assuming the token is in response.data
  } catch (error) {
    console.error("Registration failed:", error);
    throw error;
  }
};

export const testUser = async () => {
  try {
    const response = await apiClient.get("/user");
    return response.data; // Assuming the token is in response.data
  } catch (error: unknown) {
    console.error("Test user failed:", error);
    if (axios.isAxiosError(error)) {
      console.error("Axios error details:", {
        message: error.message,
        response: error.response
          ? {
              status: error.response.status,
              data: error.response.data,
            }
          : null,
      });
    }
    throw error;
  }
};
