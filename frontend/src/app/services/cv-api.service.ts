import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';

export interface SessionResponse {
  sessionId: string;
  createdAt: string;
  status: string;
}

export interface ConversationResponse {
  sessionId: string;
  reply: string;
  missingFields: string[];
  nextQuestion?: string | null;
  transcript?: string | null;
}

@Injectable({ providedIn: 'root' })
export class CvApiService {
  constructor(private readonly http: HttpClient) {}

  createSession(userId: string): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${environment.apiBaseUrl}/session`, { userId });
  }

  sendMessage(sessionId: string, message: string): Observable<ConversationResponse> {
    return this.http.post<ConversationResponse>(`${environment.apiBaseUrl}/conversation/message`, {
      sessionId,
      message,
    });
  }

  sendVoiceMessage(sessionId: string, audioBlob: Blob, filename = 'recording.webm'): Observable<ConversationResponse> {
    const form = new FormData();
    form.append('session_id', sessionId);
    form.append('file', audioBlob, filename);
    return this.http.post<ConversationResponse>(`${environment.apiBaseUrl}/voice/message`, form);
  }

  speakText(text: string, voice?: string, format = 'mp3'): Observable<Blob> {
    return this.http.post(`${environment.apiBaseUrl}/voice/speak`, { text, voice, format }, { responseType: 'blob' });
  }

  exportCv(sessionId: string, format: 'pdf' | 'docx' | 'json'): Observable<{ jobId: string; downloadUrl: string }> {
    return this.http.post<{ jobId: string; downloadUrl: string }>(`${environment.apiBaseUrl}/export`, {
      sessionId,
      format,
    });
  }

  downloadFile(fileId: string): Observable<Blob> {
    return this.http.get(`${environment.apiBaseUrl}/download/${fileId}`, { responseType: 'blob' });
  }

  testLlm(prompt: string): Observable<{ model: string; output: string }> {
    return this.http.post<{ model: string; output: string }>(`${environment.apiBaseUrl}/llm/test`, {
      prompt,
    });
  }
}
