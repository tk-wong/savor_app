import apiClient from "./client";
import {AllChatGroupResponse, ChatResponse} from "../types/response";
import { CreateChatGroupResponse } from "../types/response/CreateChatGroupResponse";
import { mapApiError } from "./apiRequestError";
import {ChatHistoryResponse} from "@/src/types/response/ChatHistoryResponse";


export const sendMessage = async (prompt: string, group_id: number): Promise<ChatResponse> => {
    try {
        const response = await apiClient.post("/chat/", {
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

export const getAllChatGroups = async (): Promise<AllChatGroupResponse> => {
    try {
        const response = await apiClient.get("/chat/group/all");
        return response.data; // Assuming the response contains the list of chat groups
    } catch (error) {
        throw mapApiError(error);
    }
}

export const getChatHistoryByGroupId = async (group_id: number): Promise<ChatHistoryResponse> => {
    try {
        const response = await apiClient.get(`/chat/group/${group_id}/history`);
        return response.data; // Contains chat_history for the requested group
    } catch (error) {
        throw mapApiError(error);
    }
}