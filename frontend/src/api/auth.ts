import axios from "axios";
import apiClient from "./client";
import { LoginResponse } from "../types/response/loginResponse";
import { CreateUserResponse } from "../types/response/createUserResponse";
import * as SecureStore from 'expo-secure-store';
import { mapApiError } from "./apiRequestError";

export const login = async (email: string, password: string) : Promise<LoginResponse>=> {
  try {
    const response = await apiClient.post("/user/login", {
      email: email,
      password: password,
    });
    console.log("Login successful:", response.data);
    const token = response.data.user.access_token; // Assuming the token is in response.data.token
    // Store the token securely (e.g., using SecureStore in Expo)
    await SecureStore.setItemAsync("userToken", token);
    return response.data; // Assuming the token is in response.data
  } catch (error) {
    throw mapApiError(error);
  }
};

export const createUser = async (email: string, username: string, password: string): Promise<CreateUserResponse> => {
  try {
    const response = await apiClient.post("/user/create", {
      email: email,
      username: username,
      password: password,
    });
    return response.data; // Assuming the token is in response.data
  } catch (error) {
    console.error("Registration failed:", error);
    throw mapApiError(error);
  }
};


