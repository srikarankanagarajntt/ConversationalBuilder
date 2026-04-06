import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ConversationResponse, CvApiService, SessionResponse } from './services/cv-api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  userId = 'dev-user';
  sessionId = '';
  message = '';
  llmPrompt = 'Give me 2 concise CV summary lines for a Full Stack Developer.';

  assistantReply = '';
  transcript = '';
  llmOutput = '';
  errorMessage = '';
  missingFields: string[] = [];
  loading = false;
  recording = false;

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(private readonly api: CvApiService) {}

  createSession(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.createSession(this.userId).subscribe({
      next: (res: SessionResponse) => {
        this.sessionId = res.sessionId;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to create session.';
        this.loading = false;
      },
    });
  }

  sendMessage(): void {
    if (!this.sessionId || !this.message.trim()) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.sendMessage(this.sessionId, this.message).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        this.transcript = '';
        this.missingFields = res.missingFields;
        this.message = '';
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to send message.';
        this.loading = false;
      },
    });
  }

  async toggleRecording(): Promise<void> {
    if (this.recording) {
      this.stopRecording();
      return;
    }

    if (!this.sessionId) {
      this.errorMessage = 'Create a session before recording.';
      return;
    }

    await this.startRecording();
  }

  private async startRecording(): Promise<void> {
    this.errorMessage = '';
    this.audioChunks = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        const mimeType = this.audioChunks[0]?.type || 'audio/webm';
        const audioBlob = new Blob(this.audioChunks, { type: mimeType });
        this.recording = false;

        // Release microphone access after each recording.
        this.mediaRecorder?.stream.getTracks().forEach((track) => track.stop());
        this.mediaRecorder = null;

        if (audioBlob.size > 0) {
          this.sendVoiceMessage(audioBlob);
        }
      };

      this.mediaRecorder.start();
      this.recording = true;
    } catch {
      this.errorMessage = 'Microphone access failed. Check browser permissions.';
      this.recording = false;
    }
  }

  private stopRecording(): void {
    if (this.mediaRecorder && this.recording) {
      this.mediaRecorder.stop();
    }
  }

  private sendVoiceMessage(audioBlob: Blob): void {
    this.loading = true;
    this.errorMessage = '';

    this.api.sendVoiceMessage(this.sessionId, audioBlob).subscribe({
      next: (res: ConversationResponse) => {
        this.transcript = res.transcript ?? '';
        this.assistantReply = res.reply;
        this.missingFields = res.missingFields;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to process voice message.';
        this.loading = false;
      },
    });
  }

  testLlm(): void {
    if (!this.llmPrompt.trim()) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.testLlm(this.llmPrompt).subscribe({
      next: (res: { model: string; output: string }) => {
        this.llmOutput = res.output;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'LLM test call failed.';
        this.loading = false;
      },
    });
  }
}
