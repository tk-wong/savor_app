import apiClient from "./client";

export const sendMessage = async (prompt: string) => {
    try {
        const response = await apiClient.post("/chat", {
            prompt: prompt,
        });
        return response.data; // Assuming the response contains the chat reply
    } catch (error) {
        console.error("Error sending message:", error);
        throw error;
    }

}
