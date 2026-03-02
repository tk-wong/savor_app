import apiClient from "./client";
import { ChatResponse } from "../types/response";
import { CreateChatGroupResponse } from "../types/response/CreateChatGroupResponse";


export const sendMessage = async (prompt: string, group_id: number): Promise<ChatResponse> => {
    try {
        const response = await apiClient.post("/chat", {
            prompt: prompt,
            group_id: group_id
        });
        return response.data; // Assuming the response contains the chat reply
    } catch (error) {
        console.error("Error sending message:", error);
        throw error;
    }

}

export const getNewChatGroup = async (): Promise<CreateChatGroupResponse> => {
    try {
        const response = await apiClient.get("/chat/group/new");
        return response.data; // Assuming the response contains the new chat group ID
    } catch (error) {
        console.error("Error creating new chat group:", error);
        throw error;
    }
}