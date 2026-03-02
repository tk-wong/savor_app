import apiClient from "./client";
import { ChatResponse } from "../types/response";
import { CreateChatGroupResponse } from "../types/response/CreateChatGroupResponse";
import { mapApiError } from "./apiRequestError";


export const sendMessage = async (prompt: string, group_id: number): Promise<ChatResponse> => {
    try {
        const response = await apiClient.post("/chat", {
            prompt: prompt,
            chat_group_id: group_id
        }, {timeout: 120000}); 
        return response.data; // Assuming the response contains the chat reply
    } catch (error) {
        throw mapApiError(error);
    }

}

export const getNewChatGroup = async (): Promise<CreateChatGroupResponse> => {
    try {
        const response = await apiClient.get("/chat/group/new");
        return response.data; // Assuming the response contains the new chat group ID
    } catch (error) {
        throw mapApiError(error);
    }
}