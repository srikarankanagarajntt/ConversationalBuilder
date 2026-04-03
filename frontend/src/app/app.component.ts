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
  llmOutput = '';
  missingFields: string[] = [];
  loading = false;

  constructor(private readonly api: CvApiService) {}

  createSession(): void {
    this.loading = true;
    this.api.createSession(this.userId).subscribe({
      next: (res: SessionResponse) => {
        this.sessionId = res.sessionId;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  sendMessage(): void {
    if (!this.sessionId || !this.message.trim()) {
      return;
    }

    this.loading = true;
    this.api.sendMessage(this.sessionId, this.message).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        this.missingFields = res.missingFields;
        this.message = '';
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  testLlm(): void {
    if (!this.llmPrompt.trim()) {
      return;
    }

    this.loading = true;
    this.api.testLlm(this.llmPrompt).subscribe({
      next: (res: { model: string; output: string }) => {
        this.llmOutput = res.output;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }
}
