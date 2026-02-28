import apiClient from "./client";

export const getAllRecipes = async () => {
    try {
        const response = await apiClient.get("/recipes");
        return response.data; // Assuming the response contains the list of recipes
    } catch (error) {
        console.error("Error fetching recipes:", error);
        throw error;
    }
}

export const getRecipeById = async (id: string) => {
    try {
        const response = await apiClient.get(`/recipes/${id}`);
        return response.data; // Assuming the response contains the recipe details
    } catch (error) {
        console.error(`Error fetching recipe with id ${id}:`, error);
        throw error;
    }
}