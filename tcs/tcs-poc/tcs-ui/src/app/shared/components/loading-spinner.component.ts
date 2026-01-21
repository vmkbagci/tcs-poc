import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

/**
 * LoadingSpinnerComponent
 * 
 * Displays a Material spinner with optional message.
 * Used throughout the app to indicate loading states.
 * 
 * Requirements: 6.4 - Show loading indicators during API calls
 */
@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="loading-spinner-container" [class.overlay]="overlay">
      <mat-spinner [diameter]="diameter" [color]="color"></mat-spinner>
      @if (message) {
        <p class="loading-message">{{ message }}</p>
      }
    </div>
  `,
  styles: [`
    .loading-spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .loading-spinner-container.overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(255, 255, 255, 0.8);
      z-index: 9999;
    }

    .loading-message {
      margin-top: 16px;
      font-size: 14px;
      color: rgba(0, 0, 0, 0.6);
    }
  `]
})
export class LoadingSpinnerComponent {
  @Input() message?: string;
  @Input() diameter: number = 50;
  @Input() color: 'primary' | 'accent' | 'warn' = 'primary';
  @Input() overlay: boolean = false;
}
