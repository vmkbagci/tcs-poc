import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

/**
 * ErrorMessageComponent
 * 
 * Displays error messages with optional retry action.
 * Used throughout the app for error handling and user feedback.
 * 
 * Requirements: 6.5 - Handle API errors gracefully with user-friendly messages
 */
@Component({
  selector: 'app-error-message',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatButtonModule],
  template: `
    @if (message) {
      <div class="error-message-container" [class.inline]="inline">
        <div class="error-content">
          <mat-icon class="error-icon">error</mat-icon>
          <div class="error-text">
            <p class="error-title">{{ title || 'Error' }}</p>
            <p class="error-details">{{ message }}</p>
          </div>
        </div>
        @if (showRetry) {
          <button mat-button color="primary" (click)="onRetry()">
            <mat-icon>refresh</mat-icon>
            Retry
          </button>
        }
        @if (dismissible) {
          <button mat-icon-button (click)="onDismiss()" class="dismiss-button">
            <mat-icon>close</mat-icon>
          </button>
        }
      </div>
    }
  `,
  styles: [`
    .error-message-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px;
      background-color: #ffebee;
      border-left: 4px solid #f44336;
      border-radius: 4px;
      margin: 16px 0;
    }

    .error-message-container.inline {
      margin: 8px 0;
      padding: 12px;
    }

    .error-content {
      display: flex;
      align-items: flex-start;
      flex: 1;
    }

    .error-icon {
      color: #f44336;
      margin-right: 12px;
      flex-shrink: 0;
    }

    .error-text {
      flex: 1;
    }

    .error-title {
      margin: 0 0 4px 0;
      font-weight: 500;
      font-size: 14px;
      color: #c62828;
    }

    .error-details {
      margin: 0;
      font-size: 14px;
      color: rgba(0, 0, 0, 0.87);
    }

    .dismiss-button {
      margin-left: 8px;
    }
  `]
})
export class ErrorMessageComponent {
  @Input() message?: string;
  @Input() title?: string;
  @Input() showRetry: boolean = false;
  @Input() dismissible: boolean = false;
  @Input() inline: boolean = false;
  
  @Output() retry = new EventEmitter<void>();
  @Output() dismiss = new EventEmitter<void>();

  onRetry(): void {
    this.retry.emit();
  }

  onDismiss(): void {
    this.dismiss.emit();
  }
}
