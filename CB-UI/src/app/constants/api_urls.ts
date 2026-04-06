export const API_URLS = {
    SESSION: {
        CREATE_SESSION: '/api/session',
        GET_SESSION: (sessionId: string) => `/api/session/${sessionId}`,
    },
    CONVERSATION: {
        MESSAGE: '/api/conversation/message',
    },
    VOICE: {
        TRANSCRIBE: '/api/voice/transcribe',
        MESSAGE: '/api/voice/message',
    },
    UPLOAD: {
        CV: '/api/upload/cv',
    },
    TEMPLATE: {
        OPTIONS: '/api/template/options',
        SELECT: '/api/template/select',
    },
    PREVIEW: {
        GET: (sessionId: string) => `/api/preview/${sessionId}`,
        UPDATE: (sessionId: string) => `/api/preview/${sessionId}`,
    },
    EXPORT: {
        REQUEST: '/api/export',
        STATUS: (jobId: string) => `/api/export/${jobId}`,
    },
    DOWNLOAD: {
        FILE: (fileId: string) => `/api/download/${fileId}`,
    }
}