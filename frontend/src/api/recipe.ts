import { AllRecipeResponse, RecipeResponse } from "../types/response";
import { mapApiError } from "./apiRequestError";
import apiClient from "./client";

export const getAllRecipes = async (): Promise<AllRecipeResponse> => {
    try {
        const response = await apiClient.get("/recipes");
        return response.data; // Assuming the response contains the list of recipes
    } catch (error) {
        throw mapApiError(error);
    }
}

export const getRecipeById = async (id: number): Promise<RecipeResponse> => {
    try {
        const response = await apiClient.get(`/recipes/${id}`);
        return response.data; // Assuming the response contains the recipe details
    } catch (error) {
        throw mapApiError(error);
    }
}