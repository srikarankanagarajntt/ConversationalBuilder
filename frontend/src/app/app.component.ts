import { Component, OnInit, SecurityContext } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { DomSanitizer } from '@angular/platform-browser';

import { ConversationResponse, CvApiService, SessionResponse, TemplateOption, PersonalInfo } from './services/cv-api.service';
import { environment } from '../environments/environment';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface TemplateWithPreview extends TemplateOption {
  previewImageUrl?: string;
  isLoading?: boolean;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements OnInit {
  userId = 'user-' + Math.random().toString(36).substr(2, 9);
  sessionId = '';
  message = '';
  llmPrompt = 'Im a software engineer with 5 years of experience in web development. Summarize my profile for a CV.';

  conversationHistory: Message[] = [];
  assistantReply = '';
  transcript = '';
  llmOutput = '';
  errorMessage = '';
  missingFields: string[] = [];
  loading = false;
  recording = false;
  sidebarOpen = false;
  showSummaryForm = false;
  showCvPreview = false;
  showTemplateModal = false;
  showPersonalInfoModal = false;
  showExportModal = false;
  pendingExportFormat: 'pdf' | 'docx' | 'pptx' | 'json' | null = null;
  cvData: any = null;
  templates: TemplateWithPreview[] = [];
  selectedTemplateId: string | null = null;

  // Personal info form fields
  personalFullName = '';
  personalEmail = '';
  personalPhone = '';
  personalLocation = '';
  personalSummary = '';
  personalSkills: string[] = [];
  personalSkillsInput = '';
  
  // Form validation errors
  formErrors: { [key: string]: string } = {
    fullName: '',
    email: '',
    phone: '',
    location: '',
    summary: '',
    skills: '',
  };

  // Toast notification
  toastMessage = '';
  toastType: 'success' | 'error' | 'info' = 'info';
  showToast = false;
  private toastTimeout: any = null;

  // Track file download completion
  hasDownloadedFile = false;

  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(private readonly api: CvApiService, private readonly http: HttpClient, private readonly sanitizer: DomSanitizer) {}

  ngOnInit(): void {
    this.createSessionOnLoad();
  }

  hasAssistantMessages(): boolean {
    return this.conversationHistory.some(m => m.role === 'assistant');
  }

  private createSessionOnLoad(): void {
    this.loading = true;
    this.errorMessage = '';
    this.api.createSession(this.userId).subscribe({
      next: (res: SessionResponse) => {
        this.sessionId = res.sessionId;
        this.loading = false;
        // Add an initial greeting to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: "Hello! I'm your AI CV Assistant. Let's build your professional CV together. Upload a resume or say Hi to continue!",
          timestamp: new Date(),
        });
      },
      error: () => {
        this.errorMessage = 'Failed to create session. Please refresh the page.';
        this.loading = false;
      },
    });
  }

  sendMessage(): void {
    const userMessage = this.message.trim();
    this.message = ''; // Clear input immediately for better UX
    if (!this.sessionId || !userMessage.trim()) {
      return;
    }

    // Add user message to conversation
    this.conversationHistory.push({
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
    });

    this.loading = true;
    this.errorMessage = '';
    this.api.sendMessage(this.sessionId, userMessage).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        // Add assistant reply to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });
        this.transcript = '';
        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
       // this.message = '';
        
        // Show personal info modal if indicated
        if (res.showPersonalInfoModal) {
          this.showPersonalInfoModal = true;
        }
        
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
        
        // Add voice message and reply to conversation
        this.conversationHistory.push({
          role: 'user',
          content: this.transcript,
          timestamp: new Date(),
        });
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });

        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
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

  toggleSummaryForm(): void {
    this.showSummaryForm = !this.showSummaryForm;
    this.llmOutput = '';
  }

  formatFieldName(field: string): string {
    // Convert "personalInfo.fullName" to "Full Name"
    // Remove the prefix (personalInfo., experience., etc.)
    const fieldName = field.split('.').pop() || field;
    
    // Convert camelCase to Title Case
    return fieldName
      .replace(/([A-Z])/g, ' $1') // Insert space before capitals
      .replace(/^./, (c) => c.toUpperCase()) // Capitalize first letter
      .trim();
  }

  playAssistantReply(): void {
    if (!this.assistantReply.trim()) {
      this.errorMessage = 'No assistant message to play.';
      return;
    }
  }

  exportCv(format: 'pdf' | 'docx' | 'pptx' | 'json'): void {
    if (!this.sessionId) {
      this.errorMessage = 'No active session to export.';
      return;
    }

    if (!this.cvData) {
      this.errorMessage = 'No CV data to export. Continue the conversation to gather information.';
      return;
    }

    // Trigger actual download
    this.loading = true;
    this.errorMessage = '';
    this.api.exportCv(this.sessionId, format).subscribe({
      next: (res: { jobId: string; downloadUrl: string }) => {
        this.downloadFile(res.downloadUrl, format);
        this.closeExportModal();
        this.loading = false;
        this.hasDownloadedFile = true;
      },
      error: () => {
        this.errorMessage = `Failed to export CV as ${format.toUpperCase()}.`;
        this.loading = false;
      },
    });
  }

  downloadCv(): void {
    if (!this.sessionId) {
      this.errorMessage = 'No active session to export.';
      return;
    }

    // Open export modal
    this.showExportModal = true;
    this.errorMessage = '';
  }

  closeCvPreview(): void {
    this.showCvPreview = false;
    this.pendingExportFormat = null;
    this.errorMessage = '';
  }

  private downloadFile(downloadUrl: string, format: string): void {
    // Extract file ID from the download URL (e.g., /api/download/file-id)
    const fileId = downloadUrl.split('/').pop();
    if (!fileId) {
      this.errorMessage = 'Invalid download URL.';
      return;
    }

    this.api.downloadFile(fileId).subscribe({
      next: (response: any) => {
        // Extract filename from Content-Disposition header
        // Supports formats:
        //   - attachment; filename="John_cv.pdf" (RFC 5987 - quoted)
        //   - attachment; filename=John_cv.pdf (unquoted)
        //   - attachment; filename*=UTF-8''John_cv.pdf (RFC 5987 - encoded)
        let filename = `resume.${format}`; // fallback filename
        
        const contentDisposition = response.headers.get('content-disposition');
        if (contentDisposition) {
          // Try RFC 5987 encoded filename first (filename*=)
          let matches = contentDisposition.match(/filename\*=(?:UTF-8'')?([^;]+)/i);
          if (matches && matches[1]) {
            // Decode URL-encoded filename
            filename = decodeURIComponent(matches[1]).trim();
          } else {
            // Try standard filename= (quoted or unquoted)
            matches = contentDisposition.match(/filename=(?:"([^"]*)"|([^;,\s]*))/i);
            if (matches && (matches[1] || matches[2])) {
              filename = (matches[1] || matches[2]).trim();
            }
          }
        }
        
        const blob = response.body;
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.errorMessage = `Failed to download ${format.toUpperCase()} file.`;
      },
    });
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  onFileUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;

    if (!files || files.length === 0) {
      return;
    }

    const file = files[0];
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      this.errorMessage = 'Invalid file type. Please upload PDF, DOCX, or TXT file.';
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      this.errorMessage = 'File size exceeds 10MB limit.';
      return;
    }

    this.uploadFile(file);
    
    // Reset input
    input.value = '';
  }

  private uploadFile(file: File): void {
    if (!this.sessionId) {
      this.errorMessage = 'Please start a new chat session first.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    this.api.uploadCv(file, this.sessionId).subscribe({
      next: (response: any) => {
        console.log('Upload response received:', response);
        
        // Show success toast message
        this.showToastNotification('✅ Resume uploaded successfully!', 'success');

        // Update CV data if available
        if (response.extracted_data) {
          const header = response.extracted_data.header || {};
          const skills = response.extracted_data.technicalSkills || {};
          const workExperienceList = response.extracted_data.workExperience || [];
          const experienceList = response.extracted_data.experience || [];
          
          // Map workExperience to consolidated experience format
          const mappedExperience = workExperienceList.map((exp: any) => ({
            company: exp.employer || '',
            title: exp.position || '',
            role: exp.position || '',
            startDate: exp.startDate || '',
            endDate: exp.endDate || '',
            location: exp.location || '',
            clients: exp.clients || '',
            projectName: exp.projectName || '',
            projectInformation: exp.projectInformation || '',
            technology: exp.technology || [],
            description: exp.projectDescription || '',
            achievements: exp.achievements || [],
          }));

          // Also include experience entries if they exist
          const allExperience = experienceList.length > 0 ? experienceList : mappedExperience;
          
          this.cvData = { 
            ...response.extracted_data,
            personalInfo: {
              fullName: header.fullName || '',
              email: header.email || '',
              phone: header.phone || '',
              location: header.location || '',
              role: header.jobTitle || '',
              summary: Array.isArray(response.extracted_data.professionalSummary)
                ? response.extracted_data.professionalSummary.join('\n')
                : (response.extracted_data.professionalSummary || ''),
            },
            skills: this.extractSkillsFromTechnical(skills),
            experience: allExperience,
            // Ensure certifications are included
            certifications: response.extracted_data.certifications || [],
            header: header,
          };
        }

        // Always send the upload response to conversation service immediately
        console.log('Sending to conversation service...');
        this.sendUploadResponseToConversation(response);
      },
      error: (error) => {
        this.loading = false;
        const errorMsg = error.error?.detail || error.error?.message || 'Failed to upload resume. Please try again.';
        this.errorMessage = `Upload failed: ${errorMsg}`;
        
        console.error('Upload error:', error);
        
        // Show error toast message
        this.showToastNotification(`❌ ${errorMsg}`, 'error');
        
        this.conversationHistory.push({
          role: 'assistant',
          content: `❌ ${errorMsg}`,
          timestamp: new Date(),
        });
        
        this.scrollToBottom();
      },
    });
  }

  private sendUploadResponseToConversation(uploadResponse: any): void {
    console.log('sendUploadResponseToConversation called with:', uploadResponse);
    
    // Add user message to conversation history
    const extractedData = uploadResponse.extracted_data || uploadResponse;
    this.conversationHistory.push({
      role: 'user',
      content: `📄 Resume uploaded\n\n${this.formatCvDataAsMessage(extractedData)}`,
      timestamp: new Date(),
    });

    // Send the full upload response to conversation endpoint for LLM processing
    const messageContent = JSON.stringify(uploadResponse);
    console.log('Calling sendMessage with:', messageContent.substring(0, 100) + '...');
    
    this.api.sendMessage(this.sessionId, messageContent).subscribe({
      next: (res: ConversationResponse) => {
        console.log('Conversation message response:', res);
        
        // Add LLM response to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: res.reply,
          timestamp: new Date(),
        });

        this.transcript = '';
        this.missingFields = res.missingFields;
        this.message = '';
        this.loading = false;

        // Update CV data from response (enables preview button)
        this.cvData = (res as any).cvDraft || null;

        // Show personal info modal if indicated
        if (res.showPersonalInfoModal) {
          this.showPersonalInfoModal = true;
        }

        this.scrollToBottom();
      },
      error: (error) => {
        console.error('Conversation message error:', error);
        this.loading = false;
        const errorMsg = error.error?.detail || error.error?.message || 'Failed to process resume.';
        this.errorMessage = `Processing failed: ${errorMsg}`;
        
        this.conversationHistory.push({
          role: 'assistant',
          content: `❌ ${errorMsg}`,
          timestamp: new Date(),
        });
        
        this.scrollToBottom();
      },
    });
  }

  private sendExtractedCvToConversation(extractedData: any): void {
    // Format extracted CV data as a structured message for the LLM
    const cvMessage = this.formatCvDataAsMessage(extractedData);

    // Add user message to conversation history
    this.conversationHistory.push({
      role: 'user',
      content: `📄 Resume uploaded\n\n${cvMessage}`,
      timestamp: new Date(),
    });

    // Send to conversation endpoint for LLM processing
    this.api.sendMessage(this.sessionId, cvMessage).subscribe({
      next: (res: ConversationResponse) => {
        // Add LLM response to conversation
        this.conversationHistory.push({
          role: 'assistant',
          content: res.reply,
          timestamp: new Date(),
        });

        this.transcript = '';
        this.missingFields = res.missingFields;
        this.message = '';
        this.loading = false;

        // Show personal info modal if indicated
        if (res.showPersonalInfoModal) {
          this.showPersonalInfoModal = true;
        }

        this.scrollToBottom();
      },
      error: (error) => {
        this.loading = false;
        const errorMsg = error.error?.detail || error.error?.message || 'Failed to process resume.';
        this.errorMessage = `Processing failed: ${errorMsg}`;
        
        this.conversationHistory.push({
          role: 'assistant',
          content: `❌ ${errorMsg}`,
          timestamp: new Date(),
        });
        
        this.scrollToBottom();
      },
    });
  }

  private formatCvDataAsMessage(data: any): string {
    const lines: string[] = [];

    // Header (personal info)
    const header = data.header || {};
    if (header.fullName || header.email) {
      lines.push('**Extracted Resume Information:**');
      lines.push('');
      if (header.fullName) lines.push(`**Name:** ${header.fullName}`);
      if (header.jobTitle) lines.push(`**Current Title:** ${header.jobTitle}`);
      if (header.email) lines.push(`**Email:** ${header.email}`);
      if (header.phone) lines.push(`**Phone:** ${header.phone}`);
      if (header.location) lines.push(`**Location:** ${header.location}`);
      lines.push('');
    }

    // Professional summary
    const summary = data.professionalSummary || [];
    if (Array.isArray(summary) && summary.length > 0) {
      lines.push('**Professional Summary:**');
      summary.forEach((s: string) => lines.push(`• ${s}`));
      lines.push('');
    }

    // Technical skills
    const skills = data.technicalSkills || {};
    const primarySkills = skills.primary || [];
    if (primarySkills.length > 0) {
      lines.push('**Primary Skills:** ' + primarySkills.map((s: any) => s.skill_name || s).join(', '));
    }
    const secondarySkills = skills.secondary || [];
    if (secondarySkills.length > 0) {
      lines.push('**Secondary Skills:** ' + secondarySkills.map((s: any) => s.skill_name || s).join(', '));
      lines.push('');
    }

    // Work experience
    const experience = data.workExperience || [];
    if (experience.length > 0) {
      lines.push('**Work Experience:**');
      experience.forEach((exp: any, index: number) => {
        lines.push(`${index + 1}. **${exp.position}** at ${exp.employer} (${exp.duration || 'N/A'})`);
        if (exp.project_description) {
          lines.push(`   ${exp.project_description}`);
        }
      });
    }

    return lines.join('\n');
  }

  private extractSkillsFromTechnical(technicalSkills: any): string[] {
    const skills: string[] = [];
    
    if (technicalSkills.primary) {
      technicalSkills.primary.forEach((skill: any) => {
        if (typeof skill === 'string') {
          skills.push(skill);
        } else if (skill.skill_name) {
          skills.push(skill.skill_name);
        }
      });
    }
    
    if (technicalSkills.secondary) {
      technicalSkills.secondary.forEach((skill: any) => {
        if (typeof skill === 'string') {
          skills.push(skill);
        } else if (skill.skill_name) {
          skills.push(skill.skill_name);
        }
      });
    }
    
    return skills;
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.chat-main');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }

  private showToastNotification(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.toastMessage = message;
    this.toastType = type;
    this.showToast = true;

    // Clear any existing timeout
    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
    }

    // Auto-hide toast after 4 seconds
    this.toastTimeout = setTimeout(() => {
      this.showToast = false;
      this.toastTimeout = null;
    }, 4000);
  }

  closeToast(): void {
    this.showToast = false;
    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
      this.toastTimeout = null;
    }
  }


  showTemplateSelector(): void {
    if (!this.sessionId) {
      this.errorMessage = 'Create a session before selecting a template.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.getTemplates().subscribe({
      next: (res: any) => {
        this.templates = res.templates;
        // Generate previews for all templates
        this.generateTemplatePreview();
        this.showTemplateModal = true;
        this.selectedTemplateId = null;
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to load templates.';
        this.loading = false;
      },
    });
  }

  private generateTemplatePreview(): void {
    this.templates.forEach((template: TemplateWithPreview) => {
      template.isLoading = true;
      
      // First check if backend provided a preview image
      if (template.previewImageUrl) {
        template.isLoading = false;
        return;
      }
      
      if (template.previewImageBase64) {
        try {
          template.previewImageUrl = `data:image/png;base64,${template.previewImageBase64}`;
          template.isLoading = false;
          return;
        } catch (error) {
          console.error('Error processing preview image:', error);
        }
      }
      
      // Fallback: Generate preview from template file
      if (template.fileBase64) {
        try {
          const byteCharacters = atob(template.fileBase64);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: this.getMimeType(template.fileType) });

          // Generate preview based on file type
          if (template.fileType === 'docx') {
            this.generateDocxPreview(blob, template);
          } else if (template.fileType === 'pptx') {
            this.generatePptxPreview(blob, template);
          } else {
            this.setDefaultPreview(template);
          }
        } catch (error) {
          console.error('Error generating preview:', error);
          this.setDefaultPreview(template);
        }
      } else {
        this.setDefaultPreview(template);
      }
    });
  }

  private getMimeType(fileType: string): string {
    const mimeTypes: { [key: string]: string } = {
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    };
    return mimeTypes[fileType] || 'application/octet-stream';
  }

  private generateDocxPreview(blob: Blob, template: TemplateWithPreview): void {
    // Use a temporary div to render the docx preview
    const tempDiv = document.createElement('div');
    tempDiv.style.width = '100%';
    tempDiv.style.height = '300px';
    tempDiv.style.overflow = 'hidden';

    // Import docx-preview dynamically
    import('docx-preview').then((module) => {
      module.renderAsync(blob, tempDiv).then(() => {
        // Convert the rendered content to a canvas and then to an image
        this.convertDivToImage(tempDiv, template);
      }).catch((error: any) => {
        console.error('Error rendering docx:', error);
        this.setDefaultPreview(template);
      });
    }).catch(() => {
      this.setDefaultPreview(template);
    });
  }

  private convertDivToImage(element: HTMLElement, template: TemplateWithPreview): void {
    try {
      // Use html2canvas if available, otherwise use a canvas approach
      const canvas = document.createElement('canvas');
      canvas.width = 280;
      canvas.height = 300;
      const ctx = canvas.getContext('2d');
      
      if (ctx) {
        // Create a gradient background to simulate document preview
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, '#f5f5f5');
        gradient.addColorStop(1, '#e8e8e8');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 280, 300);

        // Add border
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1;
        ctx.strokeRect(0, 0, 280, 300);

        // Add text
        ctx.fillStyle = '#333';
        ctx.font = 'bold 14px Arial';
        ctx.fillText('DOCX Preview', 10, 30);
        ctx.font = '12px Arial';
        ctx.fillText(template.templateName, 10, 50);
        
        template.previewImageUrl = canvas.toDataURL('image/png');
      }
      template.isLoading = false;
    } catch (error) {
      console.error('Error converting to image:', error);
      this.setDefaultPreview(template);
    }
  }

  private generatePptxPreview(blob: Blob, template: TemplateWithPreview): void {
    // For PPTX, create a simple preview since we need a library to properly extract slides
    const canvas = document.createElement('canvas');
    canvas.width = 280;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      // Create a gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, '#e8f5e9');
      gradient.addColorStop(1, '#c8e6c9');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 280, 300);

      // Add border
      ctx.strokeStyle = '#66bb6a';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, 280, 300);

      // Add presentation icon and text
      ctx.fillStyle = '#333';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('PPTX Preview', 10, 30);
      ctx.font = '12px Arial';
      ctx.fillText(template.templateName, 10, 50);
      ctx.fillText('Presentation File', 10, 80);
      
      // Draw slides indicator
      ctx.fillStyle = '#fff';
      ctx.fillRect(10, 100, 120, 80);
      ctx.fillRect(150, 100, 120, 80);
      
      ctx.fillStyle = '#66bb6a';
      ctx.font = '10px Arial';
      ctx.fillText('Slide 1', 50, 145);
      ctx.fillText('Slide 2', 190, 145);

      template.previewImageUrl = canvas.toDataURL('image/png');
    }
    template.isLoading = false;
  }

  private setDefaultPreview(template: TemplateWithPreview): void {
    // Create a default preview canvas
    const canvas = document.createElement('canvas');
    canvas.width = 280;
    canvas.height = 300;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
      const gradient = ctx.createLinearGradient(0, 0, 0, 300);
      gradient.addColorStop(0, '#f0f0f0');
      gradient.addColorStop(1, '#d9d9d9');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 280, 300);

      ctx.strokeStyle = '#999';
      ctx.lineWidth = 1;
      ctx.strokeRect(0, 0, 280, 300);

      ctx.fillStyle = '#666';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('Template Preview', 10, 30);
      ctx.font = '12px Arial';
      ctx.fillText(template.templateName, 10, 50);
      ctx.fillText(template.fileType.toUpperCase(), 10, 70);

      template.previewImageUrl = canvas.toDataURL('image/png');
    }
    template.isLoading = false;
  }

  selectTemplateFromPreview(): void {
    // Open template modal from preview
    this.showTemplateModal = true;
  }

  selectTemplate(): void {
    if (!this.sessionId || !this.selectedTemplateId) {
      this.errorMessage = 'Please select a template first.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.selectTemplate(this.sessionId, this.selectedTemplateId).subscribe({
      next: () => {
        this.showTemplateModal = false;
        this.showCvPreview = false; // Close preview modal when template is selected
        this.errorMessage = '';
        this.loading = false;
        this.conversationHistory.push({
          role: 'assistant',
          content: `Template "${this.selectedTemplateId}" has been selected for your CV.`,
          timestamp: new Date(),
        });
      },
      error: () => {
        this.errorMessage = 'Failed to select template.';
        this.loading = false;
      },
    });
  }

  closeTemplateModal(): void {
    this.showTemplateModal = false;
    this.selectedTemplateId = null;
    this.errorMessage = '';
  }

  openExportModal(): void {
    this.showExportModal = true;
  }

  closeExportModal(): void {
    this.showExportModal = false;
  }

  addSkill(): void {
    if (this.personalSkillsInput.trim()) {
      this.personalSkills.push(this.personalSkillsInput.trim());
      this.personalSkillsInput = '';
    }
  }

  removeSkill(index: number): void {
    this.personalSkills.splice(index, 1);
  }

  submitPersonalInfo(): void {
    // Clear previous errors
    this.formErrors = { fullName: '', email: '', phone: '', location: '', summary: '', skills: '' };
    
    // Validate form
    let isValid = true;
    
    if (!this.personalFullName.trim()) {
      this.formErrors.fullName = 'Full name is required';
      isValid = false;
    }
    
    if (!this.personalEmail.trim()) {
      this.formErrors.email = 'Email is required';
      isValid = false;
    } else if (!this.isValidEmail(this.personalEmail)) {
      this.formErrors.email = 'Please enter a valid email address';
      isValid = false;
    }

    if (!this.personalPhone.trim()) {
      this.formErrors.phone = 'Phone number is required';
      isValid = false;
    }

    if (!this.personalLocation.trim()) {
      this.formErrors.location = 'Location is required';
      isValid = false;
    }

    if (!this.personalSummary.trim()) {
      this.formErrors.summary = 'Professional summary is required';
      isValid = false;
    }

    if (this.personalSkills.length === 0) {
      this.formErrors.skills = 'At least one skill is required';
      isValid = false;
    }
    
    if (!isValid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.api.submitPersonalInfo(
      this.sessionId,
      this.personalFullName,
      this.personalEmail,
      this.personalPhone,
      this.personalLocation,
      this.personalSummary,
      this.personalSkills
    ).subscribe({
      next: (res: ConversationResponse) => {
        this.assistantReply = res.reply;
        this.conversationHistory.push({
          role: 'assistant',
          content: this.assistantReply,
          timestamp: new Date(),
        });
        this.missingFields = res.missingFields;
        this.cvData = (res as any).cvDraft || null;
        this.showPersonalInfoModal = false;
        
        // Clear form
        this.personalFullName = '';
        this.personalEmail = '';
        this.personalPhone = '';
        this.personalLocation = '';
        this.personalSummary = '';
        this.personalSkills = [];
        this.personalSkillsInput = '';
        this.formErrors = { fullName: '', email: '', phone: '', location: '', summary: '', skills: '' };
        
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Failed to save personal information.';
        this.loading = false;
      },
    });
  }

  validateEmail(): void {
    if (!this.personalEmail.trim()) {
      this.formErrors.email = 'Email is required';
    } else if (!this.isValidEmail(this.personalEmail)) {
      this.formErrors.email = 'Please enter a valid email address';
    } else {
      this.formErrors.email = '';
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  closePersonalInfoModal(): void {
    this.showPersonalInfoModal = false;
    this.errorMessage = '';
  }

  createNewSession(): void {
    this.sessionId = '';
    this.message = '';
    this.conversationHistory = [];
    this.transcript = '';
    this.assistantReply = '';
    this.errorMessage = '';
    this.cvData = null;
    this.sidebarOpen = false;
    this.selectedTemplateId = null;
    this.hasDownloadedFile = false;
    this.createSessionOnLoad();
  }

  isPersonalInfoFormValid(): boolean {
    return (
      this.personalFullName?.trim() !== '' &&
      this.personalEmail?.trim() !== '' &&
      this.isValidEmail(this.personalEmail) &&
      this.personalPhone?.trim() !== '' &&
      this.personalLocation?.trim() !== '' &&
      this.personalSummary?.trim() !== '' &&
      this.personalSkills?.length > 0
    );
  }

  // Progress Bar Methods
  showWorkflowProgress = true;
  showFieldsProgress = true;

  toggleProgressBar(type: string): void {
    if (type === 'workflow') {
      this.showWorkflowProgress = !this.showWorkflowProgress;
    } else if (type === 'fields') {
      this.showFieldsProgress = !this.showFieldsProgress;
    }
  }

  isWorkflowStageCompleted(stage: string): boolean {
    if (!this.cvData) return stage === 'upload' && this.sessionId !== '';
    
    switch (stage) {
      case 'upload': // Chat & Upload
        return this.sessionId !== '';
      case 'edit': // Edit
        return this.cvData?.personalInfo?.fullName !== '' && this.cvData?.personalInfo?.fullName !== undefined;
      case 'preview': // Preview
        return this.cvData?.experience?.length > 0 && this.getFieldsProgress() >= 100;
      case 'template': // Template
        return this.selectedTemplateId !== null;
      case 'download': // Download - only complete after file is downloaded
        return this.hasDownloadedFile;
      default:
        return false;
    }
  }

  getWorkflowProgress(): number {
    let completed = 0;
    const stages = ['upload', 'edit', 'preview', 'template', 'download'];
    for (const stage of stages) {
      if (this.isWorkflowStageCompleted(stage)) {
        completed++;
      }
    }
    return Math.round((completed / stages.length) * 100);
  }

  isFieldCompleted(field: string): boolean {
    if (!this.cvData) return false;

    switch (field) {
      case 'personalInfo':
        return (
          this.cvData.personalInfo?.fullName?.trim() !== '' &&
          this.cvData.personalInfo?.email?.trim() !== '' &&
          this.cvData.personalInfo?.phone?.trim() !== ''
        );
      case 'skills':
        return this.cvData.technicalSkills && Object.keys(this.cvData.technicalSkills).length > 0;
      case 'experience':
        return Array.isArray(this.cvData.experience) && this.cvData.experience.length > 0;
      case 'projects':
        return Array.isArray(this.cvData.projects) && this.cvData.projects.length > 0;
      case 'education':
        return Array.isArray(this.cvData.education) && this.cvData.education.length > 0;
      case 'certifications':
        return Array.isArray(this.cvData.certifications) && this.cvData.certifications.length > 0;
      default:
        return false;
    }
  }

  getFieldsProgress(): number {
    let completed = 0;
    const fields = ['personalInfo', 'skills', 'experience', 'education', 'certifications'];
    
    for (const field of fields) {
      if (this.isFieldCompleted(field)) {
        completed++;
      }
    }
    
    return Math.round((completed / fields.length) * 100);
  }

  onLanguageChange(event: any): void {
    console.log('Language changed to:', event.target.value);
  }
}
