export interface DetailChatHistory {
    id: number;
    prompt: string;
    response: string;
    timestamp: string; // ISO date string
    image_url?: string; // Optional image URL for the response
}