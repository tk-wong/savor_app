
import axios from "axios";
import { Alert } from "react-native";


export class ApiRequestError extends Error {
  status?: number;
  details?: unknown;

  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.details = details;
  }
}

export const mapApiError = (error: unknown): ApiRequestError => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const serverMessage =
      (error.response?.data as { message?: string } | undefined)?.message;

    switch (status) {
      case 400:
        return new ApiRequestError(serverMessage ?? "Bad request.", status, error);
      case 401:
        return new ApiRequestError("Unauthorized. Please sign in again.", status, error);
      case 403:
        return new ApiRequestError("Forbidden.", status, error);
      case 404:
        return new ApiRequestError("Resource not found.", status, error);
      case 409:
        return new ApiRequestError("Conflict error.", status, error);
      case 422:
        return new ApiRequestError(serverMessage ?? "Validation failed.", status, error);
      case 429:
        return new ApiRequestError("Too many requests. Try again shortly.", status, error);
      default:
        if (status && status >= 500) {
          return new ApiRequestError("Server error. Please try again.", status, error);
        }
        return new ApiRequestError(serverMessage ?? "Network/API error.", status, error);
    }
  }

  return new ApiRequestError("Unexpected error.", undefined, error);
};

