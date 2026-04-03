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

  testLlm(prompt: string): Observable<{ model: string; output: string }> {
    return this.http.post<{ model: string; output: string }>(`${environment.apiBaseUrl}/llm/test`, {
      prompt,
    });
  }
}
