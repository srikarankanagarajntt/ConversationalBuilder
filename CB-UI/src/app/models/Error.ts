interface ErrorDetail {
    field: string;
    issue: string;
}

export interface Error {
    code: string;
    message: string;
    traceId: string;
    details: ErrorDetail[];
}