import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_URLS } from '../constants/api_urls';

import { ConversationMessageRequest } from '../models/ConversationMessageRequest';
import { ConversationMessageResponse } from '../models/ConversationMessageResponse';
import { ExportRequest } from '../models/ExportRequest';
import { ExportResponse } from '../models/ExportResponse';
import { PreviewResponse } from '../models/PreviewResponse';
import { PreviewUpdate } from '../models/PreviewUpdate';
import { Session } from '../models/Session';
import { SessionCreateRequest } from '../models/SessionCreateRequest';
import { SessionCreateResponse } from '../models/SessionCreateResponse';
import { Template } from '../models/Template';
import { TemplateSelectRequest } from '../models/TemplateSelectRequest';
import { TemplateSelectResponse } from '../models/TemplateSelectResponse';
import { VoiceTranscribeResponse } from '../models/VoiceTranscribeResponse';
import { VoiceMessageResponse } from '../models/VoiceMessageReponse';

@Injectable({
  providedIn: 'root'
})
export class ChatbotService {

  constructor(private http: HttpClient) { }

  // Session Management
  sessionCreate(sessionCreateRequest: SessionCreateRequest): Observable<SessionCreateResponse> {
    return this.http.post<SessionCreateResponse>(API_URLS.SESSION.CREATE_SESSION, sessionCreateRequest);
  }

  sessionGet(sessionId: string): Observable<Session> {
    return this.http.get<Session>(API_URLS.SESSION.GET_SESSION(sessionId));
  }

  // Conversation Management
  conversationSendMessage(request: ConversationMessageRequest): Observable<ConversationMessageResponse> {
    return this.http.post<ConversationMessageResponse>(API_URLS.CONVERSATION.MESSAGE, request);
  }

  // Voice Message Management
  voiceTranscribeMessage(audioFile: FormData): Observable<VoiceTranscribeResponse> { // FormData contains audio file with key 'audio'
    return this.http.post<VoiceTranscribeResponse>(API_URLS.VOICE.TRANSCRIBE, audioFile);
  }

  voiceSendMessage(audioFile: FormData): Observable<VoiceMessageResponse> { // FormData contains audio file with key 'audio', and sessionId
    return this.http.post<VoiceMessageResponse>(API_URLS.VOICE.MESSAGE, audioFile);
  }

  // Upload CV
  uploadCV(file: FormData): Observable<any> { // FormData contains file with key 'file', and sessionId
    return this.http.post(API_URLS.UPLOAD.CV, file);
  }

  // Template Management
  templateGetOptions(): Observable<Template[]> {
    return this.http.get<Template[]>(API_URLS.TEMPLATE.OPTIONS);
  }

  templateSelect(request: TemplateSelectRequest): Observable<TemplateSelectResponse> {
    return this.http.post<TemplateSelectResponse>(API_URLS.TEMPLATE.SELECT, request);
  }

  // Preview Management
  previewGet(sessionId: string): Observable<PreviewResponse> {
    return this.http.get<PreviewResponse>(API_URLS.PREVIEW.GET(sessionId));
  }

  previewUpdate(sessionId: string, updateData: PreviewUpdate): Observable<PreviewResponse> {
    return this.http.put<PreviewResponse>(API_URLS.PREVIEW.UPDATE(sessionId), updateData);
  }

  // Export Management
  exportRequest(request: ExportRequest): Observable<ExportResponse> {
    return this.http.post<ExportResponse>(API_URLS.EXPORT.REQUEST, request);
  }

  exportStatus(jobId: string): Observable<ExportResponse> {
    return this.http.get<ExportResponse>(API_URLS.EXPORT.STATUS(jobId));
  }

  // Download Management
  downloadFile(fileId: string): Observable<Blob> {
    return this.http.get(API_URLS.DOWNLOAD.FILE(fileId), { responseType: 'blob' });
  }
}
