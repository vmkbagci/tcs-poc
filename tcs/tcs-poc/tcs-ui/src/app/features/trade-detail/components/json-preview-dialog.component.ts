/**
 * JSON Preview Dialog Component
 * 
 * Displays trade data in JSON format with collapsible tree view and copy functionality.
 */

import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { NgxJsonViewerModule } from 'ngx-json-viewer';

export interface JsonPreviewDialogData {
  title: string;
  jsonData: any;
}

@Component({
  selector: 'app-json-preview-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    MatButtonToggleModule,
    NgxJsonViewerModule
  ],
  template: `
    <h2 mat-dialog-title>
      <mat-icon>code</mat-icon>
      {{ data.title }}
    </h2>
    
    <div class="view-toggle">
      <mat-button-toggle-group [value]="viewMode()" (change)="onViewModeChange($event.value)">
        <mat-button-toggle value="tree">
          <mat-icon>account_tree</mat-icon>
          Tree View
        </mat-button-toggle>
        <mat-button-toggle value="raw">
          <mat-icon>code</mat-icon>
          Raw JSON
        </mat-button-toggle>
      </mat-button-toggle-group>
    </div>
    
    <mat-dialog-content>
      @if (viewMode() === 'tree') {
        <div class="json-tree-container">
          <ngx-json-viewer 
            [json]="data.jsonData" 
            [expanded]="false">
          </ngx-json-viewer>
        </div>
      } @else {
        <div class="json-container">
          <pre class="json-content">{{ formattedJson }}</pre>
        </div>
      }
    </mat-dialog-content>
    
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCopy()">
        <mat-icon>content_copy</mat-icon>
        Copy to Clipboard
      </button>
      <button mat-raised-button color="primary" [mat-dialog-close]="true">
        Close
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    h2 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      padding: 16px 24px;
      background-color: #e3f2fd;
      color: #1976d2;

      mat-icon {
        color: #1976d2;
      }
    }

    .view-toggle {
      padding: 12px 24px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.12);
      background-color: #f5f5f5;

      mat-button-toggle-group {
        mat-icon {
          margin-right: 4px;
          font-size: 18px;
          width: 18px;
          height: 18px;
        }
      }
    }

    mat-dialog-content {
      padding: 0;
      margin: 0;
      max-height: 65vh;
      overflow: hidden;
    }

    .json-tree-container {
      max-height: 65vh;
      overflow: auto;
      padding: 24px;
      background-color: #fafafa;

      ::ng-deep {
        .ngx-json-viewer {
          font-family: 'Courier New', Courier, monospace;
          font-size: 13px;
          line-height: 1.6;

          .segment {
            padding: 2px 0;
          }

          .segment-key {
            color: #1976d2;
            font-weight: 500;
          }

          .segment-value {
            color: #424242;
          }

          .segment-type-string {
            color: #2e7d32;
          }

          .segment-type-number {
            color: #d84315;
          }

          .segment-type-boolean {
            color: #6a1b9a;
          }

          .segment-type-null {
            color: #757575;
          }

          .toggler {
            color: #1976d2;
            cursor: pointer;
            user-select: none;
            
            &:hover {
              color: #0d47a1;
            }
          }
        }
      }
    }

    .json-container {
      max-height: 65vh;
      overflow: auto;
      background-color: #263238;
    }

    .json-content {
      margin: 0;
      padding: 24px;
      color: #aed581;
      font-family: 'Courier New', Courier, monospace;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    mat-dialog-actions {
      padding: 16px 24px;
      margin: 0;
      border-top: 1px solid rgba(0, 0, 0, 0.12);

      button {
        mat-icon {
          margin-right: 4px;
        }
      }
    }
  `]
})
export class JsonPreviewDialogComponent {
  data = inject<JsonPreviewDialogData>(MAT_DIALOG_DATA);
  dialogRef = inject(MatDialogRef<JsonPreviewDialogComponent>);
  snackBar = inject(MatSnackBar);

  /**
   * Current view mode (tree or raw)
   */
  viewMode = signal<'tree' | 'raw'>('tree');

  /**
   * Formatted JSON string
   */
  get formattedJson(): string {
    return JSON.stringify(this.data.jsonData, null, 2);
  }

  /**
   * Handle view mode change
   */
  onViewModeChange(mode: 'tree' | 'raw'): void {
    this.viewMode.set(mode);
  }

  /**
   * Copy JSON to clipboard
   */
  onCopy(): void {
    navigator.clipboard.writeText(this.formattedJson).then(
      () => {
        this.snackBar.open('JSON copied to clipboard', 'Close', {
          duration: 2000
        });
      },
      (err) => {
        console.error('Failed to copy:', err);
        this.snackBar.open('Failed to copy to clipboard', 'Close', {
          duration: 3000
        });
      }
    );
  }
}
