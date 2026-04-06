export interface VoiceMessageResponse {
    assistantMessage: string;
    updatedFields: { [key: string]: any };
    missingFields: string[];
    nextStep: string;
    previewAvailable: boolean;
    transcript: string;
}