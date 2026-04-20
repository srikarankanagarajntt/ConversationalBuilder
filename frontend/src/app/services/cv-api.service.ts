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
  showPersonalInfoModal?: boolean;
  cvDraft?: any;
}

export interface TemplateOption {
  templateId: string;
  templateName: string;
  description: string;
  fileType: string;
  fileBase64: string;
  previewImageUrl?: string;
  previewImageBase64?: string;
}

export interface TemplateListResponse {
  templates: TemplateOption[];
}

export interface PersonalInfo {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
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

  exportCv(sessionId: string, format: 'pdf' | 'docx' | 'pptx' | 'json', language: string = 'en'): Observable<{ jobId: string; downloadUrl: string }> {
    return this.http.post<{ jobId: string; downloadUrl: string }>(`${environment.apiBaseUrl}/export`, {
      sessionId,
      format,
      language,
    });
  }

  downloadFile(fileId: string): Observable<any> {
    return this.http.get(`${environment.apiBaseUrl}/download/${fileId}`, { 
      responseType: 'blob',
      observe: 'response'
    });
  }

  testLlm(prompt: string): Observable<{ model: string; output: string }> {
    return this.http.post<{ model: string; output: string }>(`${environment.apiBaseUrl}/llm/test`, {
      prompt,
    });
  }

  getTemplates(): Observable<TemplateListResponse> {
    return this.http.get<TemplateListResponse>(`${environment.apiBaseUrl}/template/options`);
  }

  selectTemplate(sessionId: string, templateId: string): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(`${environment.apiBaseUrl}/template/select`, {
      sessionId,
      templateId,
    });
  }

  submitPersonalInfo(
    sessionId: string,
    fullName: string,
    email: string,
    phone: string,
    location: string,
    summary: string,
    skills: string[]
  ): Observable<ConversationResponse> {
    return this.http.post<ConversationResponse>(`${environment.apiBaseUrl}/conversation/personal-info`, {
      sessionId,
      fullName,
      email,
      phone,
      location,
      summary,
      skills,
    });
  }

  uploadCv(file: File, sessionId: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('sessionId', sessionId);
    return this.http.post<any>(`${environment.apiBaseUrl}/upload/cv`, formData);
  }
}
