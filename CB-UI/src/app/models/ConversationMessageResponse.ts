export interface ConversationMessageResponse {
    assistantMessage: string;
    updatedFields: Record<string, any>;
    missingFields: string[];
    nextStep: string;
    previewAvailable: boolean;
}